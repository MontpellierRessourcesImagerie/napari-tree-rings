======================================
How to use "Napari Tree Rings" widget?
======================================

1. Get your data ready
======================
The Napari plugin expects your data to respect a precise format:
   - The images must be available as dissociated TIF images (no jpg, no 3D stack, no video, …).
   - The plugin only accept images in 2D grayscale (Y, X) or 2D RGB (Y, X, 3).
   - In the case of running batch, all the images that you want to process must be in the same folder.
   - Avoid using special characters in the folder's name. (Tips: `Doranum <https://doranum.fr/stockage-archivage/comment-nommer-fichiers_10_13143_wgqw-aa59/>`_)
   - Both models used by this plugin were trained on images with the size ranging from 2000x2000 to 10000x10000 pixels, you may have troubles if your images out of this size.

.. code-block:: bash

   .
   ├── 📁 my-awesome-experiment
   │   ├── some-image.tif
   │   ├── another-image.tif
   │   ├── ...
   │   └── last-image.tif

2. Workflow
===========

a. Import your images
---------------------

- In this section, you will import your experiment so you can visualize and analyze it.
- Open the plugin via Plugins > Segment Trunk (Napari Tree Rings).
- For running only one image, you just have to drag and drop that image into the interface.
- For running batch, press the :code:`Browse` button at the :code:`Source` in the :code:`Batch Segment Trunk` tag and choose the path to the foloder containing your images. It is the path of "my-awesome-experiment" in the previous example.
- You can adjust the contrast and brightness in the upper-left corner of Napari.
- If your image doesn't appear in the viewer anymore, or if it becomes too small, you can click on the little "Home" button in the lower-left corner of Napari to center the view.

b. Segment the tree rings (Segmentation)
----------------------------------------

- If you would like to change the default configurations before the segmentation, click on the ⚙ button:

+---------------+--------------------+-------------------------------------------------------------------------------------------------------------+
| Options of    | Setting            | Description                                                                                                 |
+===============+====================+=============================================================================================================+
| Segment Trunk | Scale Factor       | Controls how much your image is scaled down before processing (default is 8).                               |
|               +--------------------+-------------------------------------------------------------------------------------------------------------+
|               | Opening radius     | The size (in pixels) of the structuring element used in the opening operation, which removes small objects  |
|               |                    | and smooths boundaries in the image (default is 96).                                                        |
+---------------+--------------------+-------------------------------------------------------------------------------------------------------------+
| Segment Rings | Ring model         | Choose model for segmenting tree ring boundaries.                                                           |
|               +--------------------+-------------------------------------------------------------------------------------------------------------+
|               | Pith model         | Choose model for segmenting pith.                                                                           |
|               +--------------------+-------------------------------------------------------------------------------------------------------------+
|               | Patch size         | Image will be cropped into smaller patches to ensure computational cost. The default is 256, since it is the|
|               |                    | size we used to train our models.                                                                           |
|               +--------------------+-------------------------------------------------------------------------------------------------------------+
|               | Overlap            | The proportion of length shared between adjacent image tiles to ensure smooth transitions and avoid edge    |
|               |                    | artifacts. The default is 60.                                                                               |
|               +--------------------+-------------------------------------------------------------------------------------------------------------+
|               | Batch size         | The number of tiles processed together in a single iteration. The default is 8.                             |
|               +--------------------+-------------------------------------------------------------------------------------------------------------+
|               | Rescale Factor     | Controls how much your image is scaled down before post-processing (default is 5).                          |
|               +--------------------+-------------------------------------------------------------------------------------------------------------+
|               | Heuristic function | Choose the heuristic function applied in the post-processing of A-star algorithm. Default is H0.            |
+---------------+--------------------+-------------------------------------------------------------------------------------------------------------+

- You have to click the :code:`Save` button to save the new configurations.
- For running only one image, you can choose the output folder (to export CSV file) by pressing the :code:`Browse` button at the :code:`Output` in the :code:`Segment Rings` tag.
- For running batch, press the :code:`Browse` button at the :code:`Output` in the :code:`Batch Segment Trunk` tag.
- You can just click the :code:`Run` button in :code:`Segment Rings` tag to start the segmentation on one image, or :code:`Run Batch` button in :code:`Batch Segment Trunk` tag to start the batch segmentation.
- The first time, the models will have to be downloaded from internet.

C. Extract measures (Measures)
------------------------------
- The exported CSV files will be extracted at the end of the process.
- For running one image, there is only one CSV file exported at the chosen output folder, containing necessary measuremnts (except :code:`area_growth`).
- For running batch, each image will have three exported CSV files:
   - {imageName}.csv: containing the coordinates of bark boundary
   - {imageName}_rings.csv: containing the coordinates of ring and pith boundaries.
   - {imageName}_table.csv: containing the necessary measurements.

3. Examples of processed data
=============================

.. tabs::

   .. tab:: Input images

      +----------------------------------------------------+----------------------------------------------------+
      | .. image:: _images/input-01.png                    | .. image:: _images/input-02.png                    |
      |   :height: 512px                                   |   :height: 512px                                   | 
      |   :width: 600px                                    |   :width: 600px                                    |
      |   :align: center                                   |   :align: center                                   |
      +----------------------------------------------------+----------------------------------------------------+

   .. tab:: Segmented images

      +----------------------------------------------------+----------------------------------------------------+
      | .. image:: _images/segmented-01.png                | .. image:: _images/segmented-02.png                |
      |   :height: 512px                                   |   :height: 512px                                   | 
      |   :width: 600px                                    |   :width: 600px                                    |
      |   :align: center                                   |   :align: center                                   |
      +----------------------------------------------------+----------------------------------------------------+

4. Workflow diagram
===================

.. image:: _images/complete-workflow.png
   :align: center