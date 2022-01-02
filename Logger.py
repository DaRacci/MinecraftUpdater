from colorama import Fore, init


init()
debug_mode = False


def debug(msg):
    if debug_mode is True:
        print(Fore.CYAN + f"DEBUG: {msg}")


def error(msg):
    print(Fore.RED + f"ERROR: {msg}")
