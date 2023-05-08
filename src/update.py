#!/usr/bin/python3

import os
import time
import subprocess

snapshot = subprocess.check_output("/usr/local/sbin/ast c", shell=True)
while True:
    if os.path.exists(f"/.snapshots/rootfs/snapshot-chr{snapshot}"):
        time.sleep(20)
    else:
        subprocess.run(
            shell=True,
            check=True,
            args="/usr/local/sbin/ast clone $(/usr/local/sbin/ast c)",
        )
        subprocess.run(shell=True, check=True, args="/usr/local/sbin/ast auto-upgrade")
        subprocess.run(shell=True, check=True, args="/usr/local/sbin/ast base-update")
        break

upstate = open("/.snapshots/ast/upstate")
line = upstate.readline()
upstate.close()

if "1" not in line:
    subprocess.run(
        shell=True,
        check=True,
        args="/usr/local/sbin/ast deploy $(/usr/local/sbin/ast c)",
    )
