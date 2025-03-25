import os
import tifffile as tiff
import numpy as np
import datetime
from pandas import DataFrame
from typing import Iterable
from napari.layers import Image, Layer
from napari_tree_rings.image.fiji import SegmentTrunk
from napari_tree_rings.image.file_util import TiffFileTags
from napari_tree_rings.image.measure import MeasureShape


class TrunkSegmenter:


    def __init__(self, layer):
        self.layer = layer
        self.tiffFileTags = None
        self.shapeLayer = None
        self.segmentTrunkOp = None
        self.measureTrunkOp = None
        self.batchMode = False
        self.measurements = {}


    def run(self):
        yield
        self.setPixelSizeAndUnit()
        yield
        self.segmentTrunk()
        yield
        self.measureTrunk()
        yield


    def setPixelSizeAndUnit(self):
        self.tiffFileTags = TiffFileTags(self.layer.metadata['path'])
        self.tiffFileTags.getPixelSizeAndUnit()
        pixelSize = self.tiffFileTags.pixelSize
        unit = self.tiffFileTags.unit
        self.layer.scale = (pixelSize, pixelSize)
        self.layer.units = (unit, unit)


    def segmentTrunk(self):
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


    def measureTrunk(self):
        self.measureTrunkOp = MeasureShape(self.shapeLayer, "trunk")
        self.measureTrunkOp.do()
        self.measureTrunkOp.addToTable(self.measurements)


class BatchSegmentTrunk:


    def __init__(self, sourceFolder, outputFolder):
        self.sourceFolder = sourceFolder
        self.outputFolder = outputFolder
        self.measurements =  {}
        self.segmenter = None


    def run(self):
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
            self.segmenter.batchMode = True
            self.segmenter.measurements = self.measurements
            self.segmenter.setPixelSizeAndUnit()
            self.segmenter.segmentTrunk()
            self.segmenter.measureTrunk()
            self.measurements = self.segmenter.measurements
            csvFilename = os.path.splitext(imageFilename)[0] + ".csv"
            path = os.path.join(self.outputFolder, csvFilename)
            self.segmenter.shapeLayer.save(path)
            yield self.measurements
        time = str(datetime.datetime.now())
        tablePath = os.path.join(self.outputFolder, time + "_trunk-measurements.csv")
        df = DataFrame(self.segmenter.measurements)
        df.to_csv(tablePath)
