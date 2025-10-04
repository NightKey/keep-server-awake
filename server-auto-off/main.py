from time import sleep
import requests
from typing import Union
from subprocess import run
from sys import argv


target_ip: Union[str, None] = None
fail_count = 0

def check():
    while True:
        response = requests.get(f"http://{target_ip}:9999")
        if response.status_code != 418:
            fail_count += 1
        else:
            fail_count = 0
        
        if fail_count == 5:
            run(["shutdown", "/s", "/f", "/t", "0", "/d", "u:7:0"])
        sleep(24)

if __name__=="__main__":
    if "-ip" not in argv:
        print(f"usage: '{__file__} -ip [IPv4 ADDRESS]'")
        input("press return to exit")
        exit(1)
    target_ip = argv[argv.index('-ip') + 1]
    check()
