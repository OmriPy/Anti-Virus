from anti_virus_utils import *
import time

class AntiVirus:

    server_ip = '127.0.0.1'
    virus = 'lab_rat.py'
    delay = 10
    possibilities: Dict[Tuple[bool, bool], str] = {
        (False, False): 'No virus detected',
        (True, True): 'The virus was detected and killed successfully',
        (True, False): 'The virus was detected but could not be killed'
    }

    @classmethod
    def run(cls):
        with Protocol.connected_socket(cls.server_ip) as anti_virus:
            print_colored('info', 'Anti Virus has connected to the server')

            # Verify connection with the server
            server_msg = send_and_recv(anti_virus, Messages.ANTI_VIRUS)
            if server_msg != Messages.OK:
                print_colored('server', server_msg)
                print_colored('error', 'The server sent a message that is not OK. Exiting')
                return
            
            # Main loop
            while True:
                try:
                    time.sleep(cls.delay)
                except KeyboardInterrupt:
                    try:
                        send_and_recv(anti_virus, Messages.CONNECTION_CLOSED)
                    except ProtocolError as e:
                        print_colored('error', e)
                        return
                    print_colored('anti virus', Messages.CONNECTION_CLOSED)
                    print_colored('info', Messages.CTRL_C)
                    return
                
                # Perform virus scanning and send results to the server
                virus_proc = FindAndKillProcess(cls.virus)
                killing_result = virus_proc.kill()
                if killing_result[0]:   # If a virus was found
                    msg = cls.possibilities[killing_result]
                    server_msg = send_and_recv(anti_virus, msg)
                    print_colored('server', server_msg)


if __name__ == '__main__':
    AntiVirus.run()
