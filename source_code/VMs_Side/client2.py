from protocol import *
from clientUtils import *
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
            server_msg = recv(client)
            print_colored('server', server_msg)


class GUI(QWidget):
    
    def __init__(self):
        super().__init__()

        # Initialize window
        self.setWindowTitle('Client')
        self.setGeometry(450, 300, 250, 100)

        # Create window layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Show Entry Page
        self.show_entry_page()

        # Show screen
        self.show()


    def show_entry_page(self):
        # Create Entry page
        self.entry_page = Page()

        # Shape the frame
        self.entry_page.setFrameShape(QFrame.Shape.Box)
        self.entry_page.setLineWidth(3)

        # Create layout for the frame
        entry_page_layout = QVBoxLayout()
        self.entry_page.setLayout(entry_page_layout)

        # Add label for Entry page
        entry_label = QLabel('Welcome!')
        self.main_layout.addWidget(entry_label)
        self.entry_page.associate_widget(entry_label)

        # Create 'Connect to server' button
        connect_button = QPushButton('Connect to Server')
        connect_button.clicked.connect(MainApp.connect_to_server)

        # Add button to layout
        entry_page_layout.addWidget(connect_button)

        # Add frame to main layout
        self.main_layout.addWidget(self.entry_page)

    def show_logs_page(self):
        # Remove Entry page
        self.entry_page.remove()

        # Create Logs page
        logs_page = Page()

        # Shape the frame
        logs_page.setFrameShape(QFrame.Shape.Box)
        logs_page.setLineWidth(3)

        # Create layout for frame
        logs_page_layout = QVBoxLayout()
        logs_page.setLayout(logs_page_layout)

        # Add Label to Logs page
        label = QLabel('Virus Detection Logs:')
        self.main_layout.addWidget(label)

        # Add list view to Logs page
        list_view = ItemsList()
        logs_page_layout.addWidget(list_view)

        # Add frame to main layout
        self.main_layout.addWidget(logs_page)


class MainApp:

    @classmethod
    def run(cls):
        app = QApplication(argv)

        cls.gui = GUI()

        exit(app.exec())
    
    @classmethod
    def connect_to_server(cls):
        Client.connect_to_server()
        cls.gui.show_logs_page()


if __name__ == '__main__':
    MainApp.run()
