from protocol import *
import PyQt6.QtWidgets as qtw
from threading import Thread

class Window(qtw.QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('hElLo ThErE aSaF') # set title
        self.setLayout(qtw.QVBoxLayout()) # set layout
        self.data_label = qtw.QLabel('hi') # create label
        self.layout().addWidget(self.data_label) # adding the label to the layout

        self.button = qtw.QPushButton('Press!')
        self.button.setCheckable(True)
        self.button.clicked.connect(self.button_clicked)
        self.layout().addWidget(self.button)

        self.list_view = qtw.QListView()
        self.layout().addWidget(self.list_view)

        self.show()

    def change_text(self, text: str):
        self.data_label.setText(text)

    def button_clicked(self):
        print('The button was clicked!')


def client(window: Window):
    with connected_socket('127.0.0.1') as client:
        try:
            data = recv(client)
        except ProtocolError as e:
            print(e)
            return
        window.change_text(data)

if __name__ == '__main__':
    app = qtw.QApplication([])
    window = Window()
    
    thrd = Thread(target=client, args=(window,))
    thrd.start()
    
    app.exec()