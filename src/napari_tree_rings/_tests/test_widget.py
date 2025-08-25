import numpy as np
import tifffile
import os
from napari_tree_rings._widget import (
    SegmentTrunkWidget,
    SegmentTrunkOptionsWidget,
    SegmentRingsOptionsWidget
)
from napari_tree_rings._tests import utils



# capsys is a pytest fixture that captures stdout and stderr output streams
def test_segment_trunk_widget(make_napari_viewer, tmp_path):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()
    img = utils.make_checkboard((1000, 1000), 1, 'grayscale')

    # Save it to a temporary TIFF file
    tiff_path = os.path.join(tmp_path, "test_image.tif")
    tifffile.imwrite(tiff_path, img)

    # Load the TIFF into napari
    viewer.open(str(tiff_path))

    # create our widget, passing in the viewer
    my_widget = SegmentTrunkWidget(viewer)

    # call our widget method
    my_widget.onRunButtonPressed()
    my_widget.onSegmentRingsOptionsButtonPressed()
    # my_widget.onRunSegmentRingsButtonPressed()

    # read captured output and check that it's as we expected
    assert my_widget is not None


# def test_segment_trunk_batch_widget(make_napari_viewer, tmp_path):
#     img = utils.make_checkboard((1000, 1000), 1, 'grayscale')
#     tiff_path = os.path.join(tmp_path, "test_image.tif")
#     tifffile.imwrite(tiff_path, img)

#     img = utils.make_checkboard((1000, 1000), 1, 'grayscale')
#     tiff_path = os.path.join(tmp_path, "test_image_02.tif")
#     tifffile.imwrite(tiff_path, img)

#     viewer = make_napari_viewer()
#     my_widget = SegmentTrunkWidget(viewer)
#     my_widget.sourceFolder = tmp_path

#     my_widget.runBatchButtonClicked()

#     assert my_widget is not None

def test_segment_ring_options(make_napari_viewer):
    viewer = make_napari_viewer()

    my_widget = SegmentRingsOptionsWidget(viewer)
    
    my_widget.saveOptionsButtonPressed()

    assert my_widget is not None


def test_segment_trunk_options(make_napari_viewer):
    viewer = make_napari_viewer()

    my_widget = SegmentTrunkOptionsWidget(viewer)
    
    my_widget.saveOptionsButtonPressed()

    assert my_widget is not None
