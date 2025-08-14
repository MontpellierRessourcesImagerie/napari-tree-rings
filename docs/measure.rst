======================
Measures on Tree Rings
======================

- The measurements will be automatically exported in CSV file after segmentation.
- The unit will be taken directly from TIF file (if available). Otherwise, it will be pixel.
- The measures include:

+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| Column            | Description                                                                                                                            |
+===================+========================================================================================================================================+
| bbox              | The bounding box's minimum and maximum coordinates on the horizontal and vertical axes make up the calculated parameters.              |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| area              | Region's area.                                                                                                                         |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| area_convex       | Area of the convex hull image, which is the smallest convex polygon enclosing the region.                                              |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| axis_major_length | Length of the ring borders' main axis.                                                                                                 |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| axis_minor_length | Length of the ring borders' minor axis.                                                                                                |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| eccentricity      | The eccentricity, which ranges from 0 to 1, is the focal distance divided by the major axis length. When the maximum Feret's diameter, |
|                   | which is the largest distance between points across the convex hull, is zero, the region becomes a circle.                             |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| orientation       | Angle, measured in radians and ranging from -pi/2 to pi/2 anticlockwise, between the main axis and the vertical axis.                  |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+
| area_growth       | The area between the two ring boundaries that experiences growth over the course of a year.                                            |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------+