from typing import Tuple, List, Dict, Callable, Optional

def func_name(func: Callable, cls = None) -> str:
    if cls:
        return f'{cls.__name__}.{func.__name__}()'
    return f'{func.__name__}()'