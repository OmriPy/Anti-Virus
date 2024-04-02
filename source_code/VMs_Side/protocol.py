from colored_printing import *
from socket import socket, AF_INET, SOCK_STREAM

class Protocol:

    PORT = 55667

    @classmethod
    def listening_socket(cls, IP: str) -> socket:
        """Returns a socket listening to the given IP"""

        sock = socket(AF_INET, SOCK_STREAM)
        try:
            sock.bind((IP, cls.PORT))
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
            sock.connect((IP, cls.PORT))
        except ConnectionRefusedError:
            print_colored('error', 'The server is not running')
            exit(0)
        return sock


####    Errors Handling    ####

class ProtocolError(Exception):

    FLAWED = 'The given packet is flawed according to the protocol'
    BIGGER_THAN_MAX = 'Given data is bigger than the maximum data size'
    HAS_DELIMITER = 'Packet contains DELIMITER string inside its data field'

    def __init__(self, err: str):
        super().__init__(err)


####    Packet Structure    ####

# The structure:    DATA_SIZE|DATA

class Packet:

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
    def flawed(cls, packet: str) -> bool:
        """Returns False if the packet is well structured (no errors), and returns True if it has an error"""

        if cls.DELIMITER not in packet:
            return True

        try:
            size, data = packet.split(cls.DELIMITER)
        except ValueError:
            raise ProtocolError(ProtocolError.HAS_DELIMITER)

        return \
            len(packet) > cls.MAX_TOTAL_SIZE or \
            len(size) != cls.EXACT_SIZE_LENGTH or \
            len(data) > cls.MAX_DATA_LENGTH or \
            not size.isnumeric() or \
            int(size) != len(data)

    @classmethod
    def parse(cls, packet: str) -> Tuple[str, str]:
        "Parses the packet into its fields and returns it, if it's a valid one. If it isn't, ProtocolError is raised"

        if cls.flawed(packet):
            raise ProtocolError(ProtocolError.FLAWED)

        return tuple(packet.split(cls.DELIMITER))


####    Communication    ####

def send(sock: socket, msg: str):
    """Sends the message to the socket"""

    packet = Packet.build(msg)
    sock.send(packet.encode())


def recv(sock: socket) -> str:
    """Recieves the message from the socket"""

    try:
        msg = sock.recv(Packet.MAX_TOTAL_SIZE).decode()
    except ConnectionResetError as e:
        print_colored('error', e)
    msg = Packet.parse(msg)

    return msg[1]

def send_and_recv(sock: socket, msg: str) -> str:
    send(sock, msg)
    return recv(sock)


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
