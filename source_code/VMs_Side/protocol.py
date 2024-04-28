from socket import socket, AF_INET, SOCK_STREAM
from cryptography import RSA, AESCipher
from utils import *

class Network:

    PORT = 55667

    class Server:

        @classmethod
        def listening_socket(cls, IP: str = '0.0.0.0') -> socket | NoReturn:
            """
            Creates and returns a listening socket bound to the specified IP address.

            Parameters:
            - IP (str): The IP address the server will listen on. Defaults to '0.0.0.0', which means all available interfaces.

            Returns:
            - socket: A socket object that is listening for incoming connections.

            Raises:
            - NoReturn: Exits the program if an OSError occurs during the binding process.
            """

            sock = socket(AF_INET, SOCK_STREAM)
            try:
                sock.bind((IP, Network.PORT,))
            except OSError as e:
                if e.errno == 48:
                    print_colored(Prefixes.ERROR, 'Try again later')
                elif e.errno == 49:
                    print_colored(Prefixes.ERROR, 'Cannot bind given IP address')
                sock.close()
                exit(0)
            print_colored(Prefixes.INFO, 'Server is up and running')
            sock.listen()
            return sock

        @classmethod
        def establish_secure_connection(cls, client: socket) -> AESCipher:
            """
            Establishes a secure connection with a client using RSA for key exchange and AES for encryption.

            This function first generates an RSA key pair. It then sends the RSA public key to the client.
            The client is expected to encrypt an AES key with the RSA public key and send it back.
            This function receives the encrypted AES key, decrypts it using the RSA private key,
            and initializes an AESCipher with the decrypted AES key for secure communication.

            Parameters:
            - client (socket): The client socket to establish a secure connection with.

            Returns:
            - AESCipher: An initialized AESCipher instance for encrypted communication with the client.
            """

            public_key, private_key = RSA.generate_keys()    # Generate RSA key pair
            client.send(RSA.export_key(public_key))   # Send RSA public key to client
            encrypted_aes_key = client.recv(1024)    # Receive AES key encrypted with RSA public key
            aes_key = RSA.decrypt(private_key, encrypted_aes_key)    # Decrypt AES key with RSA private key
            aes_cipher = AESCipher(aes_key)    # Initialize AESCipher with AES key
            return aes_cipher   # Return AESCipher instance for secure communication


    class Client:

        @classmethod
        def connected_socket(cls, IP: str = '127.0.0.1') -> socket | None:
            """Returns a socket connected to the given IP address"""

            sock = socket(AF_INET, SOCK_STREAM)
            try:
                sock.connect((IP, Network.PORT,))
            except ConnectionRefusedError:
                print_colored(Prefixes.ERROR, 'The server is not running')
                sock.close()
                return None
            return sock

        @classmethod
        def establish_secure_connection(cls, client: socket) -> AESCipher:
            """
            Establishes a secure connection to a server by exchanging an AES key encrypted with the server's RSA public key.
            
            This function generates a random AES key, encrypts it using the server's RSA public key, and sends it to the server.
            The AES key is used for creating an AESCipher object for encrypting and decrypting messages sent over the connection.
            
            Parameters:
            - user (socket): The socket object representing the connection to the server.
            
            Returns:
            - AESCipher: An AESCipher object initialized with the generated AES key for encrypting and decrypting messages.
            """
            aes_key = generate_random_string()    # Generate random AES key
            aes_cipher = AESCipher(aes_key)    # Create AESCipher object
            public_key = client.recv(1024)    # Receive the RSA public key
            public_key = RSA.import_key(public_key)    # Import the RSA public key
            client.send(RSA.encrypt(public_key, aes_key))    # Send the AES key encrypted with the RSA public key
            return aes_cipher    # Return the AESCipher object

        @classmethod
        def verify_connection_with_server(cls, client: socket, identity: str) -> Tuple[AESCipher, str]:
            if identity != Messages.IS_USER and identity != Messages.IS_ANTI_VIRUS:
                return None, 'Client identity is neither User nor Anti'
            try:
                server_msg = Network.send_and_recv(client, identity)
            except ProtocolError as e:
                print_colored(Prefixes.ERROR, e)
                return None, 'Protocol error'
            if server_msg != Messages.OK:
                reason = f'Server sent: {server_msg}. Expected: {Messages.OK}'
                print_colored(Prefixes.WARNING, reason)
                return None, reason
            cls.aes = Network.Client.establish_secure_connection(client) # think what to do about errors handling in this function


    @classmethod
    def send(cls, sock: socket, msg: str, aes: Optional[AESCipher] = None):
        """Sends the message to the socket"""

        if aes:
            msg = aes.encrypt(msg)
        msg = Packet.build(msg)
        sock.send(msg.encode())

    @classmethod
    def recv(cls, sock: socket, aes: Optional[AESCipher] = None) -> str:
        """Recieves the message from the socket"""

        bufsize = 1024
        msg = ''
        try:
            size = sock.recv(Packet.EXACT_SIZE_LENGTH).decode()
            msg += size
            size = int(size)
            iters = size // bufsize
            remainder = size % bufsize
            delimiter = sock.recv(Packet.DELIMITER_LENGTH).decode()
            if delimiter != Packet.DELIMITER:
                raise ProtocolError(f'The received delimiter \'{delimiter}\' is not the expected delimiter \'{Packet.DELIMITER}\'')
            msg += delimiter
            for _ in range(iters):
                msg += sock.recv(bufsize).decode()
            msg += sock.recv(remainder).decode()
        except ConnectionResetError as e:
            raise ProtocolError(e.strerror)

        msg = Packet.extract_data(msg)
        if aes:
            try:
                msg = aes.decrypt(msg)
            except ValueError as e:
                raise ProtocolError(e)
        return msg

    @classmethod
    def send_and_recv(cls, sock: socket, msg: str, aes: Optional[AESCipher] = None) -> str:
        cls.send(sock, msg, aes)
        return cls.recv(sock, aes)


