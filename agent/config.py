import yaml
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("config/default.yaml")


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)