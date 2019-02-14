import PyQt5.Qt as qt
import PyQt5.QtChart as qc


class Plot(qc.QChartView):

    def __init__(self, parent=None, title=''):
        qc.QChartView.__init__(self, parent)
        chart = qc.QChart()
        chart.legend().hide()
        chart.setTitle(title)
        chart.setMargins(qt.QMargins(0, 0, 0, 0))
        self.setChart(chart)
        self.setRenderHint(qt.QPainter.Antialiasing)

    def plot(self, y, x=None, pen=None, autoAxes=True):
        sz = len(y)
        if not sz:
            return
        if x is None:
            x = range(sz)
        elif len(x) != sz:
            raise ValueError('x and y arrays must be the same length')

        series = qc.QLineSeries()
        append = series.append
        for c in zip(x, y):
            append(*c)
        if pen:
            series.setPen(pen)
        chart = self.chart()
        chart.addSeries(series)
        if autoAxes:
            chart.createDefaultAxes()
        else:
            for axis in chart.axes():
                series.attachAxis(axis)

    def clear(self):
        self.chart().removeAllSeries()
