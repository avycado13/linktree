import toml
from db import Database
from typing import Any


def load_config(path="linktagger.toml"):
    # Load configuration
    config = toml.load(path)
    return config


def load_db(config: dict[str, Any]):
    if config["db"]["url"]:
        db = Database(config["db"]["url"])
    else:
        db = Database()
    return db
