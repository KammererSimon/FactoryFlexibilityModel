# This script fulfills the single task to read in config files for the factory
# and to return the contained parameters as a dictionary

# IMPORT
import configparser
import logging


# Code start
def read_config(filepath: str):
    """
    This function takes a filepath as input argument that points to a valid factorymodel config.
    The specified config file is opened using the configparser library.
    All parameters given in the config are transferred into a config-dictionary which is returned as output
    :param filepath: path to a valid factorymodel config
    :return: config as dict.
    """

    # open the specified file
    config = configparser.ConfigParser()

    # read the contained parameters
    config.read("config.ini")

    if config["LOGS"]["logging_level"] == "debug":
        logging.basicConfig(level=logging.DEBUG)
    elif config["LOGS"]["logging_level"] == "info":
        logging.basicConfig(level=logging.INFO)
    elif config["LOGS"]["logging_level"] == "warning":
        logging.basicConfig(level=logging.WARNING)
    elif config["LOGS"]["logging_level"] == "error":
        logging.basicConfig(level=logging.ERROR)
    elif config["LOGS"]["logging_level"] == "critical":
        logging.basicConfig(level=logging.CRITICAL)

    # return the dictionary
    return config

    # TODO: implement inputvalidations!!
