======================
Measures on Tree Rings
======================

- The measurements will be automatically exported in CSV file after segmentation.
- The unit will be taken directly from TIF file (if available). Otherwise, it will be pixel.
- The measures include:

+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| Column            | Description                                                                                                                            |
+===================+========================================================================================================================================+
| bbox              | The bounding box's minimum and maximum coordinates on the horizontal and vertical axes.                                                |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| area              | Region's area.                                                                                                                         |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| area_convex       | Area of the convex hull image, which is the smallest convex polygon enclosing the region.                                              |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| axis_major_length | Length of the ring boundaries' major axis.                                                                                             |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| axis_minor_length | Length of the ring boundaries' minor axis.                                                                                             |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| eccentricity      | The eccentricity, which ranges from 0 to 1, is the focal distance divided by the major axis length. When the eccentricity is zero, the |
|                   | region becomes a circle.                                                                                                               |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| feret_diameter_max| The maximum Feret's diameter, which is the largest distance between points across the convex hull.                                     |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| orientation       | Angle between the major axis and the vertical axis, measured in radians and ranging from -pi/2 to pi/2 anticlockwise.                  |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| area_growth       | The area between the two ring boundaries that experiences growth over a year (except the cases of pith and bark).                      |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+

- If you would like to add other measurements while running batch, you can modify `BatchSegmentTrunk.run` in the src/napari_tree_rings/image/process.py. There is an example of `area_growth` for you to see and refer to.