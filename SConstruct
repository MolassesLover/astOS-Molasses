#!/usr/bin/env scons

import colorama
from colorama import Fore
import os
import subprocess


def build():
    if bool(os.path.exists("/tmp/astOS-tmp")):
        print(
            f":: Directory {Fore.YELLOW}/tmp/astOS-tmp{Fore.RESET} exists, {Fore.RED}deleting{Fore.RESET} it."
        )

        subprocess.run(
            "sudo rm -fr /tmp/astOS-tmp",
            shell=True,
            stdout=subprocess.DEVNULL,
        )
    else:
        os.mkdir("/tmp/astOS-tmp")

    subprocess.run(
        shell=True,
        check=True,
        args="sudo mkarchiso -v -w /tmp/astOS-tmp live",
        stdout=subprocess.DEVNULL,
    )

match __name__:
    case "__main__":
        print(f":: Running as a {Fore.YELLOW}Python{Fore.RESET} script.")
        build()
    case "SCons.Script":
        print(f":: Running as a {Fore.YELLOW}SCons{Fore.RESET} script.")
        build()
    case "SConstruct":
        print(
            f":: {Fore.RED}Error{Fore.RESET}: The {Fore.YELLOW}SConstruct{Fore.RESET} file should not be used as a module."
        )
        sys.exit(1)
    case _:
        print(
            f":: {Fore.RED}Error{Fore.RESET}: The {Fore.YELLOW}SConstruct{Fore.RESET} script seems to have been used abnormally, exiting..."
        )
        sys.exit(1)
