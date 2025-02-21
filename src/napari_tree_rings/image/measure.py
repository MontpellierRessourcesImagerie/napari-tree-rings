from skimage.measure import regionprops_table



class Measure(object):

    def __init__(self, layer):
        super(Measure, self).__init__()
        self.layer = layer
        self.image = None
        self.parent = None
        self.parent = self.getParentLayer()
        self.table =None
        self.properties = ('label', 'bbox', 'perimeter', 'area', 'area_convex', "axis_major_length",
                           'axis_minor_length', 'eccentricity', 'feret_diameter_max', 'orientation')


    def getParentLayer(self):
        if self.layer.source.parent:
            return self.layer.source.parent()
        else:
            return None


    def do(self):
        self.table = regionprops_table(self.image, properties=self.properties, spacing=self.layer.scale)
        self.table['']


class MeasureShape(Measure):

    def __init__(self, layer):
        super(MeasureShape, self).__init__(layer)
        if self.parent:
            self.image = self.layer.to_labels(self.parent.data.shape[0:2])
        else:
            self.image = self.layer.to_labels()


class MeasureLabels(Measure):

    def __init__(self, layer):
        super(MeasureLabels, self).__init__(layer)
        self.image = layer