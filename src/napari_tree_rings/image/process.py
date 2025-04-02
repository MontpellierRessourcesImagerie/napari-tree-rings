import os
import appdirs
import json
import tifffile as tiff
import numpy as np
import datetime
from pathlib import Path
from pandas import DataFrame
from typing import Iterable
from urllib.request import urlretrieve
from napari.layers import Image, Layer
from napari_tree_rings.image.fiji import SegmentTrunk
from napari_tree_rings.image.file_util import TiffFileTags
from napari_tree_rings.image.measure import MeasureShape


class Segmenter(object):
    """Abstract superclass of operations segmenting given objects in an image."""


    def __init__(self, layer):
        super().__init__()
        self.layer = layer
        self.tiffFileTags = None
        self.segmentTrunkOp = None
        self.measureTrunkOp = None
        self.measurements = {}


    def run(self):
        """Run the trunk segmenter on the image. Yield between operations to allow to display the progress.
        """
        yield
        self.setPixelSizeAndUnit()
        yield
        self.segment()
        yield
        self.measure()
        yield


    def setPixelSizeAndUnit(self):
        """Read the pixel size and the unit from the tiff-file's metadata and store them in the layer."""
        self.tiffFileTags = TiffFileTags(self.layer.metadata['path'])
        self.tiffFileTags.getPixelSizeAndUnit()
        pixelSize = self.tiffFileTags.pixelSize
        unit = self.tiffFileTags.unit
        self.layer.scale = (pixelSize, pixelSize)
        self.layer.units = (unit, unit)


    def segment(self):
        self.subClassResponsibility()


    def measure(self):
        self.subClassResponsibility()


    def subClassResponsibility(self):
        raise Exception("SubclassResponsibility Exception: A method of an abstract class has been called!")



class TrunkSegmenter(Segmenter):
    """The operation reads the tiff-metadata from the image file, segments the trunk using FIJI, and measures the
    trunk on the resulting shape-layer."""


    def __init__(self, layer):
        """Create a new trunk segmenter on the given image-layer. The image-layer must have the path information
        in its metadata."""
        super().__init__(layer)
        self.shapeLayer = None


    def segment(self):
        """Segment the trunk in FIJI and retrieve the result as a shape-layer. Sets the parent of the shape layer
        to the image layer and copies the parent's path into its own metadata. So that they will be available for
        the measure trunk method."""

        self.segmentTrunkOp = SegmentTrunk(self.layer)
        self.segmentTrunkOp.run()
        py_image = self.segmentTrunkOp.result
        shapeLayer = None
        for _, v in py_image.metadata.items():
            if isinstance(v, Layer):
                shapeLayer = v
            elif isinstance(v, Iterable):
                for itm in v:
                    if isinstance(itm, Layer):
                        shapeLayer = itm
        shapeLayer.scale = self.layer.scale
        shapeLayer.units = self.layer.units
        shapeLayer.metadata['parent'] = self.layer
        shapeLayer.metadata['parent_path'] = self.layer.metadata['path']
        shapeLayer.name = 'trunk of ' + self.layer.name
        self.shapeLayer = shapeLayer


    def measure(self):
        """Measure the features on the shape layer and add them to the operations measurements."""

        self.measureTrunkOp = MeasureShape(self.shapeLayer, "trunk")
        self.measureTrunkOp.do()
        self.measureTrunkOp.addToTable(self.measurements)



