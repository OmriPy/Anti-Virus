from protocol import *
from threading import Thread, Lock

lock = Lock()

def handle_client(client: socket):
    lock.acquire()
    print_colored('server', Messages.CLIENT_CONNECTED)
    lock.release()
    try:
        send(client, 'This is a message from the server!')
    except ProtocolError as e:
        lock.acquire()
        print_colored('error', e)
        lock.release()
        client.close()
        return

def handle_anti_virus(anti_virus: socket):
    lock.acquire()
    print_colored('server', Messages.ANTI_VIRUS_CONNECTED)
    lock.release()
    while True:
        anti_virus_msg = recv(anti_virus)
        lock.acquire()
        print_colored('anti virus', anti_virus_msg)
        lock.release()
        send(anti_virus, Messages.OK)
        if anti_virus_msg == Messages.CONNECTION_CLOSED:
            break
    anti_virus.close()

clients_types: Dict[str, Callable] = {
    Messages.ANTI_VIRUS_CONNECTED: handle_anti_virus,
    Messages.CLIENT_CONNECTED: handle_client
}

def server():
    with listening_socket('0.0.0.0') as server:
        while True:
            try:
                client, cli_add = server.accept()
            except KeyboardInterrupt:
                print_colored('info', Messages.CTRL_C)
                return
            try:
                identity_msg = recv(client)
            except KeyboardInterrupt:
                print_colored('info', Messages.CTRL_C)
                client.close()
                return
            except ProtocolError as e:
                print_colored('error', e)
                client.close()
                return
            if identity_msg in clients_types:
                sock_thrd = Thread(target=clients_types[identity_msg], args=(client,))
            else:
                print_colored('error', 'Unknown socket has connected! Neither client nor Anti Virus')
                client.close()
                return
            send(client, Messages.OK)
            sock_thrd.start()


if __name__ == '__main__':
    server()
