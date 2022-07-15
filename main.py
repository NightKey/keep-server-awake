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


class ConfigException(Exception):
    pass


class DifferentLenghtException(Exception):
    def __init__(self) -> None:
        super().__init__("The computer IPs and MACs should have the same length!")


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
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            return Config(config['computers']["ips"], config['computers']["macs"], config["local broadcast address"], int(config["wait between pings in seconds"]), config["log folder"], config["log level"])
        except Exception as ex:
            raise ConfigException(ex.args)


def ping(ip_address: str) -> bool:
    logger.debug(f"Pinging the following IP: {ip_address}")
    command = ['ping', '-c', '1', ip_address]
    return subprocess.call(command) == 0


def send_wol(mac_address: str, local_broadcast_address: str) -> None:
    logger.info(f"Waking {mac_address}")
    send_magic_packet(mac_address, ip_address=local_broadcast_address)


def main(install_path: str):
    config_path = "config.conf"
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
        raise ConfigException("No configuration file was present!")
    logger.debug("Loading configuration")
    config = Config.load(config_path)
    if len(config.ips) != len(config.macs):
        logger.error("The computer IPs and MACs should have the same length!")
        raise DifferentLenghtException
    logger.info(f"Started with {len(config.ips)} server(s) set.")
    try:
        logger.set_level(config.log_level)
        logger.set_folder(config.log_folder)
    except Exception as ex:
        raise ConfigException(ex.args)
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
    try:
        main()
    except Exception as ex:
        logger.error(f"Exception occured: {ex}")
    finally:
        logger.flush_buffer()
