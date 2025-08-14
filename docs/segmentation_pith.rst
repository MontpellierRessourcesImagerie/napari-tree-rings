=======================
Segmentation using UNet
=======================

0. What is UNet?
================

- UNet is a deep learning architecture that belongs to the convolutional neural network family.
- Since it is educated via supervised learning, certain inputs and expected segmentations (== ground-truth) are needed for training.
- Following training, the model's inference phase generates a probability map. To turn this probability map into a mask, it must be thresholded.
- This plugin applies UNet on the pith region segment.
- Rather than producing an examples segmentation, UNet produces a semantic segmentation. It indicates that the response to the query, "Is this pixel part of the pith?" will be contained in each pixel.

1. Get your data ready
======================

- You can retrain the model if you have some annotated data by using the file ./src/tree_ring_analyzer/training.py on `Tree Ring Analyzer GitHub <https://github.com/MontpellierRessourcesImagerie/tree-ring-analyzer/>`_.
- Before starting, you have to perform augmentation (Section 2), and create the two folders named "models" and "history" to store all the new model and history versions you create.
- You can name the model as you like.
- The outputs produced by this script include:
    - history/{name}.json: a dictionary that contains a record of training metrics (e.g., loss, accuracy) for each epoch.
    - models/{name}.keras: a model saved in Keras format.
    - models/{name}.keras: a model saved in H5 format.
    
2. Data augmentation
====================

To increase the data variablity, we need to apply augmentation to ensure that the model generalizes well to different types of data.

The data augmentation includes:
    - **Basic augmentation**:
            - **Flipping**: The images are randomly flipped horizontally and/or vertically.
            - **Random rotations**: The images are randomly rotated from -20 degrees to 20 degrees.
            - **90-degree rotations**: The images are randomly rotated in 90, 180, and 270 degrees.
    - **Hole augmentation**: The images are randomly added white holes.