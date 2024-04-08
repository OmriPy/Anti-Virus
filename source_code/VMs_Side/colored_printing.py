from colorama import init as _init, Fore as _Fore, Style as _Style
from typing import Tuple, List, Dict, Callable, Optional

#### Colored Printing ####

_init()

_colors = {
    'Server': _Fore.LIGHTBLACK_EX,
    'User': _Fore.BLUE,
    'Anti virus': _Fore.CYAN,
    'Info': _Fore.RESET,
    'Database': _Fore.GREEN,
    'Warning': _Fore.YELLOW,
    'Error': _Fore.LIGHTRED_EX
}

def _colorful_str(color: str, prefix: str, msg: str, sock_id: int = 0, username: str = '') -> str:
    if username != '':
        return f"{_Style.BRIGHT}{color}[{prefix} ({username})]: {msg}{_Style.RESET_ALL}"
    elif sock_id != 0:
        return f"{_Style.BRIGHT}{color}[{prefix}({sock_id})]: {msg}{_Style.RESET_ALL}"
    else:
        return f"{_Style.BRIGHT}{color}[{prefix}]: {msg}{_Style.RESET_ALL}"

def print_colored(prefix: str, msg: str, lock = None, sock_id: int = 0, username: str = ''):
    prefix = prefix.capitalize()
    color = _colors.get(prefix, _Fore.WHITE)
    string = _colorful_str(color, prefix, msg, sock_id, username)
    if lock == None:
        print(string)
    else:
        lock.acquire()
        print(string)
        lock.release()
