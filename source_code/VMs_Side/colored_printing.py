from colorama import init, Fore, Style
from typing import Tuple, List, Dict, Callable, Optional

__all__ = ['Tuple', 'List', 'Dict', 'Callable', 'Optional', 'print_colored']

#### Colored Printing ####

init()

colors = {
    'Server': Fore.LIGHTBLACK_EX,
    'User': Fore.BLUE,
    'Anti virus': Fore.CYAN,
    'Info': Fore.RESET,
    'Database': Fore.GREEN,
    'Warning': Fore.YELLOW,
    'Error': Fore.LIGHTRED_EX
}

def colorful_str(color: str, prefix: str, msg: str, sock_id: int = 0, username: str = '') -> str:
    if username != '':
        return f"{Style.BRIGHT}{color}[{prefix} ({username})]: {msg}{Style.RESET_ALL}"
    elif sock_id != 0:
        return f"{Style.BRIGHT}{color}[{prefix}({sock_id})]: {msg}{Style.RESET_ALL}"
    else:
        return f"{Style.BRIGHT}{color}[{prefix}]: {msg}{Style.RESET_ALL}"

def print_colored(prefix: str, msg: str, lock = None, sock_id: int = 0, username: str = ''):
    prefix = prefix.capitalize()
    color = colors.get(prefix, Fore.WHITE)
    string = colorful_str(color, prefix, msg, sock_id, username)
    if lock == None:
        print(string)
    else:
        lock.acquire()
        print(string)
        lock.release()
