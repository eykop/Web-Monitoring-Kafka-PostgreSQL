"""
Module that define custom exception for reading and parsing configuration file.
"""


class ConfigurationException(Exception):
    pass


class ConfigurationFileNotFoundException(ConfigurationException):
    pass


class ConfigurationSectionMissingException(ConfigurationException):
    pass


