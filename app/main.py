import io
import os

import folium

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
import geopandas as gpd

from qfolium import FoliumApplication

from data import DataHandler

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

folium_app = FoliumApplication()


@folium_app.register("load_shapefile")
def load_shapefile():

    dh = DataHandler()
    m = dh.generate_map

    return m


class LeafWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent)

        self.view = QtWebEngineWidgets.QWebEngineView()

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.view)

        self.resize(640, 480)

        url = folium_app.create_url("load_shapefile")
        self.view.load(url)


def main():
    app = QtWidgets.QApplication([])
    folium_app.init_handler()
    w = LeafWidget()
    w.show()
    app.exec_()


if __name__ == "__main__":
    main()
