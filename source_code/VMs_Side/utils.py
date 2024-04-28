from typing import Tuple, List, Dict, Callable, Optional, NoReturn
from colored_printing import print_colored, Prefixes
from base64 import b64encode as _b64encode
from random import randbytes as _randbytes

def func_name(func: Callable, cls = None) -> str:
    if cls:
        return f'{cls.__name__}.{func.__name__}()'
    return f'{func.__name__}()'

def generate_random_string(size: int = 32) -> str:
    return _b64encode(_randbytes(size)).decode()
