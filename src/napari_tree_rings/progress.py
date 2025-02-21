import time
from napari.utils import progress
from napari.qt.threading import create_worker



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