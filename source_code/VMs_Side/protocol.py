from colored_printing import *
from socket import socket, AF_INET, SOCK_STREAM

class Network:

    PORT = 55667

    @classmethod
    def listening_socket(cls, IP: str) -> socket:
        """Returns a socket listening to the given IP"""

        sock = socket(AF_INET, SOCK_STREAM)
        try:
            sock.bind((IP, cls.PORT,))
        except OSError as e:
            if e.errno == 48:
                print_colored('error', 'Try again later')
            elif e.errno == 49:
                print_colored('error', 'Cannot bind given IP address')
            sock.close()
            exit(0)
        print_colored('info', 'Server is up and running')
        sock.listen()
        return sock

    @classmethod
    def connected_socket(cls, IP: str) -> socket:
        """Returns a socket connected to the given IP"""

        sock = socket(AF_INET, SOCK_STREAM)
        try:
            sock.connect((IP, cls.PORT,))
        except ConnectionRefusedError:
            print_colored('error', 'The server is not running')
            exit(0)
        return sock

    @classmethod
    def send(cls, sock: socket, msg: str):
        """Sends the message to the socket"""

        packet = Packet.build(msg)
        sock.send(packet.encode())

    @classmethod
    def recv(cls, sock: socket) -> str:
        """Recieves the message from the socket"""

        try:
            msg = sock.recv(Packet.MAX_TOTAL_SIZE).decode()
        except ConnectionResetError as e:
            print_colored('error', e)
        msg = Packet.unpack(msg)

        return msg[1]

    @classmethod
    def send_and_recv(cls, sock: socket, msg: str) -> str:
        cls.send(sock, msg)
        return cls.recv(sock)


####    Errors Handling    ####

class ProtocolError(Exception):

    def __init__(self, err: str):
        super().__init__(err)

        self.name = type(self).__name__


####    Packet Structure    ####

class Packet:
    """The structure: DATA_SIZE|DATA"""

    DELIMITER = '|'
    EXACT_SIZE_LENGTH = 6   # Exact amount of bytes the data_size field has
    MAX_DATA_LENGTH = 10 ** EXACT_SIZE_LENGTH - 1     # Max amount of bytes in data field
    MAX_TOTAL_SIZE = EXACT_SIZE_LENGTH + len(DELIMITER) + MAX_DATA_LENGTH     # Max total size of packet

    @classmethod
    def build(cls, data: str) -> str:
        """Builds a packet according to the protocol's structure"""

        size = len(data)

        if size > cls.MAX_DATA_LENGTH:
            raise ProtocolError(ProtocolError.BIGGER_THAN_MAX)
        
        return str(size).zfill(cls.EXACT_SIZE_LENGTH) + cls.DELIMITER + data
    
    @classmethod
    def flawed(cls, packet: str) -> Tuple[bool, str]:
        """Returns a tuple of flawed & reason.
        
        Flawed - boolean representing whether the packet is flawed acoording to the protocol or not.
        True if it is, False otherwise.
        
        Reason - string representing the reason to why the packet is flawed. If it isn't, Reason is empty.
        """

        if packet == '':
            return True, 'Packet is empty'
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
    def unpack(cls, packet: str) -> Tuple[str, str]:
        "Unpacks the packet into its fields and returns it, if it's a valid one. If it isn't, ProtocolError is raised"

        flawed, reason = cls.flawed(packet)
        if flawed:
            raise ProtocolError(reason)

        return tuple(packet.split(cls.DELIMITER))


class Messages:

    OK = 'OK'
    CONNECTION_CLOSED = 'The connection has been closed'
    CTRL_C = 'Exiting due to CTRL+C'
    CLIENT = 'This is Client'
    ANTI_VIRUS = 'This is Anti virus'
    CONNECTED_TEMPLATE = '{}({}) has connected'

    @classmethod
    def connected(cls, connection_type: str, sock_id: int) -> str:
        return cls.CONNECTED_TEMPLATE.format(connection_type, sock_id)
