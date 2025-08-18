=========================
Quick start: A user guide
=========================

1. Introduction
===============

- "Tree Ring Analyzer" is a Python module allowing to segment tree rings from 2D stained microscopic cross-sectional tree images.
- "Napari Tree Rings" is a Napari plugin in case you would need a graphical interface.
- The segmentation allows user to segment bark, pith, and annual rings of xylem cells.
- The measures (exported in CSV files by running batch) include:
    - bbox
    - area
    - area_convex
    - axis_major_length
    - axis_minor_length
    - eccentricity
    - orientation
    - area_growth
- From the GUI (Napari), a batch mode is available allowing you to run the whole workflow on an entire folder.

.. image:: _images/overview_noted.png
  :align: center

2. Install the plugin 
=====================

- We strongly recommend to use `conda <https://docs.conda.io/en/latest/miniconda.html>`_ or any other virtual environment manager instead of installing Napari and tree-ring-analyzer in your system's Python.
- Napari is only required if you want to use tree-ring-analyzer with a graphical interface.
- Napari is not part of tree-ring-analyzer's dependencies, so you will have to install it separately.
- Each of the commands below is supposed to be run after you activated your virtual environment.
- If the installation is successful, you will see the plugin in Napari in the top bar menu: Plugins > Segment Trunk (Napari Tree Rings).

A. Development versions
-----------------------

+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Method                | Instructions                                                                                                                                                                             |
+=======================+==========================================================================================================================================================================================+
| pip                   | :code:`pip install git+https://github.com/MontpellierRessourcesImagerie/tree-ring-analyzer.git`                                                                                          |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| GitHub                | :code:`pip install git+https://github.com/MontpellierRessourcesImagerie/tree-ring-analyzer.git`.                                                                                         |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| From an archive       | - Download `the archive <https://github.com/MontpellierRessourcesImagerie/tree-ring-analyzer/archive/refs/heads/main.zip>`_  :code:`pyproject.toml`.                                     |
|                       | - From the terminal containing your virtual env, move to the folder containing the file :code:`pyproject.toml`.                                                                          |
|                       | - Run the command :code:`pip install -e .`                                                                                                                                               |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

B. Stable versions
------------------

+-----------------------+------------------------------------------------------------------------------------+
| Method                | Instructions                                                                       |
+=======================+====================================================================================+
| pip                   | Activate your conda environment, and type :code:`pip install tree-ring-analyzer`.  |
+-----------------------+------------------------------------------------------------------------------------+
| NapariHub             | Go in the plugins menu of Napari and search for "Napari Tree Rings"                |
+-----------------------+------------------------------------------------------------------------------------+


3. Notes 
========

- The plugin provides detailed output, so it's recommended to monitor the terminal if you want detailed information about its actions.
- If a crash occurs, please `create an issue <https://github.com/MontpellierRessourcesImagerie/tree-ring-analyzer/issues>`_ and include the relevant image(s) and a copy of your terminal for further investigation.
- Napari currently supports only open file formats, so make sure to convert your images to TIF format before using them with Napari.

4. Quick start
==============

.. toctree::
   :maxdepth: 1
   :caption: Features

   mga_user_guide

   
   