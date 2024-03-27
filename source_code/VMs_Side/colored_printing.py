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

def colorful_str(color: str, prefix: str, msg: str) -> str:
    return f"{Style.BRIGHT}{color}[{prefix}]: {msg}{Style.RESET_ALL}"

def print_colored(prefix: str, msg: str, lock = None):
    prefix = prefix.capitalize()
    if prefix[-1] == ')':
        color = colors.get(prefix[:-3], Fore.WHITE)
    else:
        color = colors.get(prefix, Fore.WHITE)
    string = colorful_str(color, prefix, msg)
    if lock == None:
        print(string)
    else:
        lock.acquire()
        print(string)
        lock.release()
