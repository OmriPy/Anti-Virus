from server_utils import *
from threading import Thread, Lock

class Server:

    lock = Lock()
    users = SocketsList()
    anti_viruses = SocketsList()

    @classmethod
    def run(cls):
        with Network.listening_socket('0.0.0.0') as server:
            while True:
                try:
                    client, cli_add = server.accept()
                except KeyboardInterrupt:
                    print_colored('info', Messages.CTRL_C)
                    return
                try:
                    identity_msg = Network.recv(client)
                except KeyboardInterrupt:
                    print_colored('info', Messages.CTRL_C)
                    client.close()
                    return
                except ProtocolError as e:
                    print_colored('error', e)
                    client.close()
                    return
                if identity_msg == Messages.IS_USER:
                    sock_thrd = Thread(target=cls.handle_user, args=(client,))
                elif identity_msg == Messages.IS_ANTI_VIRUS:
                    sock_thrd = Thread(target=cls.handle_anti_virus, args=(client,))
                else:
                    print_colored('error', 'Unknown socket has connected! Neither client nor Anti Virus')
                    client.close()
                    continue
                Network.send(client, Messages.OK)
                sock_thrd.start()

    @classmethod
    def handle_user(cls, user: socket):
        user_id = cls.users.add(user)
        username = ''
        while True:
            try:
                user_msg = Network.recv(user)
            except ProtocolError as e:
                print_colored('error', e, cls.lock)
                break
            if user_msg == Messages.OK and username != '':
                print_colored('user', user_msg, cls.lock, username=username)
            if user_msg == Messages.DISCONNECTION and username != '':
                print_colored('user', user_msg, cls.lock, username=username)
                break
            if UserMessages.is_register(user_msg):
                username = cls.add_user(user, user_msg)
            elif UserMessages.is_sign_in(user_msg):
                username = cls.sign_in_check(user, user_msg)
        cls.users.remove(user_id)
    
    @classmethod
    def add_user(cls, user: socket, user_msg: str) -> str:
        user_details = UserMessages.pack(user_msg)
        username, password = user_details
        success = Database.add_user(user_details)
        if success:
            Network.send(user, UserMessages.REGISTER_OK)
            return username
        else:
            Network.send(user, UserMessages.USER_EXISTS)
            return ''

    @classmethod
    def sign_in_check(cls, user: socket, user_msg: str) -> str:
        user_details = UserMessages.pack(user_msg)
        username, password = user_details
        success, reason = Database.sign_in_check(user_details)
        if success:
            Network.send(user, UserMessages.SIGN_IN_OK)
            msg = UserMessages.user_connected(username)
            print_colored('server', msg, cls.lock)
            return username
        else:
            Network.send(user, reason)
            return ''


    @classmethod
    def handle_anti_virus(cls, anti_virus: socket):
        anti_virus_id = cls.anti_viruses.add(anti_virus)
        msg = Messages.anti_virus_connected(anti_virus_id)
        print_colored('server', msg, cls.lock)
        while True:
            try:
                anti_virus_msg = Network.recv(anti_virus)
            except ProtocolError as e:
                print_colored('error', e, cls.lock)
                break
            print_colored('anti virus', anti_virus_msg, cls.lock, anti_virus_id)
            Network.send(anti_virus, Messages.OK)
            if anti_virus_msg == Messages.DISCONNECTION:
                break
            cls.users.send_to_all(anti_virus_msg)
        cls.anti_viruses.remove(anti_virus_id)


if __name__ == '__main__':
    Database.init()
    Server.run()
