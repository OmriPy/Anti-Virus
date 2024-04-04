from protocol import *
import os, subprocess, platform

def operating_system() -> str:
    return platform.system() # Windows, Linux, Darwin

def output_of_command(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True).decode()

def filter_matches(proc_name: str, lst: List[str]) -> List[str]:
    found = []
    for proc in lst:
        if proc_name in proc:
            found.append(proc)
    return found

def find_pids(processes: List[str]) -> List[int]:
    pids = []
    for proc in processes:
        '''if operating_system() == 'Windows':
            pids.append(int(proc[?]))
        else:
            pids.append(int(proc[:5]))'''
        pids.append(int(proc[:5]))
    return pids

def kill_procs(pids: List[int]) -> bool:
    for pid in pids:
        try:
            os.kill(pid, 9)    # 9 = signal.SIGKILL
        except PermissionError:
            print_colored('anti virus', 'Virus could not be killed')
            return False
        except ProcessLookupError:
            print_colored('anti virus', 'Another Anti Virus has already killed the virus')
            return False
    print_colored('anti virus', 'Virus killed')
    return True
