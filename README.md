# napari-tree-rings

[![License MIT](https://img.shields.io/pypi/l/napari-tree-rings.svg?color=green)](https://github.com/MontpellierRessourcesImagerie/napari-tree-rings/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-tree-rings.svg?color=green)](https://pypi.org/project/napari-tree-rings)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-tree-rings.svg?color=green)](https://python.org)
[![tests](https://github.com/MontpellierRessourcesImagerie/napari-tree-rings/workflows/tests/badge.svg)](https://github.com/MontpellierRessourcesImagerie/napari-tree-rings/actions)
[![codecov](https://codecov.io/gh/MontpellierRessourcesImagerie/napari-tree-rings/branch/main/graph/badge.svg)](https://codecov.io/gh/MontpellierRessourcesImagerie/napari-tree-rings)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-tree-rings)](https://napari-hub.org/plugins/napari-tree-rings)

A tool to delineate bark, pith and xylem annual rings and to measure their property parameters on circular sections of tree trunks.

----------------------------------

This [napari] plugin was generated with [copier] using the [napari-plugin-template].

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/napari-plugin-template#getting-started

and review the napari docs for plugin developers:
https://napari.org/stable/plugins/index.html
-->

## How to use it?
Users can export the segmentation findings and estimate bark, ring borders, and pith with ease using the Napari Tree Rings plugin:
- Run button on the Segment Rings tag: find the rings in just one image.
- Run Batch button on the Batch Segment Trunk tag: runs all the images in the folder. 

Users can also modify certain parameters, including the batch size. The interface's goal is to assist biologists without having programming expertise by being user-friendly.

If accessible, the unit of micrometres will be used to determine the parameters; if not, pixels will be used. The calculated parameters are made up of:
- bbox: The bounding box’s minimum and maximum coordinates on the horizontal and vertical axes.
- area: Region’s area.
- area_convex: Area of the convex hull image, which is the smallest convex polygon enclosing the region.
- axis_major_length: Length of the ring boundaries’ major axis.
- axis_minor_length: Length of the ring boundaries’ minor axis.
- eccentricity: The eccentricity, which ranges from 0 to 1, is the focal distance divided by the major axis length. When the eccentricity is zero, the region becomes a circle.
- orientation: Angle between the major axis and the vertical axis, measured in radians and ranging from -pi/2 to pi/2 anticlockwise.
- area_growth: The area between the two ring boundaries that experiences growth over a year (except the cases of pith and bark).

## Installation

You can install `napari-tree-rings` via [pip]:

    pip install napari-tree-rings


## Adding other measurements
If you would like to add other measurements while running batch, you can modify `BatchSegmentTrunk.run` in the `src/napari_tree_rings/image/process.py`. There is an example of `area_growth` for you to see and refer to.


## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"napari-tree-rings" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[copier]: https://copier.readthedocs.io/en/stable/
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[napari-plugin-template]: https://github.com/napari/napari-plugin-template

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
