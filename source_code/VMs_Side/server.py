from server_utils import *
from threading import Thread, Lock


class Server:

    lock = Lock()
    users = SocketsList()
    anti_viruses = SocketsList()

    @classmethod
    def run(cls):
        with Network.Server.listening_socket() as server:
            Database.init()
            while True:
                try:
                    client, _ = server.accept()
                except KeyboardInterrupt:
                    print_colored(Prefixes.INFO, Messages.CTRL_C, cls.lock)
                    return

                try:
                    client_identity = Network.recv(client)
                except ProtocolError as e:
                    print_colored(Prefixes.ERROR, e, cls.lock)
                    client.close()
                    continue
                except KeyboardInterrupt:
                    print_colored(Prefixes.INFO, Messages.CTRL_C, cls.lock)
                    client.close()
                    return

                if client_identity == Messages.IS_USER:
                    client_thread = Thread(target=cls.handle_user, args=(client,))
                elif client_identity == Messages.IS_ANTI_VIRUS:
                    client_thread = Thread(target=cls.handle_anti_virus, args=(client,))
                else:
                    print_colored(Prefixes.WARNING, 'Unrecognized client has connected! Neither User nor Anti Virus', cls.lock)
                    client.close()
                    continue

                Network.send(client, Messages.OK)
                client_thread.start()

    @classmethod
    def handle_user(cls, user: socket):
        aes = Network.Server.establish_secure_connection(user)
        username = ''
        while True:
            try:
                user_msg = Network.recv(user, aes)
            except ProtocolError as e:
                print_colored(Prefixes.ERROR, e, cls.lock)
                break

            if UserMessages.Register.is_register(user_msg):
                username = cls.register_new_user(user, aes, user_msg)
            elif UserMessages.SignIn.is_sign_in(user_msg):
                username, user_id = cls.authenticate_user_sign_in(user, aes, user_msg)
            elif user_msg == UserMessages.SignOut.SIGN_OUT:
                username = cls.sign_out(user, aes, username, user_id)

            elif user_msg == Messages.OK:
                print_colored(Prefixes.USER, user_msg, cls.lock, username=username)
            elif user_msg == Messages.DISCONNECTION:
                break
        user.close()


    @classmethod
    def register_new_user(cls, user: socket, aes: AESCipher, user_msg: str) -> str:
        user_details = UserMessages.extract_details(user_msg)
        if not user_details:
            return ''
        username, password, email, phone_number = user_details
        success = Database.register(user_details)
        if success:
            Network.send(user, UserMessages.Register.OK, aes)
            return username
        else:
            Network.send(user, UserMessages.Register.Errors.USER_EXISTS, aes)
            return ''

    @classmethod
    def authenticate_user_sign_in(cls, user: socket, aes: AESCipher, user_msg: str) -> Tuple[str, int]:
        user_details = UserMessages.extract_details(user_msg)
        if not user_details:
            return ''
        username, password = user_details
        success, reason = Database.sign_in(user_details)
        if success:
            Network.send(user, UserMessages.SignIn.OK, aes)
            user_id = cls.users.add(user, aes)
            msg = UserMessages.SignIn.has_signed_in(username)
            print_colored(Prefixes.SERVER, msg, cls.lock)
            return username, user_id
        else:
            Network.send(user, reason, aes)
            return '', -1
    
    @classmethod
    def sign_out(cls, user: socket, aes: AESCipher, username: str, user_id: int):
        success, reason = Database.sign_out(username)
        if success:
            Network.send(user, UserMessages.SignOut.OK, aes)
            msg = UserMessages.SignOut.signed_out(username)
            cls.users.remove(user_id, False)
            print_colored(Prefixes.SERVER, msg, cls.lock)
        else:
            Network.send(user, reason, aes)
        return ''


    @classmethod
    def handle_anti_virus(cls, anti_virus: socket):
        aes = Network.Server.establish_secure_connection(anti_virus)
        anti_virus_id = cls.anti_viruses.add(anti_virus, aes)
        msg = Messages.anti_virus_connected(anti_virus_id)
        print_colored(Prefixes.SERVER, msg, cls.lock)
        while True:
            try:
                anti_virus_msg = Network.recv(anti_virus, aes)
            except ProtocolError as e:
                print_colored(Prefixes.ERROR, e, cls.lock)
                break
            print_colored(Prefixes.ANTI_VIRUS, anti_virus_msg, cls.lock, anti_virus_id)
            Network.send(anti_virus, Messages.OK, aes)
            if anti_virus_msg == Messages.DISCONNECTION:
                break
            cls.users.send_to_all(anti_virus_msg)
        cls.anti_viruses.remove(anti_virus_id)


if __name__ == '__main__':
    Server.run()
