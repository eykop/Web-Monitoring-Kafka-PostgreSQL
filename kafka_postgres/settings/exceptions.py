"""
Module that define custom exception for reading and parsing configuration file.
"""


class ConfigurationBaseException(Exception):
    pass


class ConfigurationFileNotFoundException(ConfigurationBaseException):
    pass


class ConfigurationSectionMissingException(ConfigurationBaseException):
    pass


