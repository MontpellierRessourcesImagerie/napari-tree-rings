"""
Widgets of the napari-tree-ring plugin.
"""

import os
import napari
from napari.qt.threading import create_worker
from typing import TYPE_CHECKING
from pathlib import Path
from qtpy.QtGui import QIcon
from qtpy.QtCore import Qt
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QGroupBox, QFileDialog
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QWidget
from qtpy.QtWidgets import QApplication
from scyjava import jimport
from napari.layers import Image
from napari_tree_rings.progress import IndeterminedProgressThread
from napari_tree_rings.qtutil import WidgetTool, TableView
from napari_tree_rings.image.process import TrunkSegmenter
from napari_tree_rings.image.process import BatchSegmentTrunk
from napari_tree_rings.image.fiji import FIJI
from napari_tree_rings.image.fiji import SegmentTrunk


if TYPE_CHECKING:
    import napari



class SegmentTrunkWidget(QWidget):


    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.fieldWidth = 300
        self.runButton = None
        self.runBatchButton = None
        self.segmenter = None
        self.batchSegmenter = None
        self.measurements = {}
        self.table = TableView(self.measurements)
        self.segmentTrunkOptionsButton = None
        self.sourceFolderInput = None
        self.outputFolderInput = None
        self.sourceFolder = str(Path.home())
        self.outputFolder = str(Path.home())
        startupWorker = FIJI.getStartUpThread()
        startupWorker.returned.connect(self.onStartUpFinished)
        self.startUpProgress = IndeterminedProgressThread("Initializing FIJI...")
        self.startUpProgress.start()
        startupWorker.start()
        app = QApplication.instance()
        app.lastWindowClosed.connect(self.onCloseApplication)
        self.tableDockWidget = self.viewer.window.add_dock_widget(self.table, area='right', name='measurements', tabify=False)
        self.createLayout()


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
        sourceFileLayout = QHBoxLayout()
        sourceFolderLabel, self.sourceFolderInput = WidgetTool.getLineInput(self, "Source: ",
                                                              self.sourceFolder,
                                                              self.fieldWidth,
                                                              self.sourceFolderChanged)
        sourceFolderBrowseButton = QPushButton("Browse")
        sourceFolderBrowseButton.clicked.connect(self.browseSourceFolderClicked)
        sourceFileLayout.addWidget(sourceFolderLabel)
        sourceFileLayout.addWidget(self.sourceFolderInput)
        sourceFileLayout.addWidget(sourceFolderBrowseButton)
        outputFileLayout = QHBoxLayout()
        outputFolderLabel, self.outputFolderInput = WidgetTool.getLineInput(self, "Output: ",
                                                                            self.outputFolder,
                                                                            self.fieldWidth,
                                                                            self.outputFolderChanged)
        outputFolderBrowseButton = QPushButton("Browse")
        outputFolderBrowseButton.clicked.connect(self.browseOutputFolderClicked)
        outputFileLayout.addWidget(outputFolderLabel)
        outputFileLayout.addWidget(self.outputFolderInput)
        outputFileLayout.addWidget(outputFolderBrowseButton)
        runBatchLayout = QHBoxLayout()
        self.runBatchButton = QPushButton("Run &Batch")
        self.runBatchButton.clicked.connect(self.runBatchButtonClicked)
        self.runBatchButton.setEnabled(False)
        runBatchLayout.addWidget(self.runBatchButton)
        batchLayout = QVBoxLayout()
        batchGroupBox = QGroupBox("Batch Segment Trunk")
        groupBoxLayout = QVBoxLayout()
        batchGroupBox.setLayout(groupBoxLayout)
        groupBoxLayout.addLayout(sourceFileLayout)
        groupBoxLayout.addLayout(outputFileLayout)
        groupBoxLayout.addLayout(runBatchLayout)
        batchLayout.addWidget(batchGroupBox)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(segmentLayout)
        mainLayout.addLayout(batchLayout)
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
        self.runBatchButton.setEnabled(True)


    def onRunButtonPressed(self):
        layer = self.getActiveLayer()
        if not layer or not type(layer) is Image:
            return
        layer.metadata['path'] = layer.source.path
        self.segmenter = TrunkSegmenter(layer)
        self.segmenter.measurements = self.measurements
        worker = create_worker(self.segmenter.run,
                               _progress={'total': 4, 'desc': 'Segment Trunk'})
        worker.finished.connect(self.onSegmentationFinished)
        worker.start()


    def runBatchButtonClicked(self):
        imagePaths = os.listdir(self.sourceFolder)
        self.batchSegmenter = BatchSegmentTrunk(self.sourceFolder, self.outputFolder)
        worker = create_worker(self.batchSegmenter.run,
                               _progress={'total': len(imagePaths), 'desc': 'Batch Segment Trunk'})
        worker.yielded.connect(self.onTableChanged)
        worker.start()


    @Slot()
    def onSegmentationFinished(self):
        self.viewer.scale_bar.unit = self.segmenter.tiffFileTags.unit
        self.addTrunkSegmentationToViewer(self.segmenter.shapeLayer)
        self.tableDockWidget.close()
        self.measurements = self.segmenter.measurements
        self.table = TableView(self.measurements)
        self.tableDockWidget = self.viewer.window.add_dock_widget(self.table, area='right', name='measurements',
                                                                  tabify=False)

    def onOptionsButtonPressed(self):
        optionsWidget = SegmentTrunkOptionsWidget(self.viewer)
        self.viewer.window.add_dock_widget(optionsWidget, area='right', name='Options of Segment Trunk ')


    def addTrunkSegmentationToViewer(self, v):
        self.viewer.add_layer(v)
        v.edge_color = "Red"
        v.edge_width = 40
        v.blending = 'minimum'
        v.refresh()


    def onCloseApplication(self):
        print("closing fiji...")
        System = jimport("java.lang.System")
        System.exit(0)


    def sourceFolderChanged(self):
        pass


    def outputFolderChanged(self):
        pass


    def browseSourceFolderClicked(self):
        sourceFolderFromUser = QFileDialog.getExistingDirectory(self, "Source Folder", self.sourceFolder,
                                                                QFileDialog.ShowDirsOnly)
        if sourceFolderFromUser:
            self.sourceFolder = sourceFolderFromUser
            self.sourceFolderInput.setText(self.sourceFolder)


    def browseOutputFolderClicked(self):
        outputFolderFromUser = QFileDialog.getExistingDirectory(self, "Output Folder", self.outputFolder,
                                                                QFileDialog.ShowDirsOnly)
        if outputFolderFromUser:
            self.outputFolder = outputFolderFromUser
            self.outputFolderInput.setText(self.outputFolder)


    @Slot(object)
    def onTableChanged(self, measurements):
        self.measurements = measurements
        self.table = TableView(self.measurements)
        self.viewer.window.remove_dock_widget(self.tableDockWidget)
        self.tableDockWidget.close()
        self.tableDockWidget = self.viewer.window.add_dock_widget(self.table, area='right', name='measurements',
                                                                  tabify=False)



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
        pass


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
        self.setOptionsFromDialog()
        self.segmentTrunk.saveOptions()


    def saveAndCloseButtonPressed(self):
        self.setOptionsFromDialog()
        self.segmentTrunk.saveOptions()
        self.viewer.window.remove_dock_widget(self)
        self.close()


    def cancelAndCloseButtonPressed(self):
        self.viewer.window.remove_dock_widget(self)
        self.close()

