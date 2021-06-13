import os
import cv2
import numpy as np

from eventkit import Op

import heartwave.conf as conf


class FaceTracker(Op):
    """
    Detect and track faces::

        (frame) -> (frame, faces)
    """
    def __init__(self, source=None):
        Op.__init__(self, source)
        path = os.path.join(
            os.path.dirname(__file__),
            'data', 'lbpcascade_frontalface_improved.xml')
        self.classifier = cv2.CascadeClassifier(path)
        self.trackers = []
        self.t0 = 0.0

    def on_source(self, frame):
        t1, im = frame

        for tracker in self.trackers:
            tracker.update(t1, im)
        self.trackers = [
            t for t in self.trackers
            if t1 - t.lastTrackTime < conf.FACE_TRACKING_TIMEOUT]

        if t1 - self.t0 >= conf.FACE_DETECT_PAUSE:
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            dets = self.classifier.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5)
            faces = [
                self.scaleFace(x, y, w, h)
                for (x, y, w, h) in dets]
            for face in faces:
                x, y, w, h = face
                tracker = next(
                    (t for t in self.trackers if t.overlaps(face)), None)
                if tracker:
                    weight = 0.2 if tracker.ok else 1
                    tracker.updateROI(t1, im, face, weight)
                else:
                    tracker = Tracker(t1, im, face)
                    self.trackers.append(tracker)
            self.t0 = t1
        faces = [t.roi for t in self.trackers]
        self.emit(frame, faces)

    def scaleFace(self, x, y, w, h):
        '''
        Calculate whole face based on detected face coordinates.
        '''
        fx, fy, fw, fh = [0.5, 0.35, 1.0, 1.4]
        rw = w * fw
        rh = h * fh
        rx = x + fx * w - rw / 2
        ry = y + fy * h - rh / 2
        face = np.array([rx, ry, rw, rh], 'd')
        return face


class Tracker:
    """
    Track a region of interest in a video.
    """
    def __init__(self, t, im, roi):
        self.roi = roi
        self.updateROI(t, im, roi)

    def updateROI(self, t, im, roi, weight=0.5):
        """
        Set the new ROI as weighted average of the given ROI
        (with given weight) and old ROI.
        """
        self.lastTrackTime = self.lastRoiTime = t
        self.roi += weight * (roi - self.roi)

        Tracker = getattr(cv2, 'TrackerMedianFlow', None) or \
                  getattr(cv2, 'legacy_TrackerMedianFlow')
        self.tracker = Tracker.create()
        self.tracker.init(im, tuple(self.roi))
        self.ok = True

    def update(self, t, im):
        """
        Update ROI with new time and image.
        """
        if self.ok:
            self.ok, roi = self.tracker.update(im)
            if self.ok:
                self.roi = roi
                self.lastTrackTime = t

    def contains(self, x, y):
        """
        Is point (x, y) is contained in the ROI?
        """
        rx, ry, rw, rh = self.roi
        return rx < x < rx + rw and ry < y < ry + rh

    def overlaps(self, roi):
        """
        Does the given ROI overlap current ROI?
        """
        x0, y0, w0, h0 = self.roi
        x1, y1, w1, h1 = roi
        return (
            x0 <= x1 + w1 and x1 <= x0 + w0 and
            y0 <= y1 + h1 and y1 <= y0 + h0)
