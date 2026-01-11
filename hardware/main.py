import json
import logging
import threading
from pathlib import Path
from time import sleep
from typing import Dict

import requests

from devices.servomotor import Servo
from vendors.pubnub_client import PubNubClient

logging.basicConfig(
    filename='./logfile.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
config_lock = threading.Lock()
stop_flag = False
lock = threading.Lock()


def load_config(path: Path) -> Dict:
    with open(path) as f:
        return json.load(f)


def save_config(path: Path, cfg: Dict) -> None:
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)


def update_pubnub_token_in_config(new_token: str) -> None:
    with config_lock:
        cfg = load_config(CONFIG_PATH)
        cfg['pubnub']['access-token'] = new_token
        save_config(CONFIG_PATH, cfg)
        logger.info("Updated PubNub access token in config file")


CONFIG_PATH = Path(__file__).parent / "config.json"
CONFIG = load_config(CONFIG_PATH)

CURRENT_SERVO_POSITION = {}

PUBNUB_CLIENT = PubNubClient(
    sub_key=CONFIG['pubnub']['subscribe-key'],
    pub_key=CONFIG['pubnub']['publish-key'],
    sensor_id=CONFIG['device-id'],
    chanel_name=CONFIG['pubnub']['channel-name'],
    access_token=CONFIG['pubnub']['access-token'],
    server_url=CONFIG['server-url'],
    certification_string=CONFIG['certificate-string'],
    config_update_callback=update_pubnub_token_in_config
)


def pubnub_channel_boot(cfg: Dict) -> None:
    if cfg["pubnub"]["channel-name"] is None:
        url: str = f"{cfg['server-url']}/device/register"
        response: requests.Response = requests.post(
            url=url,
            json={
                "device-id": cfg["device-id"],
            },
            headers={"certificate-string": cfg['certificate-string'], "device-id": cfg['device-id']}

        )
        if not response.ok:
            raise RuntimeError("Device certification failed")

        cfg["pubnub"]["channel-name"] = response.json()["channel"]
        cfg["pubnub"]["access-token"] = response.json()["token"]


def handle_pubnub_message(message: Dict) -> None:
    global CURRENT_SERVO_POSITION, config_lock

    request_type = message.get("request_type", None)

    if request_type == "change_servomotors_position":
        angles = message.get("servomotors-angle")
        with config_lock:
            cfg = load_config(CONFIG_PATH)
            cfg['servomotors-angle'] = angles
            save_config(CONFIG_PATH, cfg)
            CURRENT_SERVO_POSITION = angles
            logger.info(f"Updated angles in config: {angles}")


def boot(cfg: Dict) -> Dict:
    # TODO connect to home wifi if not registered
    # wifi_boot()

    pubnub_channel_boot(cfg)
    return cfg


if __name__ == "__main__":
    logger.info("Program launched")
    cfg = load_config(CONFIG_PATH)
    cfg = boot(cfg)
    save_config(CONFIG_PATH, cfg)
    cfg = load_config(CONFIG_PATH)
    CURRENT_SERVO_POSITION = cfg['servomotors-angle']

    PUBNUB_CLIENT.subscribe(message_handler=handle_pubnub_message)
    logger.info("Subscribed to PubNub channel for threshold updates")

    x_servo = Servo(18)
    y_servo = Servo(15)

    while True:
        sleep(0.1)

        with config_lock:
            snapshot = dict(CURRENT_SERVO_POSITION)

        if snapshot:
            if x_servo.current_angle() != snapshot['x-axis']:
                x_servo.set_angle(snapshot['x-axis'])
            if y_servo.current_angle() != snapshot['y-axis']:
                y_servo.set_angle(snapshot['x-axis'])