from protocol import *
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QLabel, QListView
from PyQt6.QtCore import QStringListModel

class Page(QFrame):

    def __init__(self):
        super().__init__()

        self.associated_widgets: List[QWidget] = []

    def associate_widget(self, widg: QWidget):
        self.associated_widgets.append(widg)

    def remove(self):
        for widg in self.associated_widgets:
            widg.setParent(None)
        self.setParent(None)


class ItemsList(QListView):

    def __init__(self):
        super().__init__()

        self.data_model = QStringListModel()
        self.data: List[str] = []
    
    def setData(self, data: List[str]):
        self.data = data
        self.data_model.setStringList(data)

    def addData(self, data: List[str]):
        self.data.extend(data)
        self.data_model.setStringList(data)