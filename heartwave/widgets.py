import PyQt5.Qt as qt

from heartwave.plot import Plot
import heartwave.util as util


class View(qt.QWidget):
    """
    Video canvas with overlay.
    """
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.image = None

    def draw(self, im, persons):
        """
        Display the CV2 image with overlay from the analysed persons.
        """
        qim = util.qImage(im)
        with qt.QPainter(qim) as p:
            for person in persons:
                x, y, w, h = person.face
                p.setPen(qt.QColor(255, 255, 255, 64))
                p.drawRect(x, y, w, h / 4)
                p.drawRect(x, y + h / 2, w, h / 4)
                font = p.font()
                font.setPixelSize(28)
                p.setFont(font)
                p.setPen(qt.QColor(255, 255, 255))
                bpm = person.bpm[-1] if len(person.bpm) else 0
                p.drawText(
                    x, y, w, h, qt.Qt.AlignHCenter, '♡' + str(int(bpm)))
        self.image = qim
        self.setMinimumSize(qim.size())
        self.update()

    def paintEvent(self, ev):
        if self.image:
            with qt.QPainter(self) as p:
                p.drawImage(0, 0, self.image)


class CurveWidget(qt.QSplitter):
    """
    Realtime curves.
    """
    def __init__(self, parent=None):
        qt.QSplitter.__init__(self, qt.Qt.Vertical, parent=parent)
        self.setMinimumHeight(640)
        self.image = None
        self.plots = [Plot(title=t) for t in (
                'Signal', 'Filtered', 'Spectrum', 'BPM')]
        for plot in self.plots:
            self.addWidget(plot)

    def plot(self, persons):
        """
        Update plots with newest data from the persons.
        """
        for plot in self.plots:
            plot.clear()
        raw, filtered, spectrum, bpm = self.plots
        for person in persons:
            raw.plot(person.corrected)
        for person in persons:
            filtered.plot(person.filtered)
        for person in persons:
            spectrum.plot(person.spectrum, x=person.freqs)
        for person in persons:
            bpm.plot(person.bpm)
            bpm.plot(person.avBpm, pen=qt.Qt.red)
