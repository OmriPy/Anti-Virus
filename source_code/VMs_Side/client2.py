from protocol import *
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from sys import argv

class Client:

    server_ip = '127.0.0.1'
    
    @classmethod
    def connect_to_server(cls):
        with Protocol.connected_socket(cls.server_ip) as client:
            print_colored('info', 'Client has connected to the server')
            server_msg = send_and_recv(client, Messages.CLIENT)
            if server_msg != Messages.OK:
                print_colored('error', 'The server sent a message that is not OK. Exiting')
                exit(1)


class GUI(QWidget):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Client')

        layout = QVBoxLayout()
        self.setLayout(layout)

        connect_button = QPushButton('Connect to Server')
        connect_button.clicked.connect(MainApp.connect_to_server)
        layout.addWidget(connect_button)

    def remove_layout(self):
        if self.layout() is not None:
            while self.layout().count():
                item = self.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.layout().deleteLater()

    def show_logs(self):
        self.remove_layout()
        layout = QVBoxLayout()
        self.setLayout(layout)


class MainApp:

    @classmethod
    def run(cls):
        app = QApplication(argv)

        cls.gui = GUI()
        cls.gui.show()

        exit(app.exec())
    
    @classmethod
    def connect_to_server(cls):
        Client.connect_to_server()
        cls.gui.show_logs()


if __name__ == '__main__':
    MainApp.run()