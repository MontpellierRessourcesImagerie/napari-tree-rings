import numpy as np
from skimage.measure import regionprops_table
from napari.qt.threading import create_worker


class Measure(object):

    def __init__(self, layer, object_type='trunk'):
        super(Measure, self).__init__()
        self.object_type = object_type
        self.layer = layer
        self.image = None
        self.table = None
        self.properties = ('label', 'bbox', 'perimeter', 'area', 'area_convex', "axis_major_length",
                           'axis_minor_length', 'eccentricity', 'feret_diameter_max', 'orientation')


    def do(self):
        self.table = regionprops_table(self.image, properties=self.properties, spacing=self.layer.scale)
        self.table["base unit"] = np.array([str(self.layer.units[0])])
        if 'parent' in self.layer.metadata.keys():
            self.table['image'] = np.array([self.layer.metadata['parent'].name])
        if 'parent_path' in self.layer.metadata.keys():
            self.table['path'] = np.array([self.layer.metadata['parent_path']])
        else:
            self.table['image'] = np.array([self.layer.name])
        self.table["object_type"] = np.array([self.object_type])


    def addToTable(self, table):
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
        worker = create_worker(self.do)
        return worker



class MeasureShape(Measure):

    def __init__(self, layer, object_type='trunk'):
        super(MeasureShape, self).__init__(layer, object_type)
        if 'parent' in self.layer.metadata.keys():
            self.image = self.layer.to_labels(self.layer.metadata['parent'].data.shape[0:2])
        else:
            self.image = self.layer.to_labels()



class MeasureLabels(Measure):

    def __init__(self, layer, object_type='trunk'):
        super(MeasureLabels, self).__init__(layer, object_type='trunk')
        self.image = layer