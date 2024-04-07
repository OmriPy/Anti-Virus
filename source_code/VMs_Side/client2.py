from client2_utils import *
from sys import argv
from threading import Thread

class ClientSocket:

    server_ip = '127.0.0.1'

    @classmethod
    def connect_to_server(cls):
        # Connect to server
        cls.client = Network.connected_socket(cls.server_ip)
        print_colored('info', 'Client has connected to the server')
        server_msg = Network.send_and_recv(cls.client, Messages.CLIENT)
        if server_msg != Messages.OK:
            print_colored('error', 'The server sent a message that is not OK. Exiting')
            MainApp.disconnect()

        # Wait for data
        while True:
            try:
                server_msg = Network.recv(cls.client)
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
            Network.send(cls.client, Messages.OK)

    @classmethod
    def close(cls):
        print_colored('client', Messages.CONNECTION_CLOSED)
        Network.send(cls.client, Messages.CONNECTION_CLOSED)
        cls.client.close()



class GUI(QWidget):

    width = 200
    height = 125

    def __init__(self, app: QApplication):
        super().__init__()

        self.app = app

        # Initialize window
        self.setWindowTitle('Client')

        # Create window layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Show Sign In screen
        self.show_sign_in_screen()

        # Show screen
        self.show()


    def show_sign_in_screen(self):
        # Create Sign In Screen
        self.sign_in_screen = Screen(self, 'Sign In', (250, 225,))
        self.sign_in_screen.center()

        # Create User Name field
        user_name_field = InputField(self, 'Username:', 'Enter your username here')
        self.sign_in_screen.add_widget(user_name_field)

        password_field = InputField(self, 'Password:', 'Enter your password here')
        self.sign_in_screen.add_widget(password_field)


    def show_anti_virus_logs_screen(self):
        # Remove Entry page
        #self.entry_screen.remove()

        # Create Logs page
        width = 400
        height = 300
        logs_screen = Screen(self, 'Anti Virus Logs', (width, height,))
        logs_screen.center()

        # Add Label to Logs page
        label = Label('Virus Detections Logs:')
        logs_screen.add_widget(label)

        # Add list view to Logs page
        self.list_view = ItemsList()
        logs_screen.add_widget(self.list_view)

        # Create Disconnect button
        disconnect_button = Button('Disconnect', MainApp.disconnect)
        logs_screen.add_widget(disconnect_button)

        # Add frame to main layout
        self.main_layout.addWidget(logs_screen)


    def add_data(self, data: str):
        self.list_view.add_data(data)



class MainApp:

    @classmethod
    def run(cls):
        app = QApplication(argv)

        cls.gui = GUI(app)

        exit(app.exec())

    @classmethod
    def connect_to_server(cls):
        client_sock_thrd = Thread(target=ClientSocket.connect_to_server, daemon=True)
        client_sock_thrd.start()
        cls.gui.show_anti_virus_logs_screen()

    @classmethod
    def add_data(cls, data: str):
        cls.gui.add_data(data)
    
    @classmethod
    def disconnect(cls):
        ClientSocket.close()
        cls.exit()

    @classmethod
    def exit(cls):
        print_colored('info', 'Exiting')
        exit(0)


if __name__ == '__main__':
    MainApp.run()
