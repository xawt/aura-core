import yaml
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("config/default.yaml")


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))
