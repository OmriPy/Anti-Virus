from user_utils import *
from sys import argv
from threading import Thread


class UserSocket:

    server_ip = '127.0.0.1'
    aes: AESCipher = None
    connected = False

    @classmethod
    def connect_to_server(cls):
        if cls.connected:
            return
        # Connect to server
        cls.user = Network.Client.connected_socket(cls.server_ip)
        if not cls.user:
            Main.server_not_running()
            return
        print_colored(Prefixes.INFO, 'User has connected to the server')

        try:
            server_msg = Network.send_and_recv(cls.user, Messages.IS_USER)
        except ProtocolError as e:
            print_colored(Prefixes.ERROR, e)
            return
        if server_msg != Messages.OK:
            print_colored(Prefixes.WARNING, f'Server sent: {server_msg}. Expected: {Messages.OK}. Exiting')
            Main.exit()
        cls.aes = Network.Client.establish_secure_connection(cls.user)

        cls.connected = True

    @classmethod
    def register(cls, user_details: Tuple[str, str, str, str]) -> Tuple[bool, str]:
        regsiter_msg = UserMessages.Register.register(user_details)
        try:
            server_msg = Network.send_and_recv(cls.user, regsiter_msg, cls.aes)
        except ProtocolError as e:
            print_colored(Prefixes.ERROR, e)
            Main.exit()
        if server_msg == UserMessages.Register.OK:
            return True, ''
        elif server_msg == UserMessages.Register.Errors.USER_EXISTS:
            return False, server_msg
        else:
            return False, 'Registration failed due to unrecognized reason'

    @classmethod
    def sign_in(cls, user_details: Tuple[str, str]) -> Tuple[bool, str]:
        sign_in_msg = UserMessages.SignIn.sign_in(user_details)
        try:
            server_msg = Network.send_and_recv(cls.user, sign_in_msg, cls.aes)
        except ProtocolError as e:
            print_colored(Prefixes.ERROR, e)
            Main.exit()
        if server_msg == UserMessages.SignIn.OK:
            return True, server_msg
        elif server_msg == UserMessages.SignIn.Errors.NO_EXISTING_USER or \
            server_msg == UserMessages.SignIn.Errors.INCORRECT_PASS or \
            server_msg == UserMessages.SignIn.Errors.ALREADY_SIGNED_IN:
            return False, server_msg
        else:
            return False, 'Sign In failed due to unrecognized reason'

    @classmethod
    def send_sign_out_request(cls):
        Network.send(cls.user, UserMessages.SignOut.SIGN_OUT, cls.aes)


    @classmethod
    def recieve_anti_virus_logs(cls):
        while True:
            try:
                server_msg = Network.recv(cls.user, cls.aes)
            except ProtocolError as e:
                print_colored(Prefixes.ERROR, e)
                continue
            except KeyboardInterrupt:
                print_colored(Prefixes.INFO, Messages.CTRL_C)
                Main.exit()

            Main.update_sign_out_status(server_msg)
            success, reason = Main.sign_out_status
            if success:
                break

            print_colored(Prefixes.SERVER, server_msg)
            Main.add_data(server_msg)
            Network.send(cls.user, Messages.OK, cls.aes)

    @classmethod
    def close(cls):
        if cls.connected:
            Network.send(cls.user, Messages.DISCONNECTION, cls.aes)
            cls.user.close()
            print_colored(Prefixes.USER, Messages.DISCONNECTION)


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
        self.exit_button = Button('Exit', Main.exit)

        # Show Sign In screen
        self.show_sign_in_screen()

        # Show screen
        self.show()


    def show_sign_in_screen(self, former_screen: Optional[Screen] = None):
        # Remove former screen
        if former_screen:
            former_screen.remove()

        # Create Sign In Screen
        width = 400
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
        sign_in_button = Button('Sign In', lambda: Main.sign_in((
            username_field.text(),
            password_field.text()
            ,)))
        self.sign_in_screen.add_widget(sign_in_button, True)

        # Register button
        register_button = Button('No account? Register here', self.show_register_screen)
        self.sign_in_screen.add_widget(register_button, True)

        # Exit button
        self.exit_button = Button('Exit', Main.exit)
        self.sign_in_screen.add_widget(self.exit_button, True)


    def show_register_screen(self):
        # Remove Sign In screen
        self.sign_in_screen.remove()

        # Create Register Screen
        width = 350
        height = 600
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
        confirm_pass_field = InputField(self, 'Confirm password', place_holder='Enter your password again', hide=True)
        self.register_screen.add_widget(confirm_pass_field)

        # Email field
        email_field = InputField(self, 'Email')
        self.register_screen.add_widget(email_field)

        # Phone Number field
        phone_number_field = InputField(self, 'Phone number')
        self.register_screen.add_widget(phone_number_field)

        # Create register button
        register_button = Button('Register', lambda: Main.register((
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
        width = 425
        height = 350
        self.logs_screen = Screen(self, 'Anti Virus Logs', (width, height,))
        self.logs_screen.center()

        # Add username label
        username_label = Label(Main.username)
        username_label.setStyleSheet('''
                                     font-size: 14px;
                                     text-decoration: underline''')
        self.logs_screen.add_widget(username_label, True)

        # Add label
        title_label = Label('Virus Detections Logs:')
        self.logs_screen.add_widget(title_label)

        # Add list view to Logs page
        self.list_view = ItemsList()
        self.logs_screen.add_widget(self.list_view)

        # Create sign out button
        sign_out_button = Button('Sign Out', Main.sign_out)
        self.logs_screen.add_widget(sign_out_button, True)

        # Add frame to main layout
        self.main_layout.addWidget(self.logs_screen)


    def add_data(self, data: str):
        self.list_view.add_data(data)



class Main:

    username: Optional[str] = None
    sign_out_status: Tuple[bool, str] = (False, '')

    @classmethod
    def run(cls):
        app = QApplication(argv)
        cls.gui = GUI(app)
        exit_code = app.exec()
        exit(exit_code)


    @classmethod
    def register(cls, user_details: Tuple[str, str, str, str, str]):
        username, password, confirm_pass, email, phone_number = user_details
        pass_length = len(password)
        pass_min_length = 4
        pass_max_length = 20
        if not username or not password or not confirm_pass or not email or not phone_number:
            pop_up = PopUp('All fields are required', PopUp.WARNING)
        elif pass_length < pass_min_length or pass_length > pass_max_length:
            pop_up = PopUp(f'Password length must be within the range {pass_min_length}-{pass_max_length}', PopUp.WARNING)
        elif password != confirm_pass:
            pop_up = PopUp('Password and Confirm Password fields are not the same', PopUp.WARNING)
        elif '@' not in email:
            pop_up = PopUp('Invalid Email', PopUp.WARNING)
        elif not phone_number.isnumeric():
            pop_up = PopUp('Invalid Phone Number', PopUp.WARNING)
        else:
            UserSocket.connect_to_server()
            if UserSocket.connected:
                success, reason = UserSocket.register(user_details)
                if success:
                    pop_up = PopUp('Registration Completed', PopUp.INFO)
                    cls.gui.show_sign_in_screen(cls.gui.register_screen)
                else:
                    pop_up = PopUp(reason, PopUp.WARNING)
            else:
                return
        pop_up.show()

    @classmethod
    def sign_in(cls, user_details: Tuple[str, str]):
        UserSocket.connect_to_server()
        if UserSocket.connected:
            success, reason = UserSocket.sign_in(user_details)
            if success:
                username, password = user_details
                cls.username = username
                pop_up = PopUp('Sign In Successful!', PopUp.INFO)
                pop_up.show()
                cls.show_anti_virus_logs()
            else:
                pop_up = PopUp(reason, PopUp.WARNING)
                pop_up.show()

    @classmethod
    def show_anti_virus_logs(cls):
        '''cls.anti_virus_logs_thread = None
        if cls.anti_virus_logs_thread and cls.anti_virus_logs_thread.is_alive():
            return'''
        cls.anti_virus_logs_thread = Thread(target=UserSocket.recieve_anti_virus_logs)
        cls.anti_virus_logs_thread.start()
        cls.gui.show_anti_virus_logs_screen()

    @classmethod
    def sign_out(cls):
        UserSocket.send_sign_out_request()
        cls.anti_virus_logs_thread.join()
        success, reason = cls.sign_out_status
        if success:
            cls.username = None
            cls.gui.show_sign_in_screen(cls.gui.logs_screen)
        else:
            pop_up = PopUp(reason, PopUp.WARNING)
            pop_up.show()


    @classmethod
    def update_sign_out_status(cls, server_msg: str):
        status_map: Dict[str, Tuple[bool, str]] = {
            UserMessages.SignOut.OK: (True, ''),
            UserMessages.SignOut.Errors.USER_NOT_FOUND: (False, server_msg),
            UserMessages.SignOut.Errors.NOT_SIGNED_IN: (False, server_msg),
            'default': (False, 'Sign Out failed due to unrecognized reason'),
        }
        cls.sign_out_status = status_map.get(server_msg, status_map.get('default'))


    @classmethod
    def add_data(cls, data: str):
        cls.gui.add_data(data)


    @classmethod
    def server_not_running(cls):
        pop_up = PopUp('The server is not running', PopUp.CRITICAL)
        pop_up.show()

    @classmethod
    def exit(cls):
        UserSocket.close()
        print_colored(Prefixes.INFO, 'Exiting')
        exit()


if __name__ == '__main__':
    Main.run()
