import io
import os

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class LeafWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.view = QtWebEngineWidgets.QWebEngineView()

        shp_filename = os.path.join(CURRENT_DIR, "input", "2015_loaded_NoCC.shp")
        shp_file = gpd.read_file(shp_filename)
        shp_file_json_str = shp_file.to_json()

        m = folium.Map(location=[40, -120], zoom_start=10)
        folium.GeoJson(shp_file_json_str).add_to(m)

        tmp_file = QtCore.QTemporaryFile("XXXXXX.html", self)
        if tmp_file.open():
            m.save(tmp_file.fileName())
            url = QtCore.QUrl.fromLocalFile(tmp_file.fileName())
            self.view.load(url)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.view)


def main():
    app = QtWidgets.QApplication([])
    w = LeafWidget()
    w.show()
    app.exec_()


if __name__ == "__main__":
    main()
