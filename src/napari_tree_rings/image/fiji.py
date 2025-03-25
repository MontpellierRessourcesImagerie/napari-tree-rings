import os
import abc
import imagej
import jpype
from scyjava import jimport
from napari_imagej import settings
from napari.qt.threading import create_worker



class FIJI(object):
    """
    FIJI is the base class of FIJI-commands. When creating the class, that must be used as a singleton, the jvm
    is started using napari-imagej. The path to the fiji installation must have bern set in the settings of
    napari-imagej before. Since the jvm can not be stopped nor started multiple times, napari-imagej must not
    be called in the same session in which FIJI is used.
    """


    instance = None


    def __init__(self):
        """The constructor starts the jvm and fiji via napari-imagej and
        installs the type converters from napari-imagej"""

        super(FIJI, self).__init__()
        self.imageJPath = settings.basedir()
        self.ij = imagej.init(self.getImageJPath())
        from napari_imagej.types.converters import install_converters
        install_converters()


    @classmethod
    def getAutoThresholdingMethods(cls):
        """Answer a list of names of the auto-thresholding methods available in FIJI."""

        fiji = cls.getInstance()
        AutoThresholder = jimport("ij.process.AutoThresholder")
        methods = AutoThresholder.getMethods()
        methods = [str(method) for method in methods]
        return methods


    @classmethod
    def getInstance(cls):
        """The first time the method is called, it creates a new instance of FIJI and returns it.
        All following calls will return the instance of FIJI created before."""

        if not FIJI.instance:
            FIJI.instance = FIJI()
        return FIJI.instance


    @classmethod
    def getStartUpThread(cls):
        """Return a worker, to make the creation of the jvm and the startup of FIIJ run in a parallel thread."""
        worker = create_worker(FIJI.getInstance)
        return worker


    def getImageJPath(self):
        """Answer the path to FIJI, which has been copied from the napari-imagej settings before."""

        return self.imageJPath


    def getImageJPluginsPath(self):
        """Answer the absolute path to the plugins folder of the connected FIJI installation."""

        fijiPath = self.getImageJPath()
        path = os.path.join(fijiPath, "plugins")
        return path



class FIJICommand(object):
    """Abstract base class of the FIJI-commands. Implements the management of the options of a command."""
    __metaclass__ = abc.ABCMeta


    def __init__(self):
        """The constructor starts the jvm, connects to FIJI and reads the options from the options-file of the
        command."""

        super(FIJICommand, self).__init__()
        self.fiji = FIJI.getInstance()
        self.options = self.readOptions()


    @abc.abstractmethod
    def getPluginPath(self):
        """Answer the path to the plugin subfolder, that contains the options file
        for this command. Should be overridden by subclasses"""

        return ""


    @abc.abstractmethod
    def getOptionsPath(self):
        """
        Answer the path to the options text file of the command.
        """
        return ""


    @classmethod
    def getOptionsString(cls, options):
        """Create a FIJI options string (as defined by GenericDialog) from the options dictionary of the command."""

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
        """Answer the default options of the command. If the command has options, this method should be overriden."""

        options = {}
        return options


    def readOptions(self):
        """Read the options of the command from the options file if it exists. Otherwise write an options file with
        the default options of the command first."""

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
        """Write the options passed to the method to the options file of the command."""

        optionsString = self.getOptionsString(options)
        path = self.getOptionsPath()
        with open(path, 'w') as f:
            f.write(optionsString)


    def saveOptions(self):
        """Save the options of the command to its options file."""

        self.writeOptions(self.options)



class SegmentTrunk(FIJICommand):


    def __init__(self, layer):
        """Create a segment-trunk operation, that will operate on the image of the layer passed to the constructor."""

        super(SegmentTrunk, self).__init__()
        self.layer = layer
        if layer:
            self.image = self.fiji.ij.py.to_java(layer)
            ImageJFunctions = jimport("net.imglib2.img.display.imagej.ImageJFunctions")
            self.image = ImageJFunctions.wrap(self.image, "tree")
        self.result = None


    def getPluginPath(self):
        """Answer the path to the plugin subfolder, that contains the options file
        for this command."""

        pluginPath = self.fiji.getImageJPluginsPath()
        path = os.path.join(pluginPath, "mri-tree-rings-tool")
        return path


    def getOptionsPath(self):
        """Answer the path to the options text file of the segment-trunk command.
        """
        segmentTrunkPluginPath = self.getPluginPath()
        path = os.path.join(segmentTrunkPluginPath, "tra-options.txt")
        return path


    def getRunThread(self):
        """Answer a worker that can be used to run this command in a parallel thread."""
        worker = create_worker(self.run)
        return worker


    @classmethod
    def getDefaultOptions(cls):
        """Answer the default options of the segment-trunk command."""

        options = {'scale': 8, 'sigma': 2, 'thresholding': 'Mean',
                   'opening': 16, 'closing': 8, 'stroke': 8, 'interpolation': 100,
                   'vectors': '0.7372839,0.63264143,0.23701741,0.91958255,0.35537627,0.16755785,0.69067574,0.64728355,0.3224746',
                   'bark': '0.7898954,0.5587874,0.25262988,0.5932292,0.7353205,0.3276933,0.57844025,0.5767322,0.5768768',
                   'min': 200, 'do': False}
        return options


    def run(self):
        """Read the options of the segment-trunk command, run the script-command with the read options in FIJI
        and retrieve the result image."""

        self.readOptions()
        IJ = jimport("ij.IJ")
        self.image.show()
        IJ.run(self.image, "segment trunk", self.getOptionsString(self.options))
        ids = self.fiji.ij.get("net.imagej.display.ImageDisplayService")
        view = ids.getActiveDatasetView(ids.getActiveImageDisplay())
        self.image.close()
        self.result = self.fiji.ij.py.from_java(view)

