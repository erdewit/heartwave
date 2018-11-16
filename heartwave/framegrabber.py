import time
import cv2
import string
from collections import namedtuple

from heartwave.runqueue import RunQueue


Frame = namedtuple('Frame', ['time', 'image'])


class FrameGrabber(RunQueue):
    """
    Make a video stream available as a series of frames.

    Input: -
    Output: frame
    """
    def __init__(self, camId=0, width=640, height=480):
        RunQueue.__init__(self)
        self._args = camId, width, height

    def run(self):
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
            while self.running:
                capture.grab()
                t = time.perf_counter()
                retval, im = capture.retrieve()
                if not retval:
                    break
                frame = Frame(t, im)
                self.output(frame)
                pause = t - time.perf_counter() + 1 / fps
                if not isLive and pause > 0:
                    time.sleep(pause)
            capture.release()
            print('stop', self.running)
        self.output(RunQueue.Stop)
