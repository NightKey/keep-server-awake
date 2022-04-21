try:
    from typing import List
    from wakeonlan import send_magic_packet
    import subprocess, json
    from os.path import exists
    from time import sleep
    from datetime import datetime
    from sys import argv
except:
    print("Please install the requirements.txt")
    exit(1)

def log(message):
    with open("/var/log/keep-server-alive.log", 'a') as f:
        f.write(f"[{datetime.now()}]: {message}\n")

class Config:
    def __init__(self, ips: List[str], macs: List[str], local_broadcast_address: str, wait_between_ping: int, log_level: str):
        self.ips = ips
        self.macs = macs
        self.local_broadcast_address = local_broadcast_address
        self.wait_between_ping = wait_between_ping
        self.log_level = log_level

    def load(file_path: str) -> 'Config':
        with open(file_path, "r") as f:
            config = json.load(f)
        return Config(config['computers']["ips"], config['computers']["macs"], config["local broadcast address"], int(config["wait between pings in seconds"]), config["log level"])

def ping(ip_address: str) -> bool:
    command = ['ping', '-c', '1', ip_address]
    return subprocess.call(command) == 0

def send_wol(mac_address: str, local_broadcast_address: str) -> None:
    log(f"Waking {mac_address}")
    send_magic_packet(mac_address, ip_address=local_broadcast_address)

def main(install_path: str):
    if install_path == "": install_path = "."
    config_path = f"{install_path}/config.conf"
    if not exists(config_path):
        log(f"Path: {config_path}")
        print("Config file not found, creating default config file")
        with open("config.conf", "w") as f:
            json.dump({'computers': {'ips': [], 'macs': []}, 'local broadcast address': '192.168.0.255', "wait between pings in seconds": '180'}, f)
        print('Config file created.\nPlease fill in the config.conf file besides the python file with the relevant info.')
        exit(0)
    config = Config.load(config_path)
    log(f"Started with {len(config.ips)} server(s) set.")
    while True:
        try:
            for ip, mac in zip(config.ips, config.macs):
                if not ping(ip):
                    send_wol(mac, config.local_broadcast_address)
            sleep(config.wait_between_ping)
        except Exception as ex:
            log(f"Exception in main loop: {ex}")
        except KeyboardInterrupt:
            log("Interrupted by user!")
            break
if __name__ == "__main__":
    main('/'.join(argv[-1].split('/')[:-1]))