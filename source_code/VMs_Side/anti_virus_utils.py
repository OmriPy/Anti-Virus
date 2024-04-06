from protocol import *
import os, subprocess, platform


class OperatingSystems:

    WINDOWS = 'Windows'
    MAC_OS = 'Darwin'
    LINUX = 'Linux'

    @classmethod
    def active(cls) -> str:
        return platform.system()


class FindAndKillProcess:

    pid_index: Dict[str, int] = {
        OperatingSystems.WINDOWS: 1,
        OperatingSystems.MAC_OS: 0,
        OperatingSystems.LINUX: 0
    }

    commands: Dict[str, str] = {
        OperatingSystems.WINDOWS: 'tasklist /v',
        OperatingSystems.MAC_OS: 'ps -A',
        OperatingSystems.LINUX: 'ps -A'
    }


    def __init__(self, proc_name: str):
        """Object that finds the given process and kills it when hunt() is called"""

        self.target_proc = proc_name
        self.os = OperatingSystems.active()
        self.cmd = self.commands[self.os]


    def hunt(self) -> Tuple[bool, bool]:
        """Finds the given process and kills it. Returns a tuple containing two booleans: Found & Killed.
        
        Returns (False, False) if the process was not detected,
        (True, False) if the process was detected, but could not be killed,
        and (True, True) if it was detected and killed successfully."""
        
        all_procs = self._all_procs()
        found_procs = self._filter_target(all_procs)
        if len(found_procs) == 0:
            found = False
            killed = False
            print_colored('anti virus' ,'Virus was not detected')
        else:
            found = True
            print_colored('anti virus' ,'Virus detected')
            pids = self._pids_of_target(found_procs)
            killed = self._kill_target_procs(pids)
        return found, killed


    def _all_procs(self) -> List[str]:
        all_procs = subprocess.check_output(self.cmd, shell=True).decode()
        return all_procs.split('\n')

    def _filter_target(self, all_procs: List[str]) -> List[str]:
        found = []
        for proc in all_procs:
            if self.target_proc in proc:
                found.append(proc)
        return found

    def _pids_of_target(self, target_procs: List[str]) -> List[int]:
        pids = []
        for proc in target_procs:
            words = proc.split()
            pid_index = self.pid_index[self.os]
            pids.append(int(words[pid_index]))
        return pids

    def _kill_target_procs(self, pids: List[int]) -> bool:
        is_windows = self.os == OperatingSystems.WINDOWS
        if is_windows:
            for pid in pids:
                try:
                    subprocess.run(['taskkill', '/F', '/T', '/PID', f'{pid}'], check=True)
                except subprocess.CalledProcessError as e:
                    print_colored('error', f'Virus could not be killed: {e}')
                    return False
        else:
            for pid in pids:
                try:
                    os.kill(pid, 9)    # 9 = signal.SIGKILL
                except PermissionError:
                    print_colored('error', 'Virus could not be killed')
                    return False
                except ProcessLookupError:
                    print_colored('error', 'Another Anti Virus has already killed the virus')
                    return False
        print_colored('anti virus', 'Virus killed')
        return True