####    Errors Handling    ####

class ProtocolError(Exception):

    def __init__(self, err: str):
        super().__init__(err)

        self.name = type(self).__name__


####    Packet Structure    ####

class Packet:
    """The structure: DATA_SIZE|DATA"""

    DELIMITER = '|'
    DELIMITER_LENGTH = len(DELIMITER)
    EXACT_SIZE_LENGTH = 6   # Exact amount of bytes the data_size field has
    MAX_DATA_LENGTH = 10 ** EXACT_SIZE_LENGTH - 1     # Max amount of bytes in data field
    MAX_TOTAL_SIZE = EXACT_SIZE_LENGTH + DELIMITER_LENGTH + MAX_DATA_LENGTH     # Max total size of packet

    @classmethod
    def build(cls, data: str) -> str:
        """Builds a packet according to the protocol's structure"""

        size = len(data)
        packet = str(size).zfill(cls.EXACT_SIZE_LENGTH) + cls.DELIMITER + data

        flawed, reason = cls.flawed(packet)
        if flawed:
            raise ProtocolError(reason)

        return packet

    @classmethod
    def flawed(cls, packet: str) -> Tuple[bool, str]:
        """Returns a tuple of flawed & reason.

        Flawed - boolean representing whether the packet is flawed acoording to the protocol or not.
        True if it is, False otherwise.

        Reason - string representing the reason to why the packet is flawed. If it isn't, Reason is empty.
        """

        if packet == '':
            return True, 'Empty packet'

        elif cls.DELIMITER not in packet:
            return True, 'No delimiter found in packet'

        elif packet.count(cls.DELIMITER) > 1:
            return True, 'Delimiter found multiple times in packet instead of once as expected'

        elif len(packet) > cls.MAX_TOTAL_SIZE:
            return True, 'Packet is bigger than maximum possible size'

        size, data = packet.split(cls.DELIMITER)

        if len(size) != cls.EXACT_SIZE_LENGTH:
            return True, 'The length of the size field is not the expected length'

        elif len(data) > cls.MAX_DATA_LENGTH:
            return True, 'The length of the data field is bigger than maximum possible size'

        elif not size.isnumeric():
            return True, 'The size field is not numeric'

        elif int(size) != len(data):
            return True, 'The length of the data field does not equal the size field\'s value'

        return False, ''

    @classmethod
    def extract_data(cls, packet: str) -> str:
        """Extracts the data from the packet and returns it if the packet is valid. If it isn't, ProtocolError is raised"""

        flawed, reason = cls.flawed(packet)
        if flawed:
            raise ProtocolError(reason)

        size, data = packet.split(cls.DELIMITER)
        return data


