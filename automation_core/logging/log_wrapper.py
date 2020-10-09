import logging
import logging.config
from pathlib import Path

import yaml

config = None


def read_config_from_yaml():
    global config
    if config is None:
        path = str(Path(__file__).parent.parent) + '/logging/logging.yml'
        config = yaml.safe_load(open(path))
    return config


def logger(context='app') -> logging.Logger:
    logging.config.dictConfig(read_config_from_yaml())
    return logging.getLogger(context)
