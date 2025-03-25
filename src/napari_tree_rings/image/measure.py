import os
import numpy as np
from skimage.measure import regionprops_table
from napari.qt.threading import create_worker


class Measure(object):
    """Base-class for classes that measure layers."""


    def __init__(self, layer, object_type='trunk'):
        """The constructor sets the properties that will be measured on the given layer. The object_type will
        be reported in the result-measurements."""

        super(Measure, self).__init__()
        self.object_type = object_type
        self.layer = layer
        self.image = None
        self.table = None
        self.properties = ('label', 'bbox', 'perimeter', 'area', 'area_convex', "axis_major_length",
                           'axis_minor_length', 'eccentricity', 'feret_diameter_max', 'orientation')


    def do(self):
        """Execute the measurements, using regionprops from skimage and add the image name, its path, the object-type
        and the base-unit of the measurements. If for example the base-unit is µm, areas will be measured
        in µm^2"""

        self.table = regionprops_table(self.image, properties=self.properties, spacing=self.layer.scale)
        self.table["base unit"] = np.array([str(self.layer.units[0])])
        if 'parent' in self.layer.metadata.keys():
            self.table['image'] = np.array([self.layer.metadata['parent'].name])
        if 'parent_path' in self.layer.metadata.keys():
            self.table['path'] = np.array([os.path.dirname(self.layer.metadata['parent_path'])])
        else:
            self.table['image'] = np.array([self.layer.name])
        self.table["object_type"] = np.array([self.object_type])


    def addToTable(self, table):
        """Add the measurements to the table. Table is a dictionary in which the keys are the column names
        and the values (each in form of a list) are the columns"""

        if len(table.keys()) == 0:
            for key, value in self.table.items():
                    table[key] = value
            return
        for key, value in self.table.items():
            if key in table.keys():
                table[key] = np.append(table[key], [value])
        for key, value in self.table.items():
            if not key in table.keys():
                column = np.array([float('nan')] * len(list(self.table.keys())[0]))
                table[key] = np.append(column, [value])


    def getRunThread(self):
        """Answer a worker that can be used to execute the measurements in a parallel thread."""

        worker = create_worker(self.do)
        return worker



class MeasureShape(Measure):
    """Measure objects in a shape layer."""


    def __init__(self, layer, object_type='trunk'):
        """Shape layers are internally converted to label layers, before
        the features are measured."""
        super(MeasureShape, self).__init__(layer, object_type)
        if 'parent' in self.layer.metadata.keys():
            self.image = self.layer.to_labels(self.layer.metadata['parent'].data.shape[0:2])
        else:
            self.image = self.layer.to_labels()



class MeasureLabels(Measure):
    """Measure objects in a labels layer."""


    def __init__(self, layer, object_type='trunk'):
        """Labels layers can directly be used for the measurements."""

        super(MeasureLabels, self).__init__(layer, object_type='trunk')
        self.image = layer