import configparser
import json
import os
import re
from typing import List

from util import ssm_client_wrapper

ENVIRONMENT = os.getenv('ENVIRONMENT')
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'properties.ini'))
CONFIG.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'properties-{ENVIRONMENT}.ini'))

SSM_REGEX = re.compile('\$\{/.*\}')


def get_string_property(key: str, group: str = 'APP') -> str:
    value = CONFIG.get(group, key)
    matches = SSM_REGEX.match(value)
    if matches:
        parameter_store_key = value[2:][:-1]
        return ssm_client_wrapper.get_parameter_value(parameter_store_key)
    else:
        return value


def get_list_string_property(key: str, group: str = 'APP') -> List[str]:
    return get_string_property(key, group).split(",")


def get_dict_property(key: str, group: str = 'APP') -> dict:
    return json.loads(get_string_property(key, group))


def get_int_property(key: str, group: str = 'APP') -> int:
    value = CONFIG.get(group, key)
    return int(value)
