"""
Widgets of the napari-tree-ring plugin.
"""

import os
import weakref
from typing import TYPE_CHECKING
from pathlib import Path
from PyQt5.QtGui import QIcon
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QWidget
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QTableWidgetItem
from scyjava import jimport
from napari_tree_rings.image.fiji import SegmentTrunk
from napari_tree_rings.image.fiji import FIJI
from napari.layers import Image, Layer
from napari_tree_rings.image.file_util import TiffFileTags
from napari_tree_rings.progress import IndeterminedProgressThread
from napari_tree_rings.qtutil import WidgetTool, TableView
from napari_tree_rings.image.measure import MeasureShape
from typing import Iterable
if TYPE_CHECKING:
    import napari



class SegmentTrunkWidget(QWidget):


    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.runButton = None
        self.runProgress = None
        self.pixelSizeProgress = None
        self.segmentTrunk = None
        self.tiffFileTags = None
        self.layer = None
        self.measurements = {}
        self.table = TableView(self.measurements)
        self.segmentTrunkOptionsButton = None
        self.createLayout()
        self.measureTrunk = None
        startupWorker = FIJI.getStartUpThread()
        startupWorker.returned.connect(self.onStartUpFinished)
        self.startUpProgress = IndeterminedProgressThread("Initializing FIJI...")
        self.startUpProgress.start()
        startupWorker.start()
        app = QApplication.instance()
        app.lastWindowClosed.connect(self.onCloseApplication)
        self.tableDockWidget = self.viewer.window.add_dock_widget(self.table, area='right', name='measurements', tabify=False)


    def createLayout(self):
        self.runButton = QPushButton("&Run")
        self.runButton.clicked.connect(self.onRunButtonPressed)
        self.runButton.setEnabled(False)
        segmentLayout = QHBoxLayout()
        resourcesPATH = os.path.join(Path(__file__).parent.resolve(), "resources", "gear.png")
        gearIcon = QIcon(resourcesPATH)
        self.segmentTrunkOptionsButton = QPushButton()
        self.segmentTrunkOptionsButton.setIcon(gearIcon)
        self.segmentTrunkOptionsButton.clicked.connect(self.onOptionsButtonPressed)
        segmentLayout.addWidget(self.runButton)
        segmentLayout.addWidget(self.segmentTrunkOptionsButton)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(segmentLayout)
        self.setLayout(mainLayout)


    def getActiveLayer(self):
        if len(self.viewer.layers) == 0:
            return None
        if len(self.viewer.layers) == 1:
            layer = self.viewer.layers[0]
        else:
            layer = self.viewer.layers.selection.active
        return layer


    def onStartUpFinished(self):
        self.startUpProgress.stop()
        self.runButton.setEnabled(True)


    def onRunButtonPressed(self):
        self.layer = self.getActiveLayer()
        if not self.layer or not type(self.layer) is Image:
            return
        if self.layer.source.path:
            self.tiffFileTags = TiffFileTags(self.layer.source.path)
            worker = self.tiffFileTags.getPixelSizeAndUnitWorker()
            worker.returned.connect(self.onGetPixelSizeReturned)
            self.pixelSizeProgress = IndeterminedProgressThread("Reading pixel size and unit...")
            self.pixelSizeProgress.start()
            worker.start()


    def onOptionsButtonPressed(self):
        SegmentTrunk.showOptionsDialog()


    def onGetPixelSizeReturned(self):
        pixelSize = self.tiffFileTags.pixelSize
        unit = self.tiffFileTags.unit
        self.layer.scale = (pixelSize, pixelSize)
        self.layer.units = (unit, unit)
        self.viewer.scale_bar.unit = unit
        self.pixelSizeProgress.stop()
        self.segmentTrunk = SegmentTrunk(self.layer)
        runThread = self.segmentTrunk.getRunThread()
        runThread.returned.connect(self.onSegmentTrunkFinished)
        self.runProgress = IndeterminedProgressThread("Segmenting the trunk...")
        self.runProgress.start()
        runThread.start()


    def onSegmentTrunkFinished(self):
        py_image = self.segmentTrunk.result
        shapeLayer = None
        for _, v in py_image.metadata.items():
            if isinstance(v, Layer):
                self.addTrunkSegmentationToViewer(v)
                shapeLayer = v
            elif isinstance(v, Iterable):
                for itm in v:
                    if isinstance(itm, Layer):
                        self.addTrunkSegmentationToViewer(itm)
                        shapeLayer = itm
        self.runProgress.stop()
        self.measureTrunk = MeasureShape(shapeLayer, "trunk")
        worker = self.measureTrunk.getRunThread()
        worker.returned.connect(self.onMeasureTrunkFinished)
        self.runProgress = IndeterminedProgressThread("Measuring...")
        self.runProgress.start()
        worker.start()


    def onMeasureTrunkFinished(self):
        self.measureTrunk.addToTable(self.measurements)
        self.tableDockWidget.close()
        self.table = TableView(self.measurements)
        self.tableDockWidget = self.viewer.window.add_dock_widget(self.table, area='right', name='measurements',
                                                                  tabify=False)
        self.runProgress.stop()


    def addTrunkSegmentationToViewer(self, v):
        self.viewer.add_layer(v)
        v.edge_color = "Red"
        v.edge_width = 40
        v.blending = 'minimum'
        v.scale = self.layer.scale
        v.units = self.layer.units
        v.metadata['parent'] = self.layer
        v.metadata['parent_path'] = self.layer.source.path
        v.name = 'trunk of ' + self.layer.name
        v.refresh()


    def onCloseApplication(self):
        print("closing fiji...")
        System = jimport("java.lang.System")
        System.exit(0)



class SegmentTrunkOptionsWidget(QWidget):


    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.segmentTrunk = SegmentTrunk(None)
        self.options = self.segmentTrunk.options
        self.scaleFactorInput = None
        self.fieldWidth = 50
        self.createLayout()


    def createLayout(self):
        scaleFactorLabel, self.scaleFactorInput = WidgetTool.getLineInput(self, "Scale Factor",
                                                                          self.options['scale'],
                                                                          self.fieldWidth,
                                                                          self.scaleFactorChanged)
        mainLayout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.addRow(scaleFactorLabel, self.scaleFactorInput)
        mainLayout.addLayout(formLayout)
        self.setLayout(mainLayout)


    def scaleFactorChanged(self):
        print("scale factor changed")