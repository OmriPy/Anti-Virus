from protocol import *
import os
import subprocess
import time
from typing import List, Dict


virus = 'WhatsApp'
delay = 5

#### Utility Functions ####

def output_of_command(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True).decode()

def filter_matches(string: str, lst: List[str]) -> List[str]:
    found = []
    for proc in lst:
        if string in proc:
            found.append(proc)
    return found

def find_pids(processes: List[str]) -> List[int]:
    pids = []
    for proc in processes:
        pids.append(int(proc[:5]))
    return pids

def kill_procs(pids: List[int]) -> bool:
    for pid in pids:
        try:
            os.kill(pid, 9)    # 9 = signal.SIGKILL
        except PermissionError:
            print('Virus could not be killed.')
            return False
    print('Virus killed.')
    return True


#### Main Functions ####

def find_and_kill_process(process_name: str) -> Tuple[bool]:
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
        print('Virus was not detected.')
    else:
        found = True
        print('Virus detected!')
        pids = find_pids(found_procs)
        killed = kill_procs(pids)
    return found, killed

possibilities: Dict[Tuple[bool], str] = {
    (False, False): 'No virus detected.',
    (True, True): 'The virus was detected and killed successfully.',
    (True, False): 'The virus was detected, but could not be killed'
}

def main():
    sock = connected_socket('127.0.0.1')    # TODO: think about the ip. on client VMs, the ip should not be localhost
    while True:
        try:
            time.sleep(delay)
        except KeyboardInterrupt:
            return
        killing_result = find_and_kill_process(virus)
        msg = possibilities[killing_result]
        print(send_and_recv(sock, msg))
        print()


if __name__ == '__main__':
    main()
