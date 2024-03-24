from utils import *
from socket import socket, AF_INET, SOCK_STREAM

####    Utilities    ####

PORT = 55667


####    Errors Handling    ####

class ProtocolError(Exception):

    FLAWED = 'The given packet is flawed according to the protocol'
    BIGGER_THAN_MAX = 'Given data is bigger than the maximum data size'
    HAS_DELIMITER = 'Packet contains DELIMITER string inside its data field'

    def __init__(self, err: str):
        super().__init__(err)


####    Server Side    ####

def listening_socket(IP: str) -> socket:
    """Returns a socket listening to the given IP"""

    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.bind((IP, PORT))
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


####    Client Side    ####

def connected_socket(IP: str) -> socket:
    """Returns a socket connected to the given IP"""

    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect((IP, PORT))
    except ConnectionRefusedError:
        print_colored('error', 'The server is not running')
        exit(0)
    return sock


####    Packet Structure    ####

# The structure:    DATA_SIZE|DATA

DELIMITER = '|'
EXACT_SIZE_LENGTH = 6   # Exact amount of bytes the data_size field has
MAX_DATA_LENGTH = 10 ** EXACT_SIZE_LENGTH - 1     # Max amount of bytes in data field
MAX_TOTAL_SIZE = EXACT_SIZE_LENGTH + len(DELIMITER) + MAX_DATA_LENGTH     # Max total size of packet


def build_packet(data: str) -> str:
    """Builds a packet according to the protocol's structure"""

    size = len(data)

    if size > MAX_DATA_LENGTH:
        raise ProtocolError(ProtocolError.BIGGER_THAN_MAX)
    
    return str(size).zfill(EXACT_SIZE_LENGTH) + DELIMITER + data


def flawed_packet(packet: str) -> bool:
    """Returns False if the packet is well structured (no errors), and returns True if it has an error"""

    if DELIMITER not in packet:
        return True

    try:
        size, data = packet.split(DELIMITER)
    except ValueError:
        raise ProtocolError(ProtocolError.HAS_DELIMITER)

    return \
        len(packet) > MAX_TOTAL_SIZE or \
        len(size) != EXACT_SIZE_LENGTH or \
        len(data) > MAX_DATA_LENGTH or \
        not size.isnumeric() or \
        int(size) != len(data)


def parse_packet(packet: str) -> Tuple[str, str]:
    "Parses the packet into its fields and returns it, if it's a valid one. If it isn't, ProtocolError is raised"

    if flawed_packet(packet):
        raise ProtocolError(ProtocolError.FLAWED)

    return tuple(packet.split(DELIMITER))


####    Communication    ####

def send(sock: socket, msg: str):
    """Sends the message to the socket"""

    packet = build_packet(msg)
    sock.send(packet.encode())


def recv(sock: socket) -> str:
    """Recieves the message from the socket"""

    msg = sock.recv(MAX_TOTAL_SIZE).decode()
    msg = parse_packet(msg)

    return msg[1]

def send_and_recv(sock: socket, msg: str) -> str:
    send(sock, msg)
    return recv(sock)


class Messages:

    OK = 'Your message was recieved and managed'
    CONNECTION_CLOSED = 'The connection has been closed'
    CLIENT_CONNECTED = 'Client has connected'
    ANTI_VIRUS_CONNECTED = 'Anti Virus has connected'
    CTRL_C = 'Exiting due to CTRL+C'
