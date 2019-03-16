import time
import cv2
import string
import threading
from collections import namedtuple

from eventkit import Event

Frame = namedtuple('Frame', ['time', 'image'])


class VideoStream(Event):
    """
    Make a video stream available as an event that emits frames::

        emit(frame)
    """
    def __init__(self, camId=0, width=640, height=480):
        Event.__init__(self)
        self._args = camId, width, height
        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def _run(self):
        camId, width, height = self._args
        if type(camId) is int or camId in string.digits:
            camId = int(camId)
            isLive = True
        else:
            isLive = camId.startswith('http://')

        capture = cv2.VideoCapture(camId)
        if capture:
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            fps = capture.get(cv2.CAP_PROP_FPS)
            while self._running:
                capture.grab()
                t = time.perf_counter()
                retval, im = capture.retrieve()
                if not retval:
                    break
                frame = Frame(t, im)
                self.emit_threadsafe(frame)
                pause = t - time.perf_counter() + 1 / fps
                if not isLive and pause > 0:
                    time.sleep(pause)
            capture.release()
        self.done_event.emit_threadsafe(self)

    def stop(self):
        self._running = False
        self._thread.join()
