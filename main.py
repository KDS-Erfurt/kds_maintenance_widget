import json
import os
import shutil
import psutil as psutil
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox
import sys

name = "KDS-Maintenance Widget"
version = "v0.2"

default_config = "default_config.json"


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # noinspection PyUnresolvedReferences,PyProtectedMember
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.config = None
        if len(sys.argv) >= 2:
            config_path = sys.argv[1]
            if not os.path.exists(config_path):
                self.show_message_dialog("info", "Die Konfigurationsdatei wurde nicht gefunden.\n"
                                                 "Es wird eine Standardkonfiguration angelegt.", None)
                shutil.copyfile(resource_path(default_config), config_path)
            config_file = open(config_path, "r")
            self.config = json.load(config_file)
            config_file.close()

        if self.config == None:
            self.show_message_dialog("error", "Die Konfigurationsdatei wurde nicht gefunden.", sys.exit)

        if not os.path.isdir(self.config["messages_file_dir"]):
            self.show_message_dialog("error", "Das Nachrichtenverzeichniss wurde nicht gefunden.", sys.exit)

        self.username = os.environ["USERDOMAIN"] + "\\" + os.environ["USERNAME"]

        screen_resolution = app.desktop().screenGeometry()
        self.setGeometry(0, 0, screen_resolution.width(), self.config["height"])

        flags = QtCore.Qt.WindowFlags()
        flags |= QtCore.Qt.FramelessWindowHint
        flags |= QtCore.Qt.Tool

        if self.config["click_through"]:
            flags |= QtCore.Qt.WindowTransparentForInput
        if self.config["always_on_top"]:
            flags |= QtCore.Qt.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        style_sheet = "QWidget {" \
                      "background-color: " + self.config["background_color"] + "; " \
                                                                               "color: " + self.config[
                          "font_color"] + "; " \
                                          "font-size: " + self.config["font_size"] + "; " \
                                                                                     "font-family: " + self.config[
                          "font_family"] + "" \
                                           "}"
        self.setStyleSheet(style_sheet)
        self.setWindowOpacity(self.config["opacity"])

        self.messages_filenames = []
        self.messages = []
        self.current_message_count = 0

        self.moving_objects = []
        self.moving_limits = [0, screen_resolution.width()]
        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self.next_frame)
        self.frame_timer.start(self.config["frame_interval"])

        self.message_load_timer = QTimer(self)
        self.message_load_timer.timeout.connect(self.load_messages)
        self.message_load_timer.start(self.config["load_messages_interval"])

        if len(self.config["close_Processes"]) > 0:
            self.close_Processes_timer = QTimer(self)
            self.close_Processes_timer.timeout.connect(self.close_Processes)
            self.close_Processes_timer.start(self.config["close_Processes_interval"])


        self.next_frame()


    def close_Processes(self):
        for process in psutil.process_iter(['name', 'username']):
            for close_process in self.config["close_Processes"]:
                if close_process.lower() == process.name().lower():
                    if self.username == process.username():
                        return
        sys.exit(0)

    def load_messages(self):
        if os.path.exists(self.config["messages_file_dir"]):
            if os.path.isdir(self.config["messages_file_dir"]):
                entrys = os.listdir(self.config["messages_file_dir"])
                for entry in entrys:
                    entry_path = self.config["messages_file_dir"] + "\\" + entry
                    if os.path.isfile(entry_path):
                        if self.config["messages_file_postfix"] in entry:
                            if entry not in self.messages_filenames:
                                try:
                                    f = open(entry_path, "r")
                                    content = f.read()
                                    f.close()
                                    self.messages_filenames.append(entry)
                                    self.messages.append(content)
                                except:
                                    pass
                pop_list = []
                for message_filename in self.messages_filenames:
                    if message_filename not in entrys:
                        pop_list.append(self.messages_filenames.index(message_filename))
                for pop_index in pop_list:
                    self.messages_filenames.pop(pop_index)
                    self.messages.pop(pop_index)

    def show_message_dialog(self, type, message, slot):
        msg = QMessageBox()
        title = name + " - " + version + " - "
        if type == "error":
            msg.setIcon(QMessageBox.Critical)
            title += "Fehler"
        elif type == "info":
            msg.setIcon(QMessageBox.Information)
            title += "Information"
        msg.setWindowTitle(title)
        msg.setText(message)

        msg.exec_()

        if slot:
            slot()

    def next_frame(self):
        if len(self.messages) > 0:
            # show if messages available
            if self.isHidden():
                self.show()
            if len(self.moving_objects) == 0:
                self.spawn_seperator()
            else:
                last_obj = self.moving_objects[-1]
                current_pos_of_last_obj = self.moving_limits[1] - last_obj.pos().x() - last_obj.size().width()
                if current_pos_of_last_obj > self.config["space_between_messages"]:
                    if last_obj.is_seperator:
                        # if last obj a seperator then spawn messsage
                        self.spawn_message()

                    else:
                        # if not then spwan seperator
                        self.spawn_seperator()

        if len(self.messages) == 0 and len(self.moving_objects) == 0:
            # hide if no messages available
            if not self.isHidden():
                self.hide()

        if len(self.moving_objects) > 0:
            # move all objects
            pop_list = []
            for moving_object in self.moving_objects:
                current_pos = moving_object.pos().x()
                current_size = moving_object.size().width()
                if current_pos + current_size > self.moving_limits[0]:
                    moving_object.move(current_pos - self.config["steps_per_frame"], 0)
                else:
                    pop_list.append(self.moving_objects.index(moving_object))

            for pop_index in pop_list:
                self.moving_objects[pop_index].hide()
                self.moving_objects.pop(pop_index)

    def spawn_seperator(self):
        # print("spawn_seperator")
        seperator = QLabel(self)
        seperator.is_seperator = True
        seperator.setText(self.config["seperator"])
        # seperator.setStyleSheet("background-color: green;")
        seperator.move(self.moving_limits[1], 0)
        seperator.setMinimumSize(0, self.config["height"])
        seperator.show()
        self.moving_objects.append(seperator)

    def spawn_message(self):
        # print("spawn_message", self.current_message_count)
        if self.current_message_count - 1 >= len(self.messages) - 1:
            self.current_message_count = 0
        seperator = QLabel(self)
        seperator.is_seperator = False
        seperator.setText(self.messages[self.current_message_count])
        # seperator.setStyleSheet("background-color: blue;")
        seperator.move(self.moving_limits[1], 0)
        seperator.setMinimumSize(0, self.config["height"])
        seperator.show()
        self.current_message_count += 1
        self.moving_objects.append(seperator)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
