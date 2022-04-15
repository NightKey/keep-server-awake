try:
    from platform import system
    from typing import List
    from wakeonlan import send_magic_packet
    import subprocess, json
    from datetime import datetime
    from os.path import exists
    from time import sleep
except:
    print("Please install the requirements.txt")
    exit(1)

class Config:
    def __init__(self, ips: List[str], macs: List[str], local_broadcast_address: str, wait_between_ping: int):
        self.ips = ips
        self.macs = macs
        self.local_broadcast_address = local_broadcast_address
        self.wait_between_ping = wait_between_ping

    def load() -> 'Config':
        with open("config.conf", "r") as f:
            config = json.load(f)
        return Config(config['computers']["ips"], config['computers']["macs"], config["local broadcast address"], int(config["wait between pings in seconds"]))

def log(mac_address: str) -> None:
    with open("log.lg", 'a') as f:
        f.write(f"Host ({mac_address}) was offlone at {datetime.now()}\n")

def ping(ip_address: str) -> bool:
    param = '-n' if system().lower() == "windows" else '-c'
    command = ['ping', param, '1', ip_address]
    return subprocess.call(command) == 0

def send_wol(mac_address: str, local_broadcast_address: str) -> None:
    log(mac_address)
    send_magic_packet(mac_address, ip_address=local_broadcast_address)

def main():
    if not exists("config.conf"):
        print("Config file not found, creating default config file")
        with open("config.conf", "w") as f:
            json.dump({'computers': {'ips': [], 'macs': []}, 'local broadcast address': '192.168.0.255', "wait between pings in seconds": '180'}, f)
        print('Config file created.\nPlease fill in the config.conf file besides the python file with the relevant info.')
        exit(0)
    config = Config.load()
    while True:
        for ip, mac in zip(config.ips, config.macs):
            if not ping(ip):
                send_wol(mac, config.local_broadcast_address)
        sleep(config.wait_between_ping)
    
if __name__ == "__main__":
    main()