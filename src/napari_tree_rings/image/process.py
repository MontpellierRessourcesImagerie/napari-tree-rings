import logging
import math
import time
import os
import cv2
import appdirs
import json
import importlib.resources
import tifffile as tiff
import numpy as np
import pandas as pd
from urllib.request import urlretrieve
from skimage import measure
from scipy import ndimage
from napari.layers import Image, Shapes
from napari_tree_rings.image.segmentation import SegmentTrunk
from napari_tree_rings.image.file_util import TiffFileTags
from napari_tree_rings.image.measure import MeasureShape
from tree_ring_analyzer.segmentation import TreeRingSegmentation
import napari_tree_rings.config



class Segmenter(object):
    """Abstract superclass of operations segmenting given objects in an image."""


    def __init__(self, layer):
        super().__init__()
        self.layer = layer
        self.tiffFileTags = None
        self.segmentTrunkOp = None
        self.measureOp = None
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
        self.layer.scale = tuple([pixelSize] * self.layer.ndim)
        self.layer.units = tuple([unit] * self.layer.ndim)


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


    def run(self):
        """Run the trunk segmenter on the image. Yield between operations to allow to display the progress.
        """
        start_time = time.time()
        print("started")
        yield
        print("1. set pixel size and unit")
        self.setPixelSizeAndUnit()
        yield
        print("2. instantiate segment trunk operation")
        self.segmentTrunkOp = SegmentTrunk(self.layer)
        yield
        print("3. convert image")
        self.segmentTrunkOp.options = self.segmentTrunkOp.readOptions()
        image = self.layer.data
        image = self.segmentTrunkOp.convertImage(image)
        shape = (image.shape[0], image.shape[1])
        print("shape: " + str(shape))
        yield
        print("4. scale down")
        image = self.segmentTrunkOp.scaleDownImage(image)
        yield
        print("5. threshold")
        image = self.segmentTrunkOp.meanThresholdImage(image)
        yield
        print("6. keep largest region")
        image = self.segmentTrunkOp.keep_largest_region(image)
        yield
        print("7. fill holes")
        image = self.segmentTrunkOp.fillHolesImage(image)
        yield
        print("8. opening")
        image = self.segmentTrunkOp.morphoOpenImage(image)
        yield
        print("9. scale up")
        image = self.segmentTrunkOp.scaleUpMask(image, shape)
        yield
        print("10. erode")
        image = self.segmentTrunkOp.morphoErodeImage(image)
        yield
        print("11. convex hull")
        image = self.segmentTrunkOp.convexHullImage(image)
        yield
        print("12. create shapes")
        self.segmentTrunkOp.result = self.segmentTrunkOp.createShapes(image)
        yield
        print("13. set metadata")
        shapeLayer = self.segmentTrunkOp.result
        shapeLayer.scale = tuple([self.layer.scale[0]] * shapeLayer.ndim)
        shapeLayer.units = tuple([self.layer.units[0]] * shapeLayer.ndim)
        shapeLayer.metadata['parent'] = self.layer
        shapeLayer.metadata['parent_path'] = self.layer.metadata['path']
        shapeLayer.name = 'trunk of ' + self.layer.name
        self.shapeLayer = shapeLayer
        yield
        print("14. measure", flush=True)
        self.measureOp = MeasureShape(self.shapeLayer, object_type="trunk")
        print("measure do", flush=True)
        self.measureOp.do()
        print("measure add to table", flush=True)
        self.measureOp.addToTable(self.measurements)
        print("finished", flush=True)
        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        print("Elapsed time: ", str(minutes)+":"+str(seconds))
        yield



    def segment(self):
        """Segment the trunk in FIJI and retrieve the result as a shape-layer. Sets the parent of the shape layer
        to the image layer and copies the parent's path into its own metadata. So that they will be available for
        the measure trunk method."""


        self.doSegment()
        shapeLayer = self.segmentTrunkOp.result
        shapeLayer.scale = tuple([self.layer.scale[0]] * shapeLayer.ndim)
        shapeLayer.units = tuple([self.layer.units[0]] * shapeLayer.ndim)
        shapeLayer.metadata['parent'] = self.layer
        shapeLayer.metadata['parent_path'] = self.layer.metadata['path']
        shapeLayer.name = 'trunk of ' + self.layer.name
        self.shapeLayer = shapeLayer


    def doSegment(self):
        self.segmentTrunkOp.options = self.segmentTrunkOp.readOptions()
        image = self.layer.data
        shape = image.shape
        image = self.segmentTrunkOp.convertImage(image)
        yield
        image = self.segmentTrunkOp.scaleDownImage(image)
        yield
        image = self.segmentTrunkOp.meanThresholdImage(image)
        yield
        image = self.segmentTrunkOp.keep_largest_region(image)
        yield
        image = self.segmentTrunkOp.fillHolesImage(image)
        yield
        image = self.segmentTrunkOp.morphoOpenImage(image)
        yield
        image = self.segmentTrunkOp.scaleUpMask(image, shape)
        yield
        image = self.segmentTrunkOp.morphoErodeImage(image)
        yield
        image = self.segmentTrunkOp.convexHullImage(image)
        yield
        self.segmentTrunkOp.result = self.segmentTrunkOp.createShapes(image)
        yield


    def measure(self):
        """Measure the features on the shape layer and add them to the operations measurements."""

        self.measureOp = MeasureShape(self.shapeLayer, object_type="trunk")
        self.measureOp.do()
        self.measureOp.addToTable(self.measurements)



