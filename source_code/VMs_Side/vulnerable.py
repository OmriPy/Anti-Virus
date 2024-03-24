#!/usr/bin/python3
from os import system, listdir, sep
from typing import List


def list_directory() -> List[str]:
    file_name = __file__.split(sep)[-1]
    available_files = listdir()
    available_files.remove(file_name)
    return available_files

def cat_cmd(file_name: str) -> str:
    return f"`which cat` {file_name}"


def main():
    print(
        "Welcome!\n" + \
        "I'm a beginner coder and I'm currenly learning about System Calls in python.\n" + \
        "In this mini-project I'm focusing on the system syscall.\n" + \
        "I feel like it gives me an opportunity to explore the file system using python code.\n")
    print(f"Here is a list of the available files you can view:\n{list_directory()}\n")
    file_name = input("Enter the name of the file you would like to print its contents: ")
    command = cat_cmd(file_name)
    system(command)


if __name__ == '__main__':
    main()
