from anti_virus_utils import *
import time

class AntiVirus:

    server_ip = '127.0.0.1'
    virus = 'lab_rat.py'
    delay = 5
    scan_outcomes: Dict[Tuple[bool, bool], str] = {
        (False, False): 'No virus detected',
        (True, True): '[{}] The virus \"{}\" was detected and killed',
        (True, False): '[{}] The virus \"{}\" was detected but could not be killed'
    }

    @classmethod
    def run(cls):
        # Attempts to check whether the server is running or not
        '''socket_attempt = Network.Client.connected_socket(cls.server_ip)
        if not socket_attempt:
            return
        socket_attempt.close()'''

        # Connect to the server
        with Network.Client.connected_socket(cls.server_ip) as cls.anti_virus:
            cls.aes = Network.Client.verify_connection_with_server(cls.anti_virus, Messages.IS_ANTI_VIRUS)
            if not cls.aes:
                return

            print_colored(Prefixes.INFO, 'Anti Virus has connected to the server')
            print_colored(Prefixes.INFO, f'Virus is \"{cls.virus}\"')

            virus_proc = FindAndKillProcess(cls.virus)
            while True:
                try:
                    scan_result = virus_proc.hunt()
                except KeyboardInterrupt:
                    print_colored(Prefixes.ANTI_VIRUS, 'Scanning was interrupted')
                    cls.exit()

                found, killed = scan_result
                if found:
                    msg = cls.scan_outcomes[scan_result].format(hour(), cls.virus)
                    try:
                        server_msg = Network.send_and_recv(cls.anti_virus, msg, cls.aes)
                    except ProtocolError as e:
                        print_colored(Prefixes.ERROR, e)
                        cls.exit()
                    print_colored(Prefixes.SERVER, server_msg)

                try:
                    time.sleep(cls.delay)
                except KeyboardInterrupt:
                    cls.exit()


    @classmethod
    def exit(cls) -> NoReturn:
        print_colored(Prefixes.INFO, Messages.CTRL_C)
        try:
            server_msg = Network.send_and_recv(cls.anti_virus, Messages.DISCONNECTION, cls.aes)
        except ProtocolError as e:
            print_colored(Prefixes.ERROR, e)
            exit()
        if server_msg != Messages.OK:
            print_colored(Prefixes.WARNING, f'Server sent: {server_msg}. Expected: {Messages.OK}')
        print_colored(Prefixes.ANTI_VIRUS, Messages.DISCONNECTION)
        exit()


if __name__ == '__main__':
    AntiVirus.run()
