from protocol import *
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QLabel, QListWidget, QListWidgetItem

class Screen(QFrame):

    def __init__(self, window: QWidget, width: int = 0, height: int = 0):
        super().__init__()

        self.main_window = window
        self.app = window.app

        # Create layout for frame
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Set screen size
        if width == 0 and height == 0:
            width = self.main_window.width
            height = self.main_window.height
        self.set_size(width, height)

    def set_size(self, width: int, height: int):
        self.setFixedSize(width, height)

    def center(self):
        # Screen size
        screen_width = self.width()
        screen_height = self.height()

        # App Size
        app_size = self.main_window.app.primaryScreen().geometry()
        app_width = app_size.width()
        app_height = app_size.height()

        # Define x & y
        x = app_width // 2 - screen_width // 2
        y = app_height // 2 - screen_height // 2

        # Move the window
        self.main_window.move(x, y)

    def add_widget(self, widg: QWidget):
        self.layout.addWidget(widg)

    def remove(self):
        self.setParent(None)


class ItemsList(QListWidget):

    def __init__(self):
        super().__init__()

        self.row_num = 0

    def add_data(self, data: str):
        self.insertItem(self.row_num, QListWidgetItem(data))
        self.row_num += 1
