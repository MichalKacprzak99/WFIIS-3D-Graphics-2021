import json
from functools import singledispatch
from pathlib import Path
from types import SimpleNamespace
from typing import List, Union


@singledispatch
def wrap_namespace(ob) -> SimpleNamespace:
    return ob


@wrap_namespace.register(dict)
def _wrap_dict(ob) -> SimpleNamespace:
    return SimpleNamespace(**{k: wrap_namespace(v) for k, v in ob.items()})


@wrap_namespace.register(list)
def _wrap_list(ob) -> List[SimpleNamespace]:
    return [wrap_namespace(v) for v in ob]


def load_configuration(config_file: Union[Path, str] = None) -> SimpleNamespace:
    """Loads json configuration file and validates against json schema.
    :param config_file: path to config file
    :return: configuration data
    """
    if not config_file:
        config_file = Path(__file__).parent / 'animation_config.json'
    with open(config_file) as fp:
        config_data = json.load(fp)

        return wrap_namespace(config_data)
