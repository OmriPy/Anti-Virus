from protocol import *
from PyQt6.QtWidgets import \
    QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QLabel, \
    QListWidget, QListWidgetItem, QLineEdit,QSizePolicy, QMessageBox
from PyQt6.QtCore import Qt


class BaseScreen(QFrame):

    def __init__(self, window: QWidget, shape: bool = False):
        super().__init__()

        self.main_window = window
        self.app: QApplication = window.app

        self.frame_layout = QVBoxLayout()
        self.setLayout(self.frame_layout)

        if shape:
            self.setFrameShape(QFrame.Shape.Box)
        
        self.main_window.layout().addWidget(self)

    def add_widget(self, widg: QWidget, center: bool = False):
        self.frame_layout.addWidget(widg)
        if center:
            self.frame_layout.setAlignment(widg, Qt.AlignmentFlag.AlignHCenter)

    def set_size(self, width: int, height: int):
        self.main_window.setFixedSize(width, height)

    def remove(self):
        self.setParent(None)


class Screen(BaseScreen):

    def __init__(self,
                 window: QWidget,
                 title: str = '',
                 size: Tuple[int, int] = (0, 0,)):
        """Object used to represent a screen"""
        
        super().__init__(window, True)

        # Set title
        if title != '':
            self._set_title(title)
        
        self.w, self.h = size

        # Set screen size
        if self.w == 0 and self.h == 0:
            self.w = self.main_window.width
            self.h = self.main_window.height
        self.set_size(self.w, self.h)


    def _set_title(self, title: str):
        self.main_window.setWindowTitle(title)

    def center(self):
        """Places the screen to be exactly at the center of your monitor"""

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

    def __init__(self, text: str = '', func: Optional[Callable] = None):
        super().__init__(text)

        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        if func:
            self.connect(func)
    
    def connect(self, func: Callable):
        self.clicked.connect(func)


class InputLine(QLineEdit):

    def __init__(self, place_holder: str, hide: bool, initial_text: str):
        super().__init__(initial_text)

        self.setPlaceholderText(place_holder)
        if hide:
            self.setEchoMode(QLineEdit.EchoMode.Password)


class InputField(BaseScreen):

    def __init__(self,
                 window: QWidget,
                 sub_title: str,
                 place_holder: Optional[str] = None,
                 hide: bool = False,
                 initial_text: str = ''):
        """Object containing a Label and InputLine variable, represnting a field that asks for input"""

        super().__init__(window)

        place_holder = place_holder or f'Enter your {sub_title.lower()} here'
        sub_title = f'{sub_title}:'
        self.sub_title = Label(sub_title)
        self.input_line = InputLine(place_holder, hide, initial_text)

        self.setStyleSheet('padding: 0.25em 0.1em;')

        self.add_widget(self.sub_title)
        self.add_widget(self.input_line)
    
    def text(self) -> str:
        return self.input_line.text()


class PopUp(QMessageBox):

    INFO = 1
    QUESTION = 2
    WARNING = 3
    CRITICAL = 4

    ICONS: Dict[int, QMessageBox.Icon] = {
        INFO: QMessageBox.Icon.Information,
        QUESTION: QMessageBox.Icon.Question,
        WARNING: QMessageBox.Icon.Warning,
        CRITICAL: QMessageBox.Icon.Critical
    }

    def __init__(self, text: str, type: int):
        super().__init__()

        self.setText(text)
        self.setIcon(self.ICONS[type])
    
    def show(self):
        self.exec()
