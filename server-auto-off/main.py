from time import sleep
import requests
from typing import Union
from subprocess import call, DEVNULL
from sys import argv


target_ip: Union[str, None] = None

def check():
    fail_count = 0
    while True:
        command = ['ping', '-n', '1', target_ip]
        if call(command, stdout=DEVNULL, stderr=DEVNULL) != 0:
            fail_count += 1
            print(f"Check failed {fail_count} times.")
        else:
            if (fail_count != 0): print(f"Check succeeded after {fail_count} failiure.")
            fail_count = 0

        if fail_count == 5:
            call(["shutdown", "/s", "/f", "/t", "0", "/d", "u:7:0"])

        sleep(24)

if __name__=="__main__":
    if "-ip" not in argv:
        print(f"usage: '{__file__} -ip [IPv4 ADDRESS]'")
        input("press return to exit")
        exit(1)
    print("Starting checker")
    target_ip = argv[argv.index('-ip') + 1]
    check()
