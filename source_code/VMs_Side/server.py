from server_utils import *
from threading import Thread, Lock


class Server:

    lock = Lock()
    users = SocketsList()
    anti_viruses = SocketsList()

    @classmethod
    def run(cls):
        with Network.listening_socket('0.0.0.0') as server:
            Database.init()
            while True:
                try:
                    client, _ = server.accept()
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
                    client_thread = Thread(target=cls.handle_user, args=(client,))
                elif identity_msg == Messages.IS_ANTI_VIRUS:
                    client_thread = Thread(target=cls.handle_anti_virus, args=(client,))
                else:
                    print_colored('error', 'Unknown socket has connected! Neither client nor Anti Virus')
                    client.close()
                    continue
                Network.send(client, Messages.OK)
                client_thread.start()

    @classmethod
    def handle_user(cls, user: socket):
        username = ''
        while True:
            try:
                user_msg = Network.recv(user)
            except ProtocolError as e:
                print_colored('error', e, cls.lock)
                break

            if UserMessages.is_register(user_msg):
                username = cls.register_new_user(user, user_msg)
            elif UserMessages.is_sign_in(user_msg):
                username, user_id = cls.authenticate_user_sign_in(user, user_msg)
            elif user_msg == UserMessages.SIGN_OUT:
                username = cls.sign_out(user, username, user_id)

            elif user_msg == Messages.OK:
                print_colored('user', user_msg, cls.lock, username=username)
            elif user_msg == Messages.DISCONNECTION:
                break
        user.close()


    @classmethod
    def register_new_user(cls, user: socket, user_msg: str) -> str:
        user_details = UserMessages.pack(user_msg)
        if not user_details:
            return ''
        username, password, email, phone_number = user_details
        success = Database.register(user_details)
        if success:
            Network.send(user, UserMessages.REGISTER_OK)
            return username
        else:
            Network.send(user, UserMessages.USER_EXISTS)
            return ''

    @classmethod
    def authenticate_user_sign_in(cls, user: socket, user_msg: str) -> Tuple[str, int]:
        user_details = UserMessages.pack(user_msg)
        if not user_details:
            return ''
        username, password = user_details
        success, reason = Database.sign_in(user_details)
        if success:
            Network.send(user, UserMessages.SIGN_IN_OK)
            msg = UserMessages.signed_in(username)
            user_id = cls.users.add(user)
            print_colored('server', msg, cls.lock)
            return username, user_id
        else:
            Network.send(user, reason)
            return '', -1
    
    @classmethod
    def sign_out(cls, user: socket, username: str, user_id: int):
        success, reason = Database.sign_out(username)
        if success:
            Network.send(user, UserMessages.SIGN_OUT_OK)
            msg = UserMessages.signed_out(username)
            cls.users.remove(user_id, False)
            print_colored('server', msg, cls.lock)
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
    Server.run()
