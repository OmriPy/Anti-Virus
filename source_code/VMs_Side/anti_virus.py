import os
import subprocess
from typing import List

virus = 'WhatsApp'

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

def kill_procs(pids: List[int]):
    for pid in pids:
        try:
            os.kill(pid, 9)    # 9 = signal.SIGKILL
        except PermissionError:
            print('Virus could not be killed.')
            return
    print('Virus killed.')

def find_and_kill_process(process_name: str):
    output = output_of_command('ps -A')
    procs = output.split('\n')
    found = filter_matches(process_name, procs)
    if len(found) == 0:
        print('Virus was not detected.')
        return
    print('Virus detected!')
    pids = find_pids(found)
    kill_procs(pids)


def main():
    find_and_kill_process(virus)

if __name__ == '__main__':
    main()
