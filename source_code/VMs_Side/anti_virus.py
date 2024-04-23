from anti_virus_utils import *
import time

class AntiVirus:

    server_ip = '127.0.0.1'
    virus = 'lab_rat.py'
    delay = 5
    possibilities: Dict[Tuple[bool, bool], str] = {
        (False, False): 'No virus detected',
        (True, True): 'The virus was detected and killed successfully',
        (True, False): 'The virus was detected but could not be killed'
    }

    @classmethod
    def run(cls):
        with Network.connected_socket(cls.server_ip) as anti_virus:
            print_colored('info', 'Anti Virus has connected to the server')

            # Verify connection with the server
            server_msg = Network.send_and_recv(anti_virus, Messages.IS_ANTI_VIRUS)
            if server_msg != Messages.OK:
                print_colored('server', server_msg)
                print_colored('error', 'The server sent a message that is not OK. Exiting')
                return
            print_colored('info', f'Virus is: {cls.virus}')

            # Main loop
            virus_proc = FindAndKillProcess(cls.virus)
            while True:
                # Perform virus scanning and send results to the server
                try:
                    killing_result = virus_proc.hunt()
                except KeyboardInterrupt:
                    print_colored('anti virus', 'Scanning was interrupted')
                    print_colored('info', Messages.CTRL_C)
                    return
                if killing_result[0]:   # If a virus was found
                    msg = cls.possibilities[killing_result]
                    try:
                        server_msg = Network.send_and_recv(anti_virus, msg)
                    except ProtocolError as e:
                        print_colored('error', e)
                        return
                    print_colored('server', server_msg)

                try:
                    time.sleep(cls.delay)
                except KeyboardInterrupt:
                    try:
                        Network.send_and_recv(anti_virus, Messages.DISCONNECTION)
                    except ProtocolError as e:
                        print_colored('error', e)
                        return
                    print_colored('anti virus', Messages.DISCONNECTION)
                    print_colored('info', Messages.CTRL_C)
                    return


if __name__ == '__main__':
    AntiVirus.run()
