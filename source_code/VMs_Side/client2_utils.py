from PyQt6.QtCore import Qt
from protocol import *
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                            QPushButton, QFrame, QLabel, QListWidget, QListWidgetItem, QLineEdit)

class BaseScreen(QFrame):

    def __init__(self, window: QWidget, shape: bool = False):
        super().__init__()

        self.main_window = window
        self.app = window.app

        self.frame_layout = QVBoxLayout()
        self.setLayout(self.frame_layout)

        if shape:
            self.setFrameShape(QFrame.Shape.Box)
        
        self.main_window.layout().addWidget(self)
    
    def add_widget(self, widg: QWidget):
        self.frame_layout.addWidget(widg)
    
    def set_size(self, width: int, height: int):
        self.main_window.setFixedSize(width, height)

    def remove(self):
        self.setParent(None)


class Screen(BaseScreen):

    def __init__(self, window: QWidget, title: str = '', size: Tuple[int, int] = (0, 0)):
        super().__init__(window, True)

        # Set title
        if title != '':
            self._set_title(title)
        
        self.w = size[0]
        self.h = size[1]

        # Set screen size
        if self.w == 0 and self.h == 0:
            self.w = self.main_window.width
            self.h = self.main_window.height
        self.set_size(self.w, self.h)


    def _set_title(self, title: str):
        self.main_window.setWindowTitle(title)

    def center(self):
        # Monitor Size
        monitor_size = self.app.primaryScreen().geometry()
        monitor_width = monitor_size.width()
        monitor_height = monitor_size.height()

        # Define x & y
        x = monitor_width // 2 - self.w // 2
        y = monitor_height // 2 - self.h // 2

        # Move the window
        self.main_window.move(x, y)


class ItemsList(QListWidget):

    def __init__(self):
        super().__init__()

        self._row = 0

    def add_data(self, data: str):
        self.insertItem(self._row, QListWidgetItem(data))
        self._row += 1


class Label(QLabel):

    def __init__(self, text: str = ''):
        super().__init__(text)


class Button(QPushButton):

    def __init__(self, text: str = '', func: Callable = None):
        super().__init__(text)

        if func != None:
            self.connect(func) 
    
    def connect(self, func: Callable):
        self.clicked.connect(func)


class InputLine(QLineEdit):

    def __init__(self, place_holder: str, initial_text: str = ''):
        super().__init__(initial_text)

        self.setPlaceholderText(place_holder)


class InputField(BaseScreen):

    def __init__(self, window: QWidget, sub_title: str, place_holder: str, initial_text: str = ''):
        super().__init__(window)
        
        self.sub_title = Label(sub_title)
        self.input = InputLine(place_holder, initial_text)

        #self.sub_title.setFixedSize(150, 100)
        #self.input.setFixedSize(150, 100)

        self.add_widget(self.sub_title)
        self.add_widget(self.input)
