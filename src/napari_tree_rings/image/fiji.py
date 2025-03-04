import os
import abc
import imagej
import jpype
from scyjava import jimport
from napari_imagej import settings
from napari.qt.threading import create_worker



class FIJI(object):

    instance = None

    def __init__(self):
        super(FIJI, self).__init__()
        self.imageJPath = settings.basedir()
        self.ij = imagej.init(self.getImageJPath())
        from napari_imagej.types.converters import install_converters
        install_converters()


    @classmethod
    def getAutoThresholdingMethods(cls):
        fiji = cls.getInstance()
        AutoThresholder = jimport("ij.process.AutoThresholder")
        methods = AutoThresholder.getMethods()
        return methods


    @classmethod
    def getInstance(cls):
        if not FIJI.instance:
            FIJI.instance = FIJI()
        return FIJI.instance


    @classmethod
    def getStartUpThread(cls):
        worker = create_worker(FIJI.getInstance)
        return worker


    def getImageJPath(self):
        return self.imageJPath


    def getImageJPluginsPath(self):
        fijiPath = self.getImageJPath()
        path = os.path.join(fijiPath, "plugins")
        return path


    @classmethod
    def shutDown(cls):
        FIJI.instance = None
        jpype.shutdownJVM()



class FIJICommand(object):
    __metaclass__ = abc.ABCMeta


    def __init__(self):
        super(FIJICommand, self).__init__()
        self.fiji = FIJI.getInstance()
        self.options = self.readOptions()


    def getPluginPath(self):
        pluginPath = self.fiji.getImageJPluginsPath()
        path = os.path.join(pluginPath, "mri-tree-rings-tool")
        return path


    @abc.abstractmethod
    def getOptionsPath(self):
        """
        Answer the path to the options text file of the command.
        """
        return ""


    @classmethod
    def getOptionsString(cls, options):
        optionsString = ""
        index = 0
        for key, value in options.items():
            if index > 0:
                optionsString = optionsString + " "
            if  not type(value) is bool:
                optionsString = optionsString + key + "=" + str(value)
            else:
                if value:
                    optionsString = optionsString + key
            index = index + 1
        return optionsString


    @classmethod
    def getDefaultOptions(cls):
        options = {}
        return options


    def readOptions(self):
        path = self.getOptionsPath()
        options = self.getDefaultOptions()
        content = ""
        if not os.path.exists(path):
            self.writeOptions(options)
        with open(path, "r") as file:
            content = file.readlines()
        lines = content[0].split(' ')
        for line in lines:
            if '=' in line:
                parts = line.split("=")
                options[parts[0]] = parts[1]
            else:
                options[line] = True
        return options


    def writeOptions(self, options):
        optionsString = self.getOptionsString(options)
        path = self.getOptionsPath()
        with open(path, 'w') as f:
            f.write(optionsString)



class SegmentTrunk(FIJICommand):


    def __init__(self, layer):
        super(SegmentTrunk, self).__init__()
        self.layer = layer
        if layer:
            self.image = self.fiji.ij.py.to_java(layer)
            ImageJFunctions = jimport("net.imglib2.img.display.imagej.ImageJFunctions")
            self.image = ImageJFunctions.wrap(self.image, "tree")
        self.result = None


    def getOptionsPath(self):
        segmentTrunkPluginPath = self.getPluginPath()
        path = os.path.join(segmentTrunkPluginPath, "tra-options.txt")
        return path


    def getRunThread(self):
        worker = create_worker(self.run)
        return worker


    @classmethod
    def getDefaultOptions(cls):
        options = {'scale': 8, 'sigma': 2, 'thresholding': 'Mean',
                   'opening': 16, 'closing': 8, 'stroke': 8, 'interpolation': 100,
                   'vectors': '0.7372839,0.63264143,0.23701741,0.91958255,0.35537627,0.16755785,0.69067574,0.64728355,0.3224746',
                   'bark': '0.7898954,0.5587874,0.25262988,0.5932292,0.7353205,0.3276933,0.57844025,0.5767322,0.5768768',
                   'min': 200, 'do': False}
        return options


    def run(self):
        IJ = jimport("ij.IJ")
        self.image.show()
        IJ.run(self.image, "segment trunk", self.getOptionsString(self.options))
        ids = self.fiji.ij.get("net.imagej.display.ImageDisplayService")
        view = ids.getActiveDatasetView(ids.getActiveImageDisplay())
        self.image.close()
        self.result = self.fiji.ij.py.from_java(view)

