from protocol import *
import time

virus = 'lab_rat.py'
delay = 10

def find_and_kill_process(process_name: str) -> Tuple[bool, bool]:
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

possibilities: Dict[Tuple[bool, bool], str] = {
    (False, False): 'No virus detected',
    (True, True): 'The virus was detected and killed successfully',
    (True, False): 'The virus was detected, but could not be killed'
}

def main():
    with connected_socket('127.0.0.1') as sock:
        print_colored('info', 'Anti Virus has connected to the server')
        server_msg = send_and_recv(sock, Messages.ANTI_VIRUS_CONNECTED)
        if server_msg != Messages.OK:
            print_colored('error', 'The server sent a message that is not OK. Exiting')
            return
        while True:
            try:
                time.sleep(delay)
            except KeyboardInterrupt:
                send_and_recv(sock, Messages.CONNECTION_CLOSED)
                print_colored('anti virus', Messages.CONNECTION_CLOSED)
                print_colored('info', Messages.CTRL_C)
                return
            killing_result = find_and_kill_process(virus)
            if killing_result != (False, False):
                msg = possibilities[killing_result]
                server_msg = send_and_recv(sock, msg)
                print_colored('server', server_msg)


if __name__ == '__main__':
    main()
