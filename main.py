try:
    from typing import List
    from wakeonlan import send_magic_packet
    from signal import signal, SIGINT, SIGTERM, Signals
    import subprocess
    import json
    from os.path import exists, realpath
    from os import curdir
    from time import sleep
    from sys import argv
    from smdb_logger import Logger
    from threading import Event
except Exception as ex:
    print("Please install the requirements.txt")
    print(ex)
    exit(1)


class ConfigException(Exception):
    pass


class DifferentLenghtException(Exception):
    def __init__(self) -> None:
        super().__init__("The computer IPs and MACs should have the same length!")


logger = Logger("keep-server-awake.log", ".", level="DEBUG",
                log_to_console=True, storage_life_extender_mode=True, max_logfile_size=500)
stop_event = Event()

class Config:
    def __init__(self, ips: List[str], macs: List[str], local_broadcast_address: str, wait_between_ping: int, log_folder: str, log_level: str, do_ensurance: bool = False):
        self.ips = ips
        self.macs = macs
        self.local_broadcast_address = local_broadcast_address
        self.wait_between_ping = wait_between_ping
        self.log_folder = log_folder
        self.log_level = log_level
        self.do_ensurance = do_ensurance

    def load(file_path: str) -> 'Config':
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            return Config(config['computers']["ips"], config['computers']["macs"], config["local broadcast address"], int(config["wait between pings in seconds"]), config["log folder"], config["log level"], config["do ensurance"])
        except Exception as ex:
            raise ConfigException(ex.args)


def ping(ip_address: str) -> bool:
    logger.debug(f"Pinging the following IP: {ip_address}")
    command = ['ping', '-c', '1', ip_address]
    return subprocess.call(command) == 0


def send_wol(mac_address: str, local_broadcast_address: str) -> None:
    logger.info(f"Waking {mac_address}")
    send_magic_packet(mac_address, ip_address=local_broadcast_address)


def signal_handler(signal: int, _):
    logger.debug(
        f"Incoming termination signal ({Signals(signal).name}), exiting gracefully.")
    logger.flush_buffer()
    stop_event.set()
    exit(0)


def main():
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
    "log level":"INFO",
    "do ensurance": "false"
}""")
        logger.info(
            f'Config file created.\nPlease fill in the config.conf file in "{realpath(curdir)}" with the relevant info.')
        raise ConfigException("No configuration file was present!")
    logger.debug("Loading configuration")
    config: Config = Config.load(config_path)
    if len(config.ips) != len(config.macs):
        logger.error("The computer IPs and MACs should have the same length!")
        raise DifferentLenghtException
    logger.info(f"Started with {len(config.ips)} server(s) set.")
    try:
        logger.set_level(config.log_level)
        logger.set_folder(config.log_folder)
    except Exception as ex:
        raise ConfigException(ex.args)
    if (config.do_ensurance):
        try:
            from threading import Thread
            ensurance_thread = Thread(target=ensurance, name="Ensurance")
            ensurance_thread.start()
        except:
            logger.error("Ensurance was enabled, but could not start!")
    while not stop_event.is_set():
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


def setup_signal_handlers():
    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)

def ensurance():
    import socket
    logger.debug("Starting ensurance")
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _socket.bind(("0.0.0.0", 9999))
    _socket.listen()
    while not stop_event.is_set():
        (connection, _) = _socket.accept()
        connection.send(b"HTTP/1.0 418\r\nContent-Length: 0\r\n\r\n")
        connection.close()

if __name__ == "__main__":
    try:
        logger.debug("Creating signal handlers...")
        setup_signal_handlers()
        logger.debug("Starting main method...")
        main()
    except Exception as ex:
        logger.error(f"Exception occured: {ex}")
    finally:
        logger.flush_buffer()
        stop_event.set()
