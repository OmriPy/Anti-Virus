from colorama import init, Fore, Style
from typing import Tuple, List, Dict, Callable
import os
import subprocess


#### Anti Virus Utility Functions ####

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
            print_colored('anti virus', 'Virus could not be killed')
            return False
    print_colored('anti virus', 'Virus killed')
    return True


#### Colored Printing ####

init()

colors = {
    'Server': Fore.LIGHTBLACK_EX,
    'Client': Fore.BLUE,
    'Anti virus': Fore.LIGHTGREEN_EX,
    'Info': Fore.CYAN,
    'Warning': Fore.YELLOW,
    'Error': Fore.LIGHTRED_EX
}

def print_colored(prefix: str, msg: str):
    prefix = prefix.capitalize()
    color = colors.get(prefix, Fore.WHITE)
    print(f"{Style.BRIGHT}{color}[{prefix}]: {msg}{Style.RESET_ALL}")