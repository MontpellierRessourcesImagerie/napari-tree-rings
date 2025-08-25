import numpy as np
import tifffile
import os
from napari_tree_rings._widget import (
    SegmentTrunkWidget,
    SegmentTrunkOptionsWidget,
    SegmentRingsOptionsWidget
)



# capsys is a pytest fixture that captures stdout and stderr output streams
def test_segment_trunk_widget(make_napari_viewer, tmp_path):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()
    img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

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
    my_widget.onRunSegmentRingsButtonPressed()

    # call method in batch
    img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    tiff_path = os.path.join(tmp_path, "test_image_02.tif")
    tifffile.imwrite(tiff_path, img)
    my_widget.sourceFolder = tmp_path

    my_widget.runBatchButtonClicked()

    # read captured output and check that it's as we expected
    print(my_widget.measurements, 'gaugau')
    assert my_widget is not None


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
