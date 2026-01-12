from time import sleep
from typing import Dict

import requests

from devices.servomotor import Serial
from utils.config import (
    load_config,
    save_config,
    CONFIG_LOCK,
    CONFIG,
    CONFIG_PATH,
    update_pubnub_token_in_config,
)
from utils.logger import get_logger
from vendors.pubnub_client import PubNubClient

logger = get_logger()
CONFIG_LOCK = CONFIG_LOCK

CURRENT_SERVO_POSITION = {}

PUBNUB_CLIENT = PubNubClient(
    sub_key=CONFIG["pubnub"]["subscribe-key"],
    pub_key=CONFIG["pubnub"]["publish-key"],
    sensor_id=CONFIG["device-id"],
    chanel_name=CONFIG["pubnub"]["channel-name"],
    access_token=CONFIG["pubnub"]["access-token"],
    server_url=CONFIG["server-url"],
    certification_string=CONFIG["certificate-string"],
    config_update_callback=update_pubnub_token_in_config,
)


def pubnub_channel_boot(cfg: Dict) -> None:
    if cfg["pubnub"]["channel-name"] is None:
        url: str = f"{cfg['server-url']}/device/register"
        response: requests.Response = requests.post(
            url=url,
            json={
                "device-id": cfg["device-id"],
            },
            headers={
                "certificate-string": cfg["certificate-string"],
                "device-id": cfg["device-id"],
            },
        )
        if not response.ok:
            raise RuntimeError("Device certification failed")

        cfg["pubnub"]["channel-name"] = response.json()["channel"]
        cfg["pubnub"]["access-token"] = response.json()["token"]


def handle_pubnub_message(message: Dict) -> None:
    global CURRENT_SERVO_POSITION, CONFIG_LOCK

    request_type = message.get("request_type", None)

    if request_type == "change_servomotors_position":
        angles = message.get("servomotors-angle")
        with CONFIG_LOCK:
            cfg = load_config(CONFIG_PATH)
            cfg["servomotors-angle"] = angles
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
    CURRENT_SERVO_POSITION = cfg["servomotors-angle"]

    PUBNUB_CLIENT.subscribe(message_handler=handle_pubnub_message)
    logger.info("Subscribed to PubNub channel for threshold updates")

    servo_console = Serial()

    while True:
        sleep(0.1)

        with CONFIG_LOCK:
            snapshot = dict(CURRENT_SERVO_POSITION)

        if snapshot:
            servo_console.move(snapshot["x-axis"], snapshot["y-axis"])
