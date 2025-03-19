import time
from qtpy.QtCore import  QObject, Slot
from napari.utils import progress
from napari.qt.threading import create_worker


class Progress(QObject):
    """A progress indicator for operations running in a parallel thread. The
    operation needs to connect a signal to the progressChanged method, with the
    current progress and the maximum progress value.
    """

    def __init__(self, parent, maxProgress, description):
        """Create a new progress-indicator with the given parent-widget, maximum
        progress value and description.
        """
        super().__init__(parent)
        self.progress = progress(total=maxProgress)
        self.progress.set_description(description)


    @Slot(int, int)
    def progressChanged(self, value, maxProgress):
        """Update the progress value and the max. progress value.
        """
        self.progress.update(value)
        self.progress.set_description("Processing image {} of {}".format(
                                                                value,
                                                                maxProgress))
        return True


    def processFinished(self):
        self.progress.close()



class IndeterminedProgressThread:
    """An indetermined progress indicator that moves while an operation is
    still working.
    """

    def __init__(self, description):
        """Create a new indetermined progress indicator with the given
        description.
        """
        self.worker = create_worker(self.yieldUndeterminedProgress)
        self.progress = progress(total=0)
        self.progress.set_description(description)


    def yieldUndeterminedProgress(self):
        """The progress indicator has nothing to do by himself, so just
        sleep and yield, while still running.
        """
        while True:
            time.sleep(0.05)
            yield


    def start(self):
        """Start the operation in a parallel thread"""
        self.worker.start()


    def stop(self):
        """Close the progress indicator and quite the parallel thread.
        """
        self.progress.close()
        self.worker.quit()