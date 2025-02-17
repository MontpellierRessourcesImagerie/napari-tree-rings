import os
from napari_imagej import settings

class FIJI(object):

    instance = None

    def __init__(self):
        self.imageJPath = settings.basedir()


    def getImageJPath(self):
        return self.imageJPath


    def getImageJPluginsPath(self):
        fijiPath = self.getImageJPath()
        path = os.path.join(fijiPath, "plugins")
        return path


    def getSegmentTrunkPluginPath(self):
        pluginPath = self.getImageJPluginsPath()
        path = os.path.join(pluginPath, "mri-tree-rings-tool")
        return path


    def getSegmentTrunkOptionsPath(self):
        segmentTrunkPluginPath = self.getSegmentTrunkPluginPath()
        path = os.path.join(segmentTrunkPluginPath, "tra-options.txt")
        return path


    @classmethod
    def getDefaultSegmentTrunkOptions(cls):
        options = {'scale': 8, 'sigma': 2, 'thresholding': 'Mean',
                   'opening': 16, 'closing': 8, 'stroke': 8, 'interpolation': 100,
                   'vectors': '0.7372839,0.63264143,0.23701741,0.91958255,0.35537627,0.16755785,0.69067574,0.64728355,0.3224746',
                   'bark': '0.7898954,0.5587874,0.25262988,0.5932292,0.7353205,0.3276933,0.57844025,0.5767322,0.5768768',
                   'min': 200, 'do': False}
        return options


    @classmethod
    def getSegmentTrunkOptionsString(cls, options):
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


    def writeSegmentTrunkOptions(self, options):
        optionsString = self.getSegmentTrunkOptionsString(options)
        path = self.getSegmentTrunkOptionsPath()
        with open(path, 'w') as f:
            f.write(optionsString)


    def readSegmentTrunkOptions(self):
        path = self.getSegmentTrunkOptionsPath()
        options = self.getDefaultSegmentTrunkOptions()
        content = ""
        if not os.path.exists(path):
            self.writeSegmentTrunkOptions(options)
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



