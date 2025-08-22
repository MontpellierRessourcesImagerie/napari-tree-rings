# from napari_tree_rings import make_sample_data

# add your tests here...


import numpy as np
import tifffile

def test_load_tiff_image(make_napari_viewer, tmp_path):
    # Create fake image data
    img = np.random.randint(0, 255, (50, 50), dtype=np.uint8)

    # Save it to a temporary TIFF file
    tiff_path = tmp_path / "test_image.tif"
    tifffile.imwrite(tiff_path, img)

    # Make viewer
    viewer = make_napari_viewer()

    # Load the TIFF into napari
    viewer.open(str(tiff_path))

    # Check that the viewer now has 1 layer
    assert len(viewer.layers) == 1
    assert viewer.layers[0].data.shape == (50, 50)
