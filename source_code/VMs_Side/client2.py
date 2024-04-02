from clientUtils import *
from sys import argv
from threading import Thread

class ClientSocket:

    server_ip = '127.0.0.1'
    
    @classmethod
    def connect_to_server(cls):
        # Connect to server
        cls.client = Protocol.connected_socket(cls.server_ip)
        print_colored('info', 'Client has connected to the server')
        server_msg = send_and_recv(cls.client, Messages.CLIENT)
        if server_msg != Messages.OK:
            print_colored('error', 'The server sent a message that is not OK. Exiting')
            MainApp.disconnect()
        
        # Wait for data
        while True:
            try:
                server_msg = recv(cls.client)
            except ProtocolError as e:
                print_colored('error', e)
                return
            except KeyboardInterrupt:
                print_colored('info', Messages.CTRL_C)
                cls.close()
                return
            except OSError as e:
                if e.errno == 9:    # If the recv() function was interrupted due to thread termination
                    exit(0)
            
            # Handle virus message
            print_colored('server', server_msg)
            MainApp.add_data(server_msg)

            # Confirm message to server
            send(cls.client, Messages.OK)

    @classmethod
    def close(cls):
        print_colored('client', Messages.CONNECTION_CLOSED)
        send(cls.client, Messages.CONNECTION_CLOSED)
        cls.client.close()


class GUI(QWidget):

    x = 450
    y = 300
    width = 150
    height = 100
    
    def __init__(self):
        super().__init__()

        # Initialize window
        self.setWindowTitle('Client')
        self.setGeometry(self.x, self.y, self.width, self.height)

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

        # Add label for Entry page
        entry_label = QLabel('Welcome!')
        self.entry_page.addWidget(entry_label)

        # Create 'Connect to server' button
        connect_button = QPushButton('Connect to Server')
        connect_button.clicked.connect(MainApp.connect_to_server)
        self.entry_page.addWidget(connect_button)

        # Create Exit button
        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(MainApp.exit)
        self.entry_page.addWidget(self.exit_button)

        # Add frame to main layout
        self.main_layout.addWidget(self.entry_page)


    def show_logs_page(self):
        # Remove Entry page
        self.entry_page.remove()

        # Define width and height of page
        width = 400
        height = 300

        # Create Logs page
        logs_page = Page(width, height)

        # Shape the frame
        logs_page.setFrameShape(QFrame.Shape.Box)

        # Add Label to Logs page
        label = QLabel('Virus Detection Logs:')
        logs_page.addWidget(label)

        # Add list view to Logs page
        self.list_view = ItemsList()
        logs_page.addWidget(self.list_view)

        # Create Disconnect button
        disconnect_button = QPushButton('Disconnect')
        disconnect_button.clicked.connect(MainApp.disconnect)
        logs_page.addWidget(disconnect_button)

        # Add frame to main layout
        self.main_layout.addWidget(logs_page)


    def add_data(self, data: str):
        self.list_view.addData(data)


class MainApp:

    @classmethod
    def run(cls):
        app = QApplication(argv)

        cls.gui = GUI()

        exit(app.exec())
    
    @classmethod
    def connect_to_server(cls):
        client_sock_thrd = Thread(target=ClientSocket.connect_to_server)
        client_sock_thrd.start()
        cls.gui.show_logs_page()

    @classmethod
    def disconnect(cls):
        ClientSocket.close()
        cls.exit()
    
    @classmethod
    def add_data(cls, data: str):
        cls.gui.add_data(data)
    
    @classmethod
    def exit(cls):
        print_colored('info', 'Exiting')
        exit(0)


if __name__ == '__main__':
    MainApp.run()
