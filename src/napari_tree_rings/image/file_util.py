from tifffile import TiffFile
from napari.qt.threading import create_worker


class TiffFileTags:


    def __init__(self, path):
        self.pixelSize = 1
        self.unit = "pixel"
        self.path = path


    def getPixelSizeAndUnit(self):
        with TiffFile(self.path) as tif:
            tags = tif.pages[0].tags
        if not 282 in tags.keys():
            return
        else:
            self.pixelSize = tags['XResolution'].value[1] / tags['XResolution'].value[0]
        if not 270 in tags.keys():
            return
        else:
            tag = tags['ImageDescription'].value
            parts = tag.split("\n")
            if len(parts) <2 :
                return
            self.unit = parts[1].split("=")[1]
            if self.unit=='mkm':
                self.unit = "µm"


    def getPixelSizeAndUnitWorker(self):
        worker = create_worker(self.getPixelSizeAndUnit)
        return worker
