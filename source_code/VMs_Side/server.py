from protocol import *
from threading import Thread

def handle_client(client: socket):
    print('A client has connected')
    try:
        send(client, 'This is a message from the server!')
    except ProtocolError as e:
        print(e)
        return

def server():
    with listening_socket('0.0.0.0') as server:
        print()
        while True:
            try:
                client, cli_add = server.accept()
            except KeyboardInterrupt:
                return
            thrd = Thread(target=handle_client, args=(client,))
            thrd.start()


if __name__ == '__main__':
    server()