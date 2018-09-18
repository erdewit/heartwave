import math
import time
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


def formatSI(n):
    """
    Format the integer or float n to 3 significant digits + SI prefix.
    """
    s = ''
    if n < 0:
        n = -n
        s += '-'
    if type(n) is int and n < 1000:
        s = str(n) + ' '
    elif n < 1e-22:
        s = '0.00 '
    else:
        assert n < 9.99e26
        log = int(math.floor(math.log10(n)))
        i, j = divmod(log, 3)
        for _try in range(2):
            templ = '%.{}f'.format(2 - j)
            val = templ % (n * 10 ** (-3 * i))
            if val != '1000':
                break
            i += 1
            j = 0
        s += val + ' '
        if i != 0:
            s += 'yzafpnum kMGTPEZY'[i + 8]
    return s


class timeit:
    """
    Context manager for timing.
    """
    def __init__(self, title='Run'):
        self.title = title

    def __enter__(self):
        self.t0 = time.time()

    def __exit__(self, *_args):
        t = time.time() - self.t0
        print(self.title + ' took ' + formatSI(t) + 's')
