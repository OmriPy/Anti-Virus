from colorama import init as _init, Fore as _Fore, Style as _Style

_init(autoreset=True)

_colors = {
    'Server': _Fore.LIGHTBLACK_EX,
    'User': _Fore.BLUE,
    'Anti virus': _Fore.CYAN,
    'Info': _Fore.RESET,
    'Database': _Fore.GREEN,
    'Debug': _Fore.LIGHTBLUE_EX,
    'Warning': _Fore.YELLOW,
    'Error': _Fore.LIGHTRED_EX
}

def _colorful_str(color: str, prefix: str, msg: str, sock_id: int = 0, username: str = '') -> str:
    if username != '':
        return f"{_Style.BRIGHT}{color}[{prefix} ({username})]: {msg}"
    elif sock_id != 0:
        return f"{_Style.BRIGHT}{color}[{prefix}({sock_id})]: {msg}"
    else:
        return f"{_Style.BRIGHT}{color}[{prefix}]: {msg}"

def print_colored(prefix: str, msg: str, lock = None, sock_id: int = 0, username: str = ''):
    """
    Prints a message to the console with a specific color based on the prefix provided. 
    The message can optionally include a socket ID or username for more detailed logging. 
    If a threading lock is provided, the printing will be thread-safe.

    Parameters:
    - prefix (str): The category of the message which determines the color of the text.
    - msg (str): The message to be printed.
    - lock (optional): A threading lock object to ensure thread-safe printing. Defaults to None.
    - sock_id (int, optional): The socket ID associated with the message. Defaults to 0, indicating no socket ID.
    - username (str, optional): The username associated with the message. Defaults to an empty string, indicating no username.

    Returns:
    - None
    """
    prefix = prefix.capitalize()
    color = _colors.get(prefix, _Fore.WHITE)
    string = _colorful_str(color, prefix, msg, sock_id, username)
    if lock:
        lock.acquire()
        print(string)
        lock.release()
    else:
        print(string)
