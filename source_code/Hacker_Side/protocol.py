from socket import socket, AF_INET, SOCK_STREAM
from utils import *

PORT = 55667

####    Server side    ####

def listening_socket(IP: str) -> socket:
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.bind((IP, PORT))
    except OSError as e:
        if e.errno == 48:
            print('Try again later')
        elif e.errno == 49:
            print('Cannot bind given IP address')
        sock.close()
        exit(0)
    print('Server is up and running')
    sock.listen()
    return sock


####    Client side    ####

def connected_socket(IP: str) -> socket:
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((IP, PORT))
    return sock