class Messages:

    OK = 'OK'
    DISCONNECTION = 'Disconnected'
    CTRL_C = 'Exiting due to CTRL+C'
    CONNECTED = '{}({}) connected'

    IS_USER = 'This is User'
    IS_ANTI_VIRUS = 'This is Anti Virus'

    @classmethod
    def anti_virus_connected(cls, sock_id: int) -> str:
        return cls.CONNECTED.format('Anti Virus', sock_id)



class UserMessages:

    class Register:

        form = 'Register: {}, {}, {}, {}'
        OK = 'Registration form is OK'
        user_added = 'User ({}) has been added'

        class Errors:

            USER_EXISTS = 'User already exists'


        @classmethod
        def register(cls, user_details: Tuple[str, str, str, str]) -> str:
            username, password, confirm_pass, email, phone_number = user_details
            return cls.form.format(username, password, email, phone_number)

        @classmethod
        def is_register(cls, msg: str) -> bool:
            try:
                return msg.startswith(cls.form[:cls.form.index(':')])
            except AttributeError:
                err_msg = f'Function {func_name(cls.is_register, cls)} received a Non-str argument: {type(msg)}'
                print_colored(Prefixes.ERROR, err_msg)
                return False

        @classmethod
        def added(cls, username: str) -> str:
            return cls.user_added.format(username)


    class SignIn:

        form = 'Sign_In: {}, {}'
        OK = 'Sign In is OK'
        user_signed_in = 'User ({}) signed in'

        class Errors:

            NO_EXISTING_USER = 'No user exists with given username'
            INCORRECT_PASS = 'Password is incorrect'
            ALREADY_SIGNED_IN = 'This user is currently signed in'


        @classmethod
        def sign_in(cls, user_details: Tuple[str, str]) -> str:
            username, password = user_details
            return cls.form.format(username, password)

        @classmethod
        def is_sign_in(cls, msg: str) -> bool:
            try:
                return msg.startswith(cls.form[:cls.form.index(':')])
            except AttributeError:
                error_msg = f'Function {func_name(cls.is_sign_in, cls)} received a Non-str argument: {type(msg)}'
                print_colored(Prefixes.ERROR, error_msg)
                return False

        @classmethod
        def has_signed_in(cls, username: str) -> str:
            return cls.user_signed_in.format(username)


    class SignOut:

        SIGN_OUT = 'Sign out'
        OK = 'Sign out OK'
        user_signed_out = 'User ({}) signed out'

        class Errors:

            USER_NOT_FOUND = 'No user found with given username'
            NOT_SIGNED_IN = 'This user is not signed in'


        @classmethod
        def signed_out(cls, username: str) -> str:
            return cls.user_signed_out.format(username)

    # Other
    # USER_REMOVED = 'User ({}) has been removed'

    @classmethod
    def extract_details(cls, msg: str) -> Tuple | None:
        try:
            details = msg[msg.index(' ')+1:]
            return tuple(details.split(', '))
        except AttributeError:
            error_msg = f'Function {func_name(cls.extract_details, cls)} received a Non-str argument: {type(msg)}'
            print_colored(Prefixes.ERROR, error_msg)
            return None


    '''@classmethod
    def removed(cls, username: str) -> str:
        return cls.USER_REMOVED.format(username)'''
