from protocol import *
import os, subprocess, platform

class _OperatingSystems:

    WINDOWS = 'Windows'
    MAC_OS = 'Darwin'
    LINUX = 'Linux'

    @classmethod
    def active(cls) -> str:
        return platform.system()


class FindAndKillProcess:

    _pid_index: Dict[str, int] = {
        _OperatingSystems.WINDOWS: 1,
        _OperatingSystems.MAC_OS: 0,
        _OperatingSystems.LINUX: 1
    }

    _commands: Dict[str, str] = {
        _OperatingSystems.WINDOWS: 'tasklist /v',
        _OperatingSystems.MAC_OS: 'ps -A',
        _OperatingSystems.LINUX: 'ps aux'
    }


    def __init__(self, proc_name: str):
        """Object that finds the given process and kills it when hunt() is called"""

        self._target_proc = proc_name
        self._os = _OperatingSystems.active()
        self._cmd = self._commands[self._os]


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
        else:
            found = True
            print_colored(Prefixes.ANTI_VIRUS ,'Virus detected')
            pids = self._pids_of_target(found_procs)
            killed = self._kill_target_procs(pids)
        return found, killed


    def _all_procs(self) -> List[str]:
        all_procs = subprocess.check_output(self._cmd, shell=True).decode()
        return all_procs.split('\n')

    def _filter_target(self, all_procs: List[str]) -> List[str]:
        found = []
        for proc in all_procs:
            if self._target_proc in proc:
                found.append(proc)
        return found

    def _pids_of_target(self, target_procs: List[str]) -> List[int]:
        pids = []
        for proc in target_procs:
            words = proc.split()
            pid_index = self._pid_index[self._os]
            pids.append(int(words[pid_index]))
        return pids

    def _kill_target_procs(self, pids: List[int]) -> bool:
        is_windows = self._os == _OperatingSystems.WINDOWS
        if is_windows:
            for pid in pids:
                try:
                    subprocess.run(['taskkill', '/F', '/T', '/PID', f'{pid}'], check=True)
                except subprocess.CalledProcessError as e:
                    print_colored(Prefixes.WARNING, f'Virus could not be killed because: {e}')
                    return False
        else:
            for pid in pids:
                try:
                    os.kill(pid, 9)    # 9 = signal.SIGKILL
                except PermissionError:
                    print_colored(Prefixes.WARNING, 'Virus could not be killed')
                    return False
                except ProcessLookupError:
                    print_colored(Prefixes.WARNING, 'Another Anti Virus has already killed the virus')
                    return False
        print_colored(Prefixes.ANTI_VIRUS, 'Virus killed')
        return True
