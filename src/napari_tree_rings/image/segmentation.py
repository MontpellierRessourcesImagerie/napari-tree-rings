import os
import appdirs
import abc

from napari.layers import Shapes
from napari.qt.threading import create_worker
from skimage import measure
from skimage.transform import rescale, resize
from scipy.ndimage import gaussian_filter
from skimage.filters import threshold_mean
from skimage.color import rgb2gray
from scipy.ndimage import binary_fill_holes
from skimage import morphology
import cv2
import numpy as np
from shapelysmooth import taubin_smooth
from skimage.morphology import convex_hull_image


class Operation(object):
    """Abstract base class of the FIJI-commands. Implements the management of the options of a command."""
    __metaclass__ = abc.ABCMeta


    def __init__(self):
        """The constructor starts the jvm, connects to FIJI and reads the options from the options-file of the
        command."""

        super(Operation, self).__init__()
        self.options = self.readOptions()


    @abc.abstractmethod
    def getProjectPath(self):
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

        default = self.getDefaultOptions()
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
                options[parts[0].strip()] = type(default[parts[0].strip()])(parts[1].strip())
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



class SegmentTrunk(Operation):


    def __init__(self, layer):
        """Create a segment-trunk operation, that will operate on the image of the layer passed to the constructor."""

        super(SegmentTrunk, self).__init__()
        self.layer = layer
        self.result = None


    def getOptionsPath(self):
        """Answer the path to the options text file of the segment-trunk command.
        """
        path = appdirs.user_data_dir("napari-tree-rings")
        if (not os.path.exists(path)):
            os.makedirs(path)
        optionsPath = os.path.join(path, "options.txt")
        return optionsPath


    def getRunThread(self):
        """Answer a worker that can be used to run this command in a parallel thread."""
        worker = create_worker(self.run)
        return worker


    @classmethod
    def getDefaultOptions(cls):
        """Answer the default options of the segment-trunk command."""

        options = {'scale': 8, 'opening': 96}
        return options


    def run(self):
        """Read the options of the segment-trunk command, run the script-command with the read options in FIJI
        and retrieve the result image."""

        self.options = self.readOptions()
        image = self.layer.data
        if len(image.shape) == 3 and image.shape[-1] == 3:
            image = rgb2gray(image)
        elif len(image.shape) == 3 and image.shape[-1] == 1:
            image = image[:, :, 0]
        small = rescale(image, 1.0 / self.options['scale'], anti_aliasing=True)
        small = np.squeeze(small)
        thresh = threshold_mean(small)
        binary = (small < thresh) * 255
        largest = self.keep_largest_region(binary)
        filled = binary_fill_holes(largest) * 255
        se = morphology.disk(self.options['opening'])
        opened = morphology.binary.binary_opening(filled, se)
        if len(np.unique(opened)) == 1:
            opened = filled / 255
        out = resize(opened, (image.shape[0], image.shape[1])) * 1
        out = out * 255
        out = out.astype(np.uint8)
        se2 = morphology.disk(self.options['scale'])
        out = morphology.binary_erosion(out, se2)
        chull = convex_hull_image(out)
        chull = chull * 255
        chull = chull.astype(np.uint8)
        contours, hierarchy = cv2.findContours(chull, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        polys = [np.squeeze(e) for e in contours[0]]
        changed = [np.array([y, x]) for x, y in polys]
        smoothed = [np.array(taubin_smooth(changed))]
        self.result = Shapes(smoothed, shape_type='polygon')


    @classmethod
    def keep_largest_region(cls, input_mask):
        labels_mask = measure.label(input_mask)
        regions = measure.regionprops(labels_mask)
        regions.sort(key=lambda x: x.area, reverse=True)
        if len(regions) > 1:
            for rg in regions[1:]:
                labels_mask[rg.coords[:, 0], rg.coords[:, 1]] = 0
        labels_mask[labels_mask != 0] = 1
        mask = labels_mask
        return mask