import json

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget
import sys

config_file_path = "config.json"

class Window(QWidget):
    def __init__(self, dimmensions):
        QWidget.__init__(self)
        screen_resolution = app.desktop().screenGeometry()
        self.setGeometry(0, 0, screen_resolution.width(), config["height"])


        flags = QtCore.Qt.WindowFlags()
        flags |= QtCore.Qt.FramelessWindowHint
        flags |= QtCore.Qt.Tool

        if config["click_through"]:
            flags |= QtCore.Qt.WindowTransparentForInput
        if config["always_on_top"]:
            flags |= QtCore.Qt.WindowStaysOnTopHint




        self.setWindowFlags(flags)
        style_sheet = "background-color: " + config["background_color"] + ";" \
                      "bo"
        self.setStyleSheet("background-color: " + config["background_color"] + ";")
        self.setWindowOpacity(config["opacity"])

        self.show()



if __name__ == "__main__":
    config_file = open(config_file_path, "r")
    config = json.load(config_file)
    config_file.close()
    print(config)

    app = QApplication(sys.argv)
    window = Window(config)
    sys.exit(app.exec())