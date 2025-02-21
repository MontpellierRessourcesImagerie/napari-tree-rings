"""
Widgets of the napari-tree-ring plugin.
"""

import os
import weakref
from typing import TYPE_CHECKING
from pathlib import Path
from PyQt5.QtGui import QIcon
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QWidget
from qtpy.QtWidgets import QApplication
from scyjava import jimport
from napari_tree_rings.image.fiji import SegmentTrunk
from napari_tree_rings.image.fiji import FIJI
from napari.layers import Image, Layer
from napari_tree_rings.image.file_util import TiffFileTags
from napari_tree_rings.progress import IndeterminedProgressThread
from napari_tree_rings.qtutil import WidgetTool
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
        self.segmentTrunkOptionsButton = None
        self.createLayout()
        startupWorker = FIJI.getStartUpThread()
        startupWorker.returned.connect(self.onStartUpFinished)
        self.startUpProgress = IndeterminedProgressThread("Initializing FIJI...")
        self.startUpProgress.start()
        startupWorker.start()
        app = QApplication.instance()
        app.lastWindowClosed.connect(self.onCloseApplication)


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
            worker.start()
            self.pixelSizeProgress = IndeterminedProgressThread("Reading pixel size and unit...")
            self.pixelSizeProgress.start()



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
        runThread.finished.connect(self.onSegmentTrunkFinished)
        self.runProgress = IndeterminedProgressThread("Segmenting the trunk...")
        self.runProgress.start()
        runThread.start()


    def onSegmentTrunkFinished(self):
        py_image = self.segmentTrunk.result
        for _, v in py_image.metadata.items():
            if isinstance(v, Layer):
                self.viewer.add_layer(v)
                v.edge_color = "Red"
                v.edge_width = 40
                v.blending = 'minimum'
                v.refresh()
                v.scale = self.layer.scale
                v.units = self.layer.units
                v.source.parent = weakref.ref(self.layer)
            elif isinstance(v, Iterable):
                for itm in v:
                    if isinstance(itm, Layer):
                        self.viewer.add_layer(itm)
                        itm.edge_color = "Red"
                        itm.edge_width = 40
                        itm.blending = 'minimum'
                        itm.scale = self.layer.scale
                        itm.units = self.layer.units
                        itm.source.parent = weakref.ref(self.layer)
                        itm.refresh()
        self.runProgress.stop()


    def onCloseApplication(self):
        print("closing fiji...")
        System = jimport("java.lang.System")
        System.exit(0)


class SegmentTrungOptionsWidget(QWidget):

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.createLayout()


    def createLayout(self):
        pass
        '''
        WidgetTool.getLineInput("Scale Factor", )
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(segmentLayout)
        self.setLayout(mainLayout)
        '''