from os import getcwd, sep

working_dir = getcwd() + sep

def full_path(file_name: str) -> str:
    return working_dir + file_name