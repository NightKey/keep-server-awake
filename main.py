try:
    from typing import List
    from wakeonlan import send_magic_packet
    import subprocess
    import json
    from os.path import exists, realpath
    from time import sleep
    from sys import argv
    from smdb_logger import Logger
except:
    print("Please install the requirements.txt")
    exit(1)


logger = Logger("keep-server-awake.log", "/var/log", level="DEBUG",
                log_to_console=True, storage_life_extender_mode=True, max_logfile_size=500)


class Config:
    def __init__(self, ips: List[str], macs: List[str], local_broadcast_address: str, wait_between_ping: int, log_folder: str, log_level: str):
        self.ips = ips
        self.macs = macs
        self.local_broadcast_address = local_broadcast_address
        self.wait_between_ping = wait_between_ping
        self.log_folder = log_folder
        self.log_level = log_level

    def load(file_path: str) -> 'Config':
        with open(file_path, "r") as f:
            config = json.load(f)
        return Config(config['computers']["ips"], config['computers']["macs"], config["local broadcast address"], int(config["wait between pings in seconds"]), config["log folder"], config["log level"])


def ping(ip_address: str) -> bool:
    command = ['ping', '-c', '1', ip_address]
    return subprocess.call(command) == 0


def send_wol(mac_address: str, local_broadcast_address: str) -> None:
    logger.info(f"Waking {mac_address}")
    send_magic_packet(mac_address, ip_address=local_broadcast_address)


def main(install_path: str):
    if install_path == "":
        install_path = "."
    config_path = f"{install_path}/config.conf"
    if not exists(config_path):
        logger.debug(f"Path: {config_path}")
        logger.warning("Config file not found, creating default config file")
        with open("config.conf", "w") as f:
            f.write("""{
    "computers": {
        "ips": [],
        "macs": []
    },
    "local broadcast address": "192.168.0.255",
    "wait between pings in seconds": "180",
    "log folder":"/var/log",
    "log level":"INFO"
}""")
        logger.info(
            f'Config file created.\nPlease fill in the config.conf file in "{realpath(install_path)}" with the relevant info.')
        exit(0)
    config = Config.load(config_path)
    logger.info(f"Started with {len(config.ips)} server(s) set.")
    logger.set_level(config.log_level)
    logger.log_folder = config.log_folder
    while True:
        try:
            for ip, mac in zip(config.ips, config.macs):
                if not ping(ip):
                    send_wol(mac, config.local_broadcast_address)
            sleep(config.wait_between_ping)
        except KeyboardInterrupt:
            logger.info("Interrupted by user!")
            break
        except Exception as ex:
            logger.info(f"Exception in main loop: {ex}")


if __name__ == "__main__":
    main('/'.join(argv[-1].split('/')[:-1]))
