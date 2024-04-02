from protocol import *
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QLabel, QListWidget, QListWidgetItem

class Page(QFrame):

    def __init__(self, width: int = 0, height: int = 0):
        super().__init__()

        # Create layout for frame
        self.frame_layout = QVBoxLayout()
        self.setLayout(self.frame_layout)

        # Change size if arguments were given
        if width > 0 and height > 0:
            self.setFixedSize(width, height)

    def addWidget(self, widg: QWidget):
        self.frame_layout.addWidget(widg)

    def remove(self):
        self.setParent(None)


class ItemsList(QListWidget):

    def __init__(self):
        super().__init__()

        self.row_num = 0

    def addData(self, data: str):
        self.insertItem(self.row_num, QListWidgetItem(data))
        self.row_num += 1
