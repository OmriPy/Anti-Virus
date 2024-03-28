from serverUtils import *
from threading import Thread, Lock

class Server:

    lock = Lock()
    clients = Sockets()
    anti_viruses = Sockets()

    @classmethod
    def run(cls):
        with Protocol.listening_socket('0.0.0.0') as server:
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
                if identity_msg == Messages.CLIENT:
                    sock_thrd = Thread(target=cls.handle_client, args=(client,))
                elif identity_msg == Messages.ANTI_VIRUS:
                    sock_thrd = Thread(target=cls.handle_anti_virus, args=(client,))
                else:
                    print_colored('error', 'Unknown socket has connected! Neither client nor Anti Virus')
                    client.close()
                    return
                send(client, Messages.OK)
                sock_thrd.start()

    @classmethod
    def handle_client(cls, client: socket):
        client_id = cls.clients.add(client)
        print_colored('server', Messages.connected('Client', client_id), cls.lock)
        try:
            send(client, 'This is a message from the server!')
        except ProtocolError as e:
            print_colored('error', e, cls.lock)
            cls.clients.remove(client_id)
            return

    @classmethod
    def handle_anti_virus(cls, anti_virus: socket):
        anti_virus_id = cls.anti_viruses.add(anti_virus)
        print_colored('server', Messages.connected('Anti Virus', anti_virus_id), cls.lock)
        while True:
            try:
                anti_virus_msg = recv(anti_virus)
            except ProtocolError as e:
                print_colored('error', e, cls.lock)
                cls.anti_viruses.remove(anti_virus_id)
                return
            print_colored(f'anti virus({anti_virus_id})', anti_virus_msg, cls.lock)
            send(anti_virus, Messages.OK)
            if anti_virus_msg == Messages.CONNECTION_CLOSED:
                break
            # TODO: Add here the notifying the clients about the virus detection,
            # also change the client.py code accordingly
        cls.anti_viruses.remove(anti_virus_id)


if __name__ == '__main__':
    Server.run()