class RingsSegmenter(Segmenter):
    """ The operation reads the tiff-metadata from the image file, segments the trunk using an AttentionUNet to predict
    a distance map on which the rings are traced using the A* algorithm, and measures the trunk on the resulting
    labels-layer."""


    def __init__(self, layer):
        super().__init__(layer)
        self.dataFolder = appdirs.user_data_dir("napari-tree-rings")
        self.optionsPath = os.path.join(self.dataFolder, "rs_options.json")
        self.modelsPath = os.path.join(self.dataFolder, "models")
        self.pithModelsPath = os.path.join(self.modelsPath, "pith")
        self.ringsModelsPath = os.path.join(self.modelsPath, "rings")
        self.inbdModelsPath = os.path.join(self.modelsPath, "inbd")
        os.makedirs( self.pithModelsPath, exist_ok=True )
        os.makedirs( self.ringsModelsPath, exist_ok=True)
        os.makedirs( self.inbdModelsPath, exist_ok=True)
        self.pithModels = self.loadModels(self.pithModelsPath, 'pith')
        self.ringsModels = self.loadModels(self.ringsModelsPath, 'rings')
        self.inbdModels = self.loadModels(self.inbdModelsPath, 'inbd')

        self.options = {'method': 'Attention UNet', 'pithModel': self.pithModels[0], 'ringsModel': self.ringsModels[0], 'patchSize': 256,
                        'overlap': 60, 'batchSize': 8, 'resize': 5, 'lossType': 'H0',
                          'inbdModel': self.inbdModels[0]}
        self.loadOptions()
        self.resultsLayer = None
        self.minRadiusDeltaPithInnerRing = 3

        self.ringsModel = None
        self.pithModel = None
        self.inbdModel = None


    def segment(self):
        self.loadOptions()
        if self.options['method'] == 'Attention UNet':
            import tensorflow as tf
            if self.ringsModel is None:
                self.inbdModel = None
                self.ringsModel = tf.keras.models.load_model(os.path.join(self.ringsModelsPath, self.options['ringsModel']), compile=False)
                self.pithModel = tf.keras.models.load_model(os.path.join(self.pithModelsPath, self.options['pithModel']), compile=False)
                self.channel = self.pithModel.get_config()['layers'][0]['config']['batch_shape'][-1]
            
            image = self.layer.data
            
            if len(image.shape) == 2:
                image = image[:, :, None]
            if self.channel == 1 and image.shape[-1] == 3:
                image = (0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2])[:, :, None]
            segmentation = TreeRingSegmentation()
            segmentation.patchSize = self.options['patchSize']
            segmentation.overlap = self.options['overlap']
            segmentation.batchSize = self.options['batchSize']
            segmentation.lossType = self.options['lossType']
            segmentation.resize = self.options['resize']
            segmentation.segmentImage(self.ringsModel, self.pithModel, image)
            # rings = self.maskToPolygons(segmentation.maskRings)
            # pith = self.maskToPolygons(segmentation.pith)
            # self.removeInnerRing(rings, pith)
            rings = self.ringToPolygons(segmentation.predictedRings)
            
        else:
            import torch
            if self.inbdModel is None:
                self.ringsModel = None
                self.pithModel = None
                importer = torch.package.PackageImporter(os.path.join(self.inbdModelsPath, self.options['inbdModel']))
                self.inbdModel = importer.load_pickle('model', 'model.pkl').eval().requires_grad_(False)
                if torch.cuda.is_available():
                    self.inbdModel.cuda()

            output = self.inbdModel.process_image(self.layer.metadata['path'])
            rings = []
            for boundary in reversed(output.boundaries):
                rings.append(list(boundary.boundarypoints * self.inbdModel.scale))
        
        self.resultsLayer = Shapes(rings,
                                    edge_width=8,
                                    face_color='white',
                                    edge_color='red',
                                    scale=self.layer.scale,
                                    units=self.layer.units,
                                    blending='minimum',
                                    shape_type='polygon')
        self.resultsLayer.metadata['parent'] = self.layer
        self.resultsLayer.metadata['parent_path'] = self.layer.metadata['path']
        self.resultsLayer.name = 'pith and rings of ' + self.layer.name

            
    def removeInnerRing(self, ringPolygons, pithPolygons):
        innerRingShapeList = Shapes([ringPolygons[-1]], shape_type='polygon')
        pithShapeList = Shapes(pithPolygons, shape_type='polygon')
        innerRingLabels = innerRingShapeList.to_masks(mask_shape=self.layer.data.shape[0:2])[0] * 1
        pithLabels = pithShapeList.to_masks(mask_shape=self.layer.data.shape[0:2])[0] * 1
        areaRing = len(innerRingLabels[innerRingLabels>0])
        areaPith = len(pithLabels[pithLabels>0])
        radiusRing = math.sqrt(areaRing) / math.pi
        radiusPith = math.sqrt(areaPith) / math.pi
        if radiusRing - radiusPith < self.minRadiusDeltaPithInnerRing:
            ringPolygons.pop()


    @classmethod
    def ringToPolygons(cls, datas):
        len_data = [len(data) for data in datas]
        sort_leng_data = np.argsort(np.array(len_data)[1:])[::-1] + 1
        rings = []
        for po in sort_leng_data:
            rings.append(list(datas[po][:, 0, ::-1]))
        rings.append(list(datas[0][:, 0, ::-1]))
        return rings


    @classmethod
    def maskToPolygons(cls, data):
        labels = measure.label(data)
        rings = []
        maxLabel = np.max(labels)
        for ring in range(1, maxLabel + 1):
            mask = np.ndarray.copy(labels)
            mask[mask < ring] = 0
            mask[mask > ring] = 0
            mask = (mask // ring) * 255
            mask = mask.astype(np.uint8)
            mask = ndimage.binary_fill_holes(mask)
            mask = mask.astype(np.uint8)
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            polys = [np.squeeze(e) for e in contours[0]]
            changed = [np.array([y, x]) for x, y in polys]
            rings.append(changed)
        return rings


    def measure(self):
        """Measure the features on the shape layer and add them to the operations measurements."""
        for label, shape in enumerate(reversed(self.resultsLayer.data)):
            shapeLayer = Shapes([shape],
                                   scale=self.layer.scale,
                                   units=self.layer.units,
                                   shape_type='polygon' )
            shapeLayer.metadata['parent'] = self.layer
            shapeLayer.metadata['parent_path'] = self.layer.metadata['path']
            shapeLayer.name = 'pith and rings of ' + self.layer.name
            objectType = "ring"
            if label == 0:
                objectType = "pith"
            self.measureOp = MeasureShape(shapeLayer, object_type=objectType)
            self.measureOp.do()
            self.measureOp.addToTable(self.measurements)
            self.measurements['label'][-1] = label


    def loadModels(self, pathModel, typeKey):
        path_url = self.getModelURLsFilePath()
        with open(path_url) as aFile:
            paths = json.load(aFile)
        model = paths[typeKey]
        format = '.pt.zip' if typeKey == 'inbd' else '.keras'
        models = []
        for key, url in model.items():
            filename = key + format
            destPath = os.path.join(pathModel, filename)
            if os.path.exists(destPath):
                models.append(filename)
            else:
                print(url, destPath)
                outPath, msg = urlretrieve(url, destPath)
                print("downloaded ", outPath, msg)
                models.append(filename)

        return models


    @classmethod
    def getModelURLsFilePath(cls):
        path = ''
        with importlib.resources.path(napari_tree_rings.config, "model_urls.json") as config_file:
            path = config_file
        return path


    def loadOptions(self):
        if not os.path.exists(self.optionsPath):
            self.saveOptions()
        with open(self.optionsPath) as f:
            self.options = json.load(f)


    def saveOptions(self):
        with open(self.optionsPath, 'w') as f:
            json.dump(self.options, f)


class BatchSegmentTrunk:
    """Run the trunk segmentation on all tiff-images in a given folder and save the control shapes and the
    measurements into an output folder."""

    def __init__(self, sourceFolder, outputFolder):
        self.sourceFolder = sourceFolder
        self.outputFolder = outputFolder
        self.measurements =  {}
        self.segmenter = None
        self.ringSegmenter = None


    def runBatch(self):
        """Run the batch trunk segmentation."""

        imageFileNames = os.listdir(self.sourceFolder)
        self.segmenter = None
        if not imageFileNames:
            return
        
        self.ringSegmenter = RingsSegmenter(None)
        self.segmenter = TrunkSegmenter(None)
        for imageFilename in imageFileNames:
            path = os.path.join(self.sourceFolder, imageFilename)
            img = tiff.imread(path)
            imageLayer = Image(np.array(img))
            imageLayer.metadata['path'] = path
            imageLayer.name = imageFilename
            imageLayer.metadata['name'] = imageFilename

            self.ringSegmenter.layer = imageLayer
            self.ringSegmenter.measurements = dict()
            self.ringSegmenter.setPixelSizeAndUnit()
            self.ringSegmenter.segment()
            self.ringSegmenter.measure()
            df = pd.DataFrame(self.ringSegmenter.measurements)

            self.segmenter.layer = imageLayer
            self.segmenter.measurements = dict()
            self.segmenter.setPixelSizeAndUnit()
            self.segmenter.segment()
            self.segmenter.measure()
            df = pd.concat([df, pd.DataFrame(self.segmenter.measurements)], ignore_index=True)

            # self.measurements = self.segmenter.measurements
            # TableTool.addTableAToB(self.ringSegmenter.measurements, self.measurements)
            csvFilename = os.path.splitext(imageFilename)[0] + ".csv"
            csvRingsFilename = os.path.splitext(imageFilename)[0] + "_rings.csv"
            path = os.path.join(self.outputFolder, csvFilename)
            ringsPath = os.path.join(self.outputFolder, csvRingsFilename)
            self.segmenter.shapeLayer.save(path)
            self.ringSegmenter.resultsLayer.save(ringsPath)
            # yield self.measurements

            # Example of area_growth
            area = np.array(df['area'])
            df['area_growth'] = np.concatenate([[area[0]], area[1:] - area[:-1]])

            # If you would like to add anymore measurements, please add them here
            ## 

            df.to_csv(os.path.join(self.outputFolder, os.path.splitext(imageFilename)[0] + '_parameters.csv'))

        # time = str(datetime.datetime.now())
        # tablePath = os.path.join(self.outputFolder, time + "_trunk-measurements.csv")