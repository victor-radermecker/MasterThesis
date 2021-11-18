import numpy as np
import plotly.graph_objs as go

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

from qtplotly import PlotlyApplication

# PlotlyApplication must be created before the creation
# of QGuiApplication or QApplication
plotly_app = PlotlyApplication()


@plotly_app.register("scatter")
def scatter():
    t = np.arange(0, 200000, 1)
    y = np.sin(t / 20000)
    fig = go.Figure(data=[{"type": "scattergl", "y": y}])
    return fig


@plotly_app.register("scatter2")
def scatter2():
    N = 100000
    r = np.random.uniform(0, 1, N)
    theta = np.random.uniform(0, 2 * np.pi, N)

    fig = go.Figure(
        data=[
            {
                "type": "scattergl",
                "x": r * np.cos(theta),
                "y": r * np.sin(theta),
                "marker": dict(color=np.random.randn(N), colorscale="Viridis"),
            }
        ]
    )
    return fig


@plotly_app.register("scatter3")
def scatter3():
    x0 = np.random.normal(2, 0.45, 30000)
    y0 = np.random.normal(2, 0.45, 30000)

    x1 = np.random.normal(6, 0.4, 20000)
    y1 = np.random.normal(6, 0.4, 20000)

    x2 = np.random.normal(4, 0.3, 20000)
    y2 = np.random.normal(4, 0.3, 20000)

    traces = []
    for x, y in ((x0, y0), (x1, y1), (x2, y2)):
        trace = go.Scatter(x=x, y=y, mode="markers")
        traces.append(trace)

    fig = go.Figure(data=traces)
    return fig


class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.m_view = QtWebEngineWidgets.QWebEngineView()

        combobox = QtWidgets.QComboBox()
        combobox.currentIndexChanged[str].connect(self.onCurrentIndexChanged)
        combobox.addItems(["scatter", "scatter2", "scatter3"])

        vlay = QtWidgets.QVBoxLayout(self)
        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(QtWidgets.QLabel("Select:"))
        hlay.addWidget(combobox)
        vlay.addLayout(hlay)
        vlay.addWidget(self.m_view)
        self.resize(640, 480)

    @QtCore.pyqtSlot(str)
    def onCurrentIndexChanged(self, name):
        self.m_view.load(plotly_app.create_url(name))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    # Init_handler must be invoked before after the creation
    # of QGuiApplication or QApplication
    plotly_app.init_handler()
    w = Widget()
    w.show()
    sys.exit(app.exec_())