class RingsSegmenter(Segmenter):
    """ The operation reads the tiff-metadata from the image file, segments the trunk using an AttentionUNet to predict
    a distance map on which the rings are traced using the A* algorithm, and measures the trunk on the resulting
    labels-layer."""


    def __init__(self, layer):
        super().__init__(layer)
        self.dataFolder = appdirs.user_data_dir("napari-tree-rings")
        self.modelsPath = os.path.join(self.dataFolder, "models")
        self.pithModelsPath = os.path.join(self.modelsPath, "pith")
        self.ringsModelsPath = os.path.join(self.modelsPath, "rings")
        os.makedirs( self.pithModelsPath, exist_ok=True )
        os.makedirs( self.ringsModelsPath, exist_ok=True)
        self.pithModels = []
        self.ringsModels = []
        self.loadPithModels()
        self.loadRingsModels()
        self.options = {'pithModel': self.pithModels[0], 'ringsModel': self.ringsModels[0]}
        self.loadOptions()


    def segment(self):
        image = self.layer.data
        print(image.shape)


    def measure(self):
        pass


    def pithModelsExist(self):
       return self.modelsExists(self.pithModelsPath)


    def ringsModelsExists(self):
        return self.modelsExists(self.ringsModelsPath)


    @classmethod
    def modelsExists(cls, path):
        if not os.path.exists(path):
            return False
        models = [model for model in os.listdir(path) if model.endswith('.keras')]
        return len(models) > 0


    def loadPithModels(self):
        self.pithModels = self.getKerasModelsFromFolder(self.pithModelsPath)
        if len(self.pithModels) == 0:
            self.downloadPithModels()
        self.pithModels = self.getKerasModelsFromFolder(self.pithModelsPath)


    def loadRingsModels(self):
        self.ringsModels = self.getKerasModelsFromFolder(self.ringsModelsPath)
        if len(self.ringsModels) == 0:
            self.downloadRingsModels()
        self.ringsModels = self.getKerasModelsFromFolder(self.ringsModelsPath)


    def getKerasModelsFromFolder(self, folder):
        if not self.modelsExists(folder):
            return []
        models = [model for model in os.listdir(folder) if model.endswith('.keras')]
        return models


    def downloadPithModels(self):
        self.downloadModels('pith')


    def downloadRingsModels(self):
        self.downloadModels('rings')


    def downloadModels(self, typeKey):
        path = os.path.join(str(self.getProjectRoot()), "model_urls.json")
        with open(path) as aFile:
            paths = json.load(aFile)
        model = paths[typeKey]
        for key, url in model.items():
            filename = key + ".keras"
            destPath = os.path.join(self.ringsModelsPath, filename)
            if typeKey == "pith":
                destPath = os.path.join(self.pithModelsPath, filename)
            print(url, destPath)
            outPath, msg = urlretrieve(url, destPath)
            print("downloaded ", outPath, msg)


    @classmethod
    def getProjectRoot(cls):
        """
        Gets the project root directory, assuming this function is called
        from a file within the project, and that there's a 'pyproject.toml'
        file at the project root.
        """
        # Start from THIS file's directory
        current_file = Path(__file__).resolve()  # Using resolve to get an absolute path.
        # Go up directories until we find 'pyproject.toml'
        for parent in current_file.parents:  # Iterate over every parent.
            if (parent / "pyproject.toml").exists():  # Checks if file exists
                return parent
        raise FileNotFoundError("Project root (with pyproject.toml) not found.")


    def loadOptions(self):
        pass


    def saveOptions(self):
        pass


class BatchSegmentTrunk:
    """Run the trunk segmentation on all tiff-images in a given folder and save the control shapes and the
    measurements into an output folder."""

    def __init__(self, sourceFolder, outputFolder):
        self.sourceFolder = sourceFolder
        self.outputFolder = outputFolder
        self.measurements =  {}
        self.segmenter = None


    def run(self):
        """Run the batch trunk segmentation."""

        imageFileNames = os.listdir(self.sourceFolder)
        self.segmenter = None
        if not imageFileNames:
            return
        for imageFilename in imageFileNames:
            path = os.path.join(self.sourceFolder, imageFilename)
            img = tiff.imread(path)
            imageLayer = Image(np.array(img))
            imageLayer.metadata['path'] = path
            imageLayer.name = imageFilename
            imageLayer.metadata['name'] = imageFilename
            self.segmenter = TrunkSegmenter(imageLayer)
            self.segmenter.measurements = self.measurements
            self.segmenter.setPixelSizeAndUnit()
            self.segmenter.segment()
            self.segmenter.measure()
            self.measurements = self.segmenter.measurements
            csvFilename = os.path.splitext(imageFilename)[0] + ".csv"
            path = os.path.join(self.outputFolder, csvFilename)
            self.segmenter.shapeLayer.save(path)
            yield self.measurements
        time = str(datetime.datetime.now())
        tablePath = os.path.join(self.outputFolder, time + "_trunk-measurements.csv")
        df = DataFrame(self.segmenter.measurements)
        df.to_csv(tablePath)
