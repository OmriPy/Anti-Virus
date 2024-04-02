from antiVirusUtils import *
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
        with Protocol.connected_socket(cls.server_ip) as sock:
            print_colored('info', 'Anti Virus has connected to the server')

            # Verify connection with the server
            server_msg = send_and_recv(sock, Messages.ANTI_VIRUS)
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
                        send_and_recv(sock, Messages.CONNECTION_CLOSED)
                    except ProtocolError as e:
                        print_colored('error', e)
                        return
                    print_colored('anti virus', Messages.CONNECTION_CLOSED)
                    print_colored('info', Messages.CTRL_C)
                    return
                
                # Perform virus scanning and send results to the server
                killing_result = cls.find_and_kill_process(cls.virus)
                if killing_result[0]:   # If a virus was found
                    msg = cls.possibilities[killing_result]
                    server_msg = send_and_recv(sock, msg)
                    print_colored('server', server_msg)

    @classmethod
    def find_and_kill_process(cls, process_name: str) -> Tuple[bool, bool]:
        """Finds the given process and kills it. Returns a tuple containing two booleans: Found & Killed.
        
        Returns (False, False) if the process was not detected,
        (True, False) if the process was detected, but could not be killed,
        and (True, True) if it was detected and killed successfully."""
        
        ps_output = output_of_command('ps -A')
        procs = ps_output.split('\n')
        found_procs = filter_matches(process_name, procs)
        if len(found_procs) == 0:
            found = False
            killed = False
            print_colored('anti virus' ,'Virus was not detected')
        else:
            found = True
            print_colored('anti virus' ,'Virus detected')
            pids = find_pids(found_procs)
            killed = kill_procs(pids)
        return found, killed


if __name__ == '__main__':
    AntiVirus.run()
