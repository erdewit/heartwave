import sys
import asyncio
import functools

import PyQt5.Qt as qt

from heartwave.widgets import View, CurveWidget
from heartwave.framegrabber import FrameGrabber
from heartwave.facetracker import FaceTracker
from heartwave.sceneanalyzer import SceneAnalyzer
import heartwave.conf as conf
import heartwave.util as util


class Window(qt.QMainWindow):

    def __init__(self):
        qt.QMainWindow.__init__(self)
        self.setWindowTitle('HeartWave')
        self.view = View(self)
        self.view.setMinimumSize(640, 480)
        self.setCentralWidget(self.view)
        self.curves = CurveWidget()
        self.curves.show()

        def addAction(menu, name, shortcut, cb):
            action = qt.QAction(name, self)
            action.setShortcut(shortcut)
            action.triggered.connect(cb)
            menu.addAction(action)
        menu = self.menuBar()
        fileMenu = menu.addMenu('Source')
        camMenu = fileMenu.addMenu('Camera')
        addAction(fileMenu, 'File', 'Ctrl-F', self.onOpenFile)
        addAction(fileMenu, 'URL', 'Ctrl-U', self.onOpenURL)
        addAction(fileMenu, 'Exit', 'Esc', self.close)
        for i in range(10):
            addAction(camMenu, str(i), '', functools.partial(self.onCamera, i))
        addAction(menu, 'Snapshot', 'Space', self.onSnapshot)
        addAction(menu, 'Toggle curves', 'T', self.onToggleCurves)

        self.pipe = None
        self.running = False
        self.start()

    def onOpenFile(self):
        path, _filter = qt.QFileDialog.getOpenFileName(self)
        self.stop()
        conf.CAM_ID = path
        self.start()

    def onOpenURL(self):
        print('TBD')

    def onCamera(self, camId):
        self.stop()
        conf.CAM_ID = camId
        self.start()

    def onSnapshot(self):
        print('TBD')

    def onToggleCurves(self):
        self.curves.setVisible(not self.curves.isVisible())

    def start(self):
        self.running = True
        self.pipe = asyncio.ensure_future(self.pipeline())

    def stop(self):
        self.running = False
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.pipe)
        self.pipe = None

    def closeEvent(self, ev):
        self.stop()
        self.curves.close()

    async def pipeline(self):
        """
        Video capture- and processing pipeline that runs asynchronously
        alongside the GUI.
        """
        self.running = True
        async with \
                FrameGrabber(conf.CAM_ID) as grabber, \
                FaceTracker() as tracker, \
                SceneAnalyzer() as analyzer:
            async for frame in grabber:
                if not self.running:
                    break
                tracker.feed(frame)
                if tracker.hasOutput():
                    frame, faces = await tracker
                    analyzer.feed((frame, faces))
                    if analyzer.hasOutput():
                        frame, faces, persons = await analyzer
                        # skip drawing if lagging behind
                        if not grabber.hasOutput():
                            self.view.draw(frame.image, persons)
                            if self.curves.isVisible():
                                self.curves.plot(persons)


def main():
    if len(sys.argv) > 1:
        conf.CAM_ID = sys.argv[1]
    qApp = qt.QApplication(sys.argv)  # noqa
    win = Window()
    win.show()
    util.run()


if __name__ == '__main__':
    main()
