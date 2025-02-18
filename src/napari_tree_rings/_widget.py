"""
This module contains four napari widgets declared in
different ways:

- a pure Python function flagged with `autogenerate: true`
    in the plugin manifest. Type annotations are used by
    magicgui to generate widgets for each parameter. Best
    suited for simple processing tasks - usually taking
    in and/or returning a layer.
- a `magic_factory` decorated function. The `magic_factory`
    decorator allows us to customize aspects of the resulting
    GUI, including the widgets associated with each parameter.
    Best used when you have a very simple processing task,
    but want some control over the autogenerated widgets. If you
    find yourself needing to define lots of nested functions to achieve
    your functionality, maybe look at the `Container` widget!
- a `magicgui.widgets.Container` subclass. This provides lots
    of flexibility and customization options while still supporting
    `magicgui` widgets and convenience methods for creating widgets
    from type annotations. If you want to customize your widgets and
    connect callbacks, this is the best widget option for you.
- a `QWidget` subclass. This provides maximal flexibility but requires
    full specification of widget layouts, callbacks, events, etc.

References:
- Widget specification: https://napari.org/stable/plugins/guides.html?#widgets
- magicgui docs: https://pyapp-kit.github.io/magicgui/

Replace code below according to your needs.
"""

from typing import TYPE_CHECKING

from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget
from napari.layers.image.image import Image
from napari_tree_rings.image.fiji import SegmentTrunk
from napari_tree_rings.image.fiji import FIJI
from napari.layers import Image, Layer
from napari_tree_rings.progress import IndeterminedProgressThread
from typing import Iterable
if TYPE_CHECKING:
    import napari



class SegmentTrunkWidget(QWidget):


    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.runButton = None
        self.createLayout()
        startupWorker = FIJI.startUpThread()
        startupWorker.returned.connect(self.onStartUpFinished)
        self.startUpProgress = IndeterminedProgressThread("Initializing FIJI...")
        self.startUpProgress.start()
        startupWorker.start()


    def createLayout(self):
        self.runButton = QPushButton("&Run")
        self.runButton.clicked.connect(self.onRunButtonPressed)
        self.runButton.setEnabled(False)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.runButton)


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
        layer = self.getActiveLayer()
        if not layer or not type(layer) is Image:
            return
        segmentTrunk = SegmentTrunk(layer)
        segmentTrunk.run()
        py_image = segmentTrunk.result
        for _, v in py_image.metadata.items():
            if isinstance(v, Layer):
                self.viewer.add_layer(v)
                v.edge_color = "Red"
                v.edge_width = 40
                v.blending = 'minimum'
                v.refresh()
            elif isinstance(v, Iterable):
                for itm in v:
                    if isinstance(itm, Layer):
                        self.viewer.add_layer(itm)
                        itm.edge_color = "Red"
                        itm.edge_width = 40
                        itm.blending = 'minimum'
                        itm.refresh()
