from colorama import init, Fore, Style
from typing import Optional
from threading import Lock


def print_colored(
        prefix: str,
        msg: str,
        lock: Optional[Lock] = None,
        sock_id: Optional[int] = None,
        username: Optional[str] = None):
    """
    Prints a message to the console with a specific color based on the prefix provided. 
    The message can optionally include a socket ID or username for more detailed logging. 
    If a threading lock is provided, the printing will be thread-safe.

    Parameters:
    - prefix (str): The category of the message which determines the color of the text.
    - msg (str): The message to be printed.
    - lock (optional): A threading lock object to ensure thread-safe printing. Defaults to None.
    - sock_id (int, optional): The socket ID associated with the message.
      Defaults to 0, indicating no socket ID.
    - username (str, optional): The username associated with the message.
      Defaults to an empty string, indicating no username.

    Returns:
    - None
    """
    string = ColoredPrint.colored_string(prefix, msg, sock_id, username)
    if lock:
        lock.acquire()
        print(string)
        lock.release()
    else:
        print(string)


class Prefixes:
    
    SERVER = 'Server'
    USER = 'User'
    ANTI_VIRUS = 'Anti virus'
    INFO = 'Info'
    DATABASE = 'Database'
    DEBUG = 'Debug'
    WARNING = 'Warning'
    ERROR = 'Error'


class ColoredPrint:

    colors = {
        Prefixes.SERVER: Fore.LIGHTBLACK_EX,
        Prefixes.USER: Fore.BLUE,
        Prefixes.ANTI_VIRUS: Fore.CYAN,
        Prefixes.INFO: Fore.RESET,
        Prefixes.DATABASE: Fore.GREEN,
        Prefixes.DEBUG: Fore.LIGHTBLUE_EX,
        Prefixes.WARNING: Fore.YELLOW,
        Prefixes.ERROR: Fore.LIGHTRED_EX
    }


    @classmethod
    def init(self):
        init(autoreset=True)


    @classmethod
    def colored_string(cls,
                       prefix: str,
                       msg: str,
                       sock_id: Optional[int],
                       username: Optional[str]) -> str:
        color = cls.colors.get(prefix, Fore.WHITE)
        if username:
            return f"{Style.BRIGHT}{color}[{prefix} ({username})]: {msg}"
        elif sock_id:
            return f"{Style.BRIGHT}{color}[{prefix}({sock_id})]: {msg}"
        else:
            return f"{Style.BRIGHT}{color}[{prefix}]: {msg}"


if __name__ != '__main__':
    ColoredPrint.init()
