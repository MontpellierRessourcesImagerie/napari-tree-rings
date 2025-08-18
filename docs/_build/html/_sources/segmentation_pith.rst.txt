============================
Pith Prediction using UNet
============================

.. _unet:

0. What is UNet?
================

- UNet is a deep learning architecture that belongs to the convolutional neural network family.
- Since it is supervised learning, certain inputs and expected segmentations (== ground-truth) are needed for training.
- Following training, the model's inference phase generates a probability map. To turn this probability map into a mask, it must be thresholded.
- This plugin applies UNet on the pith prediction.
- Rather than producing an intance segmentation, UNet produces a semantic segmentation. It indicates the response to the query, "Is this pixel part of the pith?", which will be contained in each pixel.

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
    - **Flipping**: The images are randomly flipped horizontally and/or vertically.
    - **Random rotations**: The images are randomly rotated from -20 degrees to 20 degrees.
    - **90-degree rotations**: The images are randomly rotated in 90, 180, and 270 degrees.

These augmentations are applied before cropping and training to provide a wider variety of spatial and contextual information.

3. Cropping and Resizing
========================

- Since the pith regions are small compared to the whole image size, we have to crop the pith region as 20 % of the height of image to solve the class imbalance problem.
- We resize the cropped pith input to 256x256 pixels to ensure computational efficiency.

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
| pith_path         | Directory to save pre-processed images for training pith-prediction model.                                                       |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| tile_path         | Directory to save pre-processed images for training ring-segmentation model. If you just want to generate pith dataset, tile_path|
|                   | should be None.                                                                                                                  |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| pithWhole         | True/False. If True, the pith image will not be cropped (default is False).                                                      |
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
| filter_num        | The number of filters in UNet architecture (default is [16, 24, 40, 80, 960]).                                                   |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| attention         | True/False. In this case, attention is False to use UNet for training.                                                           |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| output_activation | Output activation. In pith prediction, the recommended output activation is 'sigmoid'.                                           |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| loss              | Loss function. In pith prediction, the recommended loss function is bce_dice_loss(bce_coef=0.5)                                  |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| name              | Name of the saved model.                                                                                                         |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| numEpochs         | Number of epochs. In pith prediction, the recommended number is 100.                                                             |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
| input_size        | Size of input. Default is (256, 256, 1).                                                                                         |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------+
