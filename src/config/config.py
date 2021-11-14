import json
from functools import lru_cache
from pathlib import Path
from typing import Union


@lru_cache(maxsize=1)
def load_configuration(config_file: Union[Path, str] = None) -> dict:
    """Loads json configuration file and validates against json schema.
    :param config_file: path to config file
    :return: configuration data
    """
    if not config_file:
        config_file = Path(__file__).parent / 'animation_config.json'
    with open(config_file) as fp:
        config_data = json.load(fp)
        return config_data
