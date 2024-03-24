from protocol import *
from threading import Thread

def handle_client(client: socket):
    print_colored('server', 'Client has connected')
    try:
        send(client, 'This is a message from the server!')
    except ProtocolError as e:
        print(e)
        return

def handle_anti_virus(anti_virus: socket):
    print_colored('server', 'Anti Virus has connected')
    while True:
        print_colored('anti virus', recv(anti_virus))
        send(anti_virus, Messages.OK)    # for now, doesn't check the value of the message, if it is alright or not
    client.close()

def server():
    with listening_socket('0.0.0.0') as server:
        while True:
            try:
                client, cli_add = server.accept()
            except KeyboardInterrupt:
                return
            identity = recv(client)
            thrd = Thread(target=handle_client, args=(client,))
            thrd.start()


if __name__ == '__main__':
    server()
