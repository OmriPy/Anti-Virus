from protocol import *
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QLabel, QListWidget

class Page(QFrame):

    def __init__(self):
        super().__init__()

    def remove(self):
        self.setParent(None)


class ItemsList(QListWidget):

    def __init__(self):
        super().__init__()

        

    def addData(self, data: str):
        pass
