import json
import threading
from pathlib import Path
from typing import Dict


def load_config(path: Path) -> Dict:
    with open(path) as f:
        return json.load(f)


def save_config(path: Path, cfg: Dict) -> None:
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)


CONFIG_LOCK = threading.Lock()
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
CONFIG = load_config(CONFIG_PATH)


def update_pubnub_token_in_config(new_token: str) -> None:
    with CONFIG_LOCK:
        cfg = load_config(CONFIG_PATH)
        cfg["pubnub"]["access-token"] = new_token
        save_config(CONFIG_PATH, cfg)
