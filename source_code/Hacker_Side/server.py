from protocol import *
from threading import Thread
from PyQt6.QtWidgets import *
from sqlite3 import *

def handle_client(virus: socket):
    print(virus.recv(2**12).decode())


def server():
    with listening_socket('0.0.0.0') as server:
        while True:
            virus, vrs_addr = server.accept()
            vrs_thrd = Thread(target=handle_client, args=(virus,))
            vrs_thrd.start()

        server.close()
        virus.close()


if __name__ == '__main__':
    server()