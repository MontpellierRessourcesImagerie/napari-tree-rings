======================================
Ring Segmentation using Attention UNet
======================================

0. What is Attention UNet?
==========================

- Attention UNet is UNet combined with attention mechanism to enhance thinner details of ring boundaries (see :ref:`unet`).
- Similar to UNet, certain inputs and expected segmentations (== ground-truth) are needed for training.
- Following training, the model's inference phase generates a distance map.
- This plugin applies Attention UNet on the ring segmentation.
- Rather than producing an instance segmentation, Attention UNet indicates the response to the query, "How far is this pixel from the actual ring boundary?", which will be contained in each pixel.

1. Get your data ready
======================

- You can retrain the model if you have some annotated data by using the file ./src/tree_ring_analyzer/training.py on `Tree Ring Analyzer GitHub <https://github.com/MontpellierRessourcesImagerie/tree-ring-analyzer/>`_.
- Before starting, you have to perform augmentation (Section 2), and create the two folders named "models" and "history" to store all the new model and history versions you create.
- You can name the model as you like.
- The outputs produced by this script include:
    - history/{name}.json: a dictionary that contains a record of training metrics (e.g., loss, accuracy) for each epoch.
    - models/{name}.keras: a model saved in Keras format.
    - models/{name}.h5: a model saved in H5 format.
    
2. Data augmentation
====================

To increase the data variablity, we need to apply augmentation to ensure that the model generalizes well to different types of data.

The data augmentation includes:
    - **Basic augmentation**:
            - **Flipping**: The images are randomly flipped horizontally and/or vertically.
            - **Random rotations**: The images are randomly rotated from -20 degrees to 20 degrees.
            - **90-degree rotations**: The images are randomly rotated in 90, 180, and 270 degrees.
    - **Hole augmentation**: The images are randomly added white holes.

These augmentations are applied before cropping and training to provide a wider variety of spatial and contextual information.

3. Pre-processing
=================

a. Dilated distance map
-----------------------

- There is a massive imbalance between the background and foreground classes.
- To address that problem, we dilate the ground truth, then calculate the Euclidean distance from the foreground elements to the corresponding nearest background elements, making the ground truth value now ranging from 0 to 13.
- It will make the model easier to learn the thin details of ring boundaries.

b. Gray conversion
------------------

- We convert images to gray scale using the NTSC (National Television System Committee) formula.

c. Cropping
-----------

- We crop the original images to 256x256 pixels with overlap of 60 pixels to ensure computational efficiency.

4. Setup
========

- If you already have a Python environment in which "Tree Ring Analyzer" is installed, it already contains everything you need to prepare dataset and train a model.
- To prepare dataset, you just have to fill the settings described below, and run the script ./src/tree_ring_analyzer/preprocessing.py.

+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| Name              | Description                                                                                                                      |
+===================+==================================================================================================================================+
| input_path        | Directory of original images.                                                                                                    |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| mask_path         | Directory of ground truths.                                                                                                      |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| pith_path         | Directory to save pre-processed images for training pith-prediction model. If you just want to generate ring dataset, pith_path  |
|                   | should be None.                                                                                                                  |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| tile_path         | Directory to save pre-processed images for training ring-segmentation model.                                                     |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| whiteHoles        | True/False. If True, the white holes will be added into ring dataset for augmentation (default is True).                         |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| gaussianHoles     | True/False. If True, the gaussian holes will be added into ring dataset for augmentation (default is False).                     |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| changeColor       | True/False. If True, the order of image channels will be changed for augmentation (default is False).                            |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| dilate            | An integer. If not None, the tree rings in ground truth will be dilated with the given number of iterations before calculating   |
|                   | the distance map (default is 10).                                                                                                |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| distance          | True/False. If True, distance map will be calculated.                                                                            |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| skeleton          | True/False. If True, the tree rings in ground truth will be skeletonized.                                                        |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+

- To launch the training, you just have to fill the settings described below, and run the script ./src/tree_ring_analyzer/training.py.

+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| Name              | Description                                                                                                                      |
+===================+==================================================================================================================================+
| train_input_path  | Directory of training input path.                                                                                                |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| train_mask_path   | Directory of training mask path.                                                                                                 |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| val_input_path    | Directory of validation input path.                                                                                              |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| val_mask_path     | Directory of validation mask path.                                                                                               |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| filter_num        | The number of filters in Attention UNet architecture (default is [16, 24, 40, 80, 960]).                                         |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| attention         | True/False. In this case, attention is True to use Attention UNet for training.                                                  |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| output_activation | Output activation. In ring segmentation, the recommended output activation is 'linear'.                                          |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| loss              | Loss function. In ring segmentation, the recommended loss function is 'mse'.                                                     |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| name              | Name of the saved model.                                                                                                         |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| numEpochs         | Number of epochs. In ring segmentation, the recommended number is 30.                                                            |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| input_size        | Size of input. Default is (256, 256, 1).                                                                                         |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+

5. Usage
========

- This model consumes patches of 256×256 pixels, with an overlap of 60 pixels.
- The merging is performed with the alpha-blending technique described on the page where the patches creation is explained.