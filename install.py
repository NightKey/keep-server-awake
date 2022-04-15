import main
from os import getcwdb
import subprocess

try:
    with open("keep-server-awake.service.template", 'r') as f:
        service = f.read(-1)
    service.replace(r"{file_path}", f'{getcwdb().decode("utf-8")}/main.py')
    with open("/etc/systemd/system/keep-server-awake.service", "w") as f:
        f.write(service)
    subprocess.call(["sudo", "systemctle", "daemon-reload"])
    subprocess.call(["sudo", "systemctle", "enable", "keep-server-awake.service"])
    subprocess.call(["sudo", "systemctle", "start", "keep-server-awake.service"])
except Exception as ex:
    print("Service creation failed, please try starting this with sudo!")