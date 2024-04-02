from colorama import init, Fore, Style
from typing import Tuple, List, Dict, Callable

#### Colored Printing ####

init()

colors = {
    'Server': Fore.LIGHTBLACK_EX,
    'Client': Fore.BLUE,
    'Anti virus': Fore.CYAN,
    'Info': Fore.RESET,
    'Warning': Fore.YELLOW,
    'Error': Fore.LIGHTRED_EX
}

def colorful_str(color: str, prefix: str, msg: str, sock_id: int = 0) -> str:
    if sock_id == 0:
        return f"{Style.BRIGHT}{color}[{prefix}]: {msg}{Style.RESET_ALL}"
    else:
        return f"{Style.BRIGHT}{color}[{prefix}({sock_id})]: {msg}{Style.RESET_ALL}"

def print_colored(prefix: str, msg: str, lock = None, sock_id: int = 0):
    prefix = prefix.capitalize()
    color = colors.get(prefix, Fore.WHITE)
    string = colorful_str(color, prefix, msg, sock_id)
    if lock == None:
        print(string)
    else:
        lock.acquire()
        print(string)
        lock.release()
