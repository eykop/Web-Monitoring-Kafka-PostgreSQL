"""
Helper Module to read configuration file.

Acknowledgement:
some of the code is based on the tutorial form https://www.postgresqltutorial.com/postgresql-python
"""
import os
from configparser import ConfigParser
from .exceptions import ConfigurationFileNotFoundException, ConfigurationSectionMissingException


def get_config(config_file_path: str, section: str) -> dict:
    """
    Loads configurations from ini file.
    :param config_file_path: full file path for the ini file to parse.
    :param section: the ini section of the configuration to read.
    :return: dict: the configuration key,value pairs.
    """
    if not os.path.exists(config_file_path):
        raise ConfigurationFileNotFoundException("Configuration file '%s' was not found." % config_file_path)
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(config_file_path)

    # get section, default to postgresql
    configs = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            configs[param[0]] = param[1]
    else:
        raise ConfigurationSectionMissingException('Section {0} not found in the {1} file'.format(section, config_file_path))

    return configs

