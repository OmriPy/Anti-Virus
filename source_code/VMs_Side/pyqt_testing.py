import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QTextEdit
import socket
import threading

class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Socket Client")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        self.label = QLabel("Enter server IP and port:")
        layout.addWidget(self.label)

        self.server_ip_entry = QLineEdit()
        layout.addWidget(self.server_ip_entry)

        self.server_port_entry = QLineEdit()
        layout.addWidget(self.server_port_entry)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_button)

        self.chat_display = QTextEdit()
        layout.addWidget(self.chat_display)

        self.message_entry = QLineEdit()
        layout.addWidget(self.message_entry)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.client_socket = None

    def connect_to_server(self):
        server_ip = self.server_ip_entry.text()
        server_port = int(self.server_port_entry.text())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, server_port))

        # Start a new thread to receive messages from the server
        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                self.chat_display.append(message)
            except ConnectionAbortedError:
                break

    def send_message(self):
        message = self.message_entry.text()
        if message:
            self.client_socket.send(message.encode())
            self.message_entry.clear()

def main():
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()