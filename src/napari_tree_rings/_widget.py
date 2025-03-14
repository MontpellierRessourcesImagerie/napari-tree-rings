"""
Widgets of the napari-tree-ring plugin.
"""

import os
import weakref
from typing import TYPE_CHECKING
from pathlib import Path
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
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
        optionsWidget = SegmentTrunkOptionsWidget(self.viewer)
        self.viewer.window.add_dock_widget(optionsWidget, area='right', name='Options of Segment Trunk ')


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


    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.segmentTrunk = SegmentTrunk(None)
        self.options = self.segmentTrunk.options
        self.scaleFactorInput = None
        self.sigmaInput = None
        self.thresholdingChoice = None
        self.openingInput = None
        self.closingInput = None
        self.strokeWidthInput = None
        self.interpolationInput = None
        self.vectorsInput = None
        self.barkVectorsInput = None
        self.fieldWidth = 200
        self.thresholdingMethods = FIJI.getAutoThresholdingMethods()
        self.createLayout()


    def createLayout(self):
        scaleFactorLabel, self.scaleFactorInput = WidgetTool.getLineInput(self, "Scale Factor: ",
                                                                          self.options['scale'],
                                                                          self.fieldWidth,
                                                                          self.scaleFactorChanged)
        sigmaLabel, self.sigmaInput = WidgetTool.getLineInput(self, "Sigma: ",
                                                                          self.options['sigma'],
                                                                          self.fieldWidth,
                                                                          self.sigmaChanged)
        thresholdingMethodLabel, self.thresholdingChoice = WidgetTool.getComboInput(self,
                                                                                         "Thresholding Method: ",
                                                                                         self.thresholdingMethods)
        self.thresholdingChoice.setCurrentText(self.segmentTrunk.options['thresholding'])
        openingRadiusLabel, self.openingInput = WidgetTool.getLineInput(self, "Opening radius: ",
                                                              self.options['opening'],
                                                              self.fieldWidth,
                                                              self.openingChanged)
        closingRadiusLabel, self.closingInput = WidgetTool.getLineInput(self, "Closing radius: ",
                                                              self.options['closing'],
                                                              self.fieldWidth,
                                                              self.closingChanged)
        strokeWidthLabel, self.strokeWidthInput = WidgetTool.getLineInput(self, "Stroke width: ",
                                                                          self.options['stroke'],
                                                                          self.fieldWidth,
                                                                          self.strokeWidthChanged)
        interpolationLabel, self.interpolationInput = WidgetTool.getLineInput(self, "Interpolation interval: ",
                                                                              self.options['interpolation'],
                                                                              self.fieldWidth,
                                                                              self.interpolationIntervalChanged)
        vectorsLabel, self.vectorsInput = WidgetTool.getLineInput(self, "Vectors: ",
                                                                  self.options['vectors'],
                                                                  self.fieldWidth,
                                                                  self.vectorsChanged)
        barkLabel, self.barkVectorsInput = WidgetTool.getLineInput(self, "Bark Vectors: ",
                                                            self.options['bark'],
                                                            self.fieldWidth,
                                                            self.barkChanged)
        saveButton = QPushButton("&Save")
        saveButton.clicked.connect(self.saveOptionsButtonPressed)
        saveAndCloseButton = QPushButton("Save && Close")
        saveAndCloseButton.clicked.connect(self.saveAndCloseButtonPressed)
        cancelAndCloseButton = QPushButton("&Cancel && Close")
        cancelAndCloseButton.clicked.connect(self.cancelAndCloseButtonPressed)
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(saveButton)
        buttonsLayout.addWidget(saveAndCloseButton)
        buttonsLayout.addWidget(cancelAndCloseButton)
        mainLayout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.setLabelAlignment(Qt.AlignRight)
        formLayout.addRow(scaleFactorLabel, self.scaleFactorInput)
        formLayout.addRow(sigmaLabel, self.sigmaInput)
        formLayout.addRow(thresholdingMethodLabel, self.thresholdingChoice)
        formLayout.addRow(openingRadiusLabel, self.openingInput)
        formLayout.addRow(closingRadiusLabel, self.closingInput)
        formLayout.addRow(strokeWidthLabel, self.strokeWidthInput)
        formLayout.addRow(interpolationLabel, self.interpolationInput)
        formLayout.addRow(vectorsLabel, self.vectorsInput)
        formLayout.addRow(barkLabel, self.barkVectorsInput)
        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(buttonsLayout)
        self.setLayout(mainLayout)


    def scaleFactorChanged(self):
        print("scale factor changed")


    def sigmaChanged(self):
        pass


    def openingChanged(self):
        pass


    def closingChanged(self):
        pass


    def strokeWidthChanged(self):
        pass


    def interpolationIntervalChanged(self):
        pass


    def vectorsChanged(self):
        pass


    def barkChanged(self):
        pass


    def setOptionsFromDialog(self):
        self.segmentTrunk.options['scale'] = int(self.scaleFactorInput.text().strip())
        self.segmentTrunk.options['sigma'] = float(self.sigmaInput.text().strip())
        self.segmentTrunk.options['thresholding'] = self.thresholdingChoice.currentText().strip()
        self.segmentTrunk.options['opening'] = int(self.openingInput.text().strip())
        self.segmentTrunk.options['closing'] = int(self.closingInput.text().strip())
        self.segmentTrunk.options['stroke'] = int(self.strokeWidthInput.text().strip())
        self.segmentTrunk.options['interpolation'] = int(self.interpolationInput.text().strip())


    def saveOptionsButtonPressed(self):
        print("save options button pressed.")
        self.setOptionsFromDialog()
        self.segmentTrunk.saveOptions()


    def saveAndCloseButtonPressed(self):
        print("save and close options button pressed.")
        self.setOptionsFromDialog()
        self.segmentTrunk.saveOptions()
        self.viewer.window.remove_dock_widget(self)
        self.close()


    def cancelAndCloseButtonPressed(self):
        print("cancel and close button pressed.")
        self.viewer.window.remove_dock_widget(self)
        self.close()

