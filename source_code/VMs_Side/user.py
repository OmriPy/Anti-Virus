from user_utils import *
from sys import argv
from threading import Thread

class UserSocket:

    server_ip = '127.0.0.1'
    connected = False

    @classmethod
    def connect_to_server(cls):
        if cls.connected:
            return
        # Connect to server
        cls.user = Network.connected_socket(cls.server_ip)
        print_colored('info', 'User has connected to the server')
        server_msg = Network.send_and_recv(cls.user, Messages.IS_USER)
        if server_msg != Messages.OK:
            print_colored('error', 'The server sent a message that is not OK. Exiting')
            MainApp.disconnect()
        cls.connected = True
    
    @classmethod
    def register(cls, user_details: Tuple[str, str, str, str]) -> Tuple[bool, str]:
        server_msg = Network.send_and_recv(cls.user, UserMessages.register(user_details))
        if server_msg == UserMessages.REGISTER_OK:
            return True, ''
        elif server_msg == UserMessages.USER_EXISTS:
            return False, server_msg

    @classmethod
    def sign_in(cls, user_details: Tuple[str, str]) -> Tuple[bool, str]:
        server_msg = Network.send_and_recv(cls.user, UserMessages.sign_in(user_details))
        if server_msg == UserMessages.SIGN_IN_OK:
            return True, server_msg
        elif server_msg == UserMessages.NO_EXISTING_USER or server_msg == UserMessages.INCORRECT_PASS:
            return False, server_msg

    @classmethod
    def recieve_anti_virus_logs(cls):
        # Wait for data
        while True:
            try:
                server_msg = Network.recv(cls.user)
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
            Network.send(cls.user, Messages.OK)

    @classmethod
    def close(cls):
        print_colored('user', Messages.DISCONNECTION)
        Network.send(cls.user, Messages.DISCONNECTION)
        cls.user.close()
        cls.connected = False


class GUI(QWidget):

    width = 200
    height = 125

    def __init__(self, app: QApplication):
        super().__init__()

        self.app = app

        # Initialize window
        self.setWindowTitle('User')

        # Create window layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Create Exit button to use accross screens
        self.exit_button = Button('Exit', MainApp.disconnect)

        # Show Sign In screen
        self.show_sign_in_screen()

        # Show screen
        self.show()


    def show_sign_in_screen(self):
        # Make sure register screen is removed
        try:
            self.register_screen.remove()
        except AttributeError:
            pass

        # Create Sign In Screen
        width = 350
        height = 350
        self.sign_in_screen = Screen(self, 'Sign In', (width, height,))
        self.sign_in_screen.center()

        # Create fields
        # Username field
        username_field = InputField(self, 'Username')
        self.sign_in_screen.add_widget(username_field)

        # Password field
        password_field = InputField(self, 'Password', hide=True)
        self.sign_in_screen.add_widget(password_field)

        # Sign In button
        sign_in_button = Button('Sign In', lambda: MainApp.sign_in((
            username_field.text(),
            password_field.text()
            ,)))
        self.sign_in_screen.add_widget(sign_in_button, True)

        # Register button
        register_button = Button('No account? Register here', self.show_register_screen)
        self.sign_in_screen.add_widget(register_button, True)

        # Exit button
        self.sign_in_screen.add_widget(self.exit_button, True)


    def show_register_screen(self):
        # Remove Sign In screen
        self.sign_in_screen.remove()

        # Create Register Screen
        width = 350
        height = 630
        self.register_screen = Screen(self, 'Register', (width, height,))
        self.register_screen.center()

        # Create fields
        # Username field
        username_field = InputField(self, 'Username')
        self.register_screen.add_widget(username_field)

        # Password field
        password_field = InputField(self, 'Password', hide=True)
        self.register_screen.add_widget(password_field)

        # Confirm password field
        confirm_pass_field = InputField(self, 'Confirm Password', 'Enter your password again', hide=True)
        self.register_screen.add_widget(confirm_pass_field)

        # Email field
        email_field = InputField(self, 'Email')
        self.register_screen.add_widget(email_field)

        # Phone Number field
        phone_number_field = InputField(self, 'Phone Number')
        self.register_screen.add_widget(phone_number_field)

        # Create register button
        register_button = Button('Register', lambda: MainApp.register((
            username_field.text(),
            password_field.text(),
            confirm_pass_field.text(),
            email_field.text(),
            phone_number_field.text()
            ,)))
        self.register_screen.add_widget(register_button, True)

        # Exit button
        self.register_screen.add_widget(self.exit_button, True)


    def show_anti_virus_logs_screen(self):
        # Remove Sign In page
        self.sign_in_screen.remove()

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
        logs_screen.add_widget(disconnect_button, True)

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
        user_thread = Thread(target=UserSocket.connect_to_server)
        user_thread.start()
        user_thread.join()  # wait for the thread to terminate


    @classmethod
    def register(cls, user_details: Tuple[str, str, str, str, str]):
        username, password, confirm_pass, email, phone_number = user_details
        if password != confirm_pass:
            pop_up = PopUp('Password and Confirm Password fields are not the same', PopUp.WARNING)
            pop_up.show()
        else:
            cls.connect_to_server()
            success, reason = UserSocket.register(user_details)
            if success:
                pop_up = PopUp('Registration Completed', PopUp.INFO)
                cls.gui.show_sign_in_screen()
            else:
                pop_up = PopUp(reason, PopUp.WARNING)
            pop_up.show()
    
    @classmethod
    def sign_in(cls, user_details: Tuple[str, str]):
        cls.connect_to_server()
        success, reason = UserSocket.sign_in(user_details)
        if success:
            pop_up = PopUp('Sign In Successful!', PopUp.INFO)
            pop_up.show()
            anti_virus_logs_thread = Thread(target=UserSocket.recieve_anti_virus_logs)
            anti_virus_logs_thread.start()
            cls.gui.show_anti_virus_logs_screen()
        else:
            pop_up = PopUp(reason, PopUp.WARNING)
            pop_up.show()


    @classmethod
    def add_data(cls, data: str):
        cls.gui.add_data(data)
    
    @classmethod
    def disconnect(cls):
        UserSocket.close()
        cls.exit()

    @classmethod
    def exit(cls):
        print_colored('info', 'Exiting')
        exit(0)


if __name__ == '__main__':
    MainApp.run()
