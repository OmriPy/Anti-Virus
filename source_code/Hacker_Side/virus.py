from protocol import *

def virus():
    virus = connected_socket('127.0.0.1')
    virus.sendall('Hello there Server Socket'.encode())
    virus.close()

if __name__ == '__main__':
    virus()