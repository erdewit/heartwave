import asyncio
import PyQt5.Qt as qt

nan = float('nan')


def qImage(cvIm):
    """
    Create QImage from cv2 image.
    """
    h, w, ch = cvIm.shape
    qim = qt.QImage(cvIm.data, w, h, w * ch, qt.QImage.Format_RGB888)
    return qim.rgbSwapped()


def run():
    def onTimer():
        loop.call_soon(loop.stop)
        loop.run_forever()

    loop = asyncio.get_event_loop()
    timer = qt.QTimer()
    timer.start(10)
    timer.timeout.connect(onTimer)
    qt.qApp.exec_()
