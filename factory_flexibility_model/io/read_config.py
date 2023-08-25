# This script fulfills the single task to read in config files for the factory factory
# and to return the contained parameters as a dictionary

# IMPORT 3RD PARTY PACKAGES
import configparser


# Code start
def read_config(filepath: str):
    """
    This function takes a filepath as validate argument that points to a valid factorymodel config.
    The specified config file is opened using the configparser library.
    All parameters given in the config are transferred into a config-dictionary which is returned as output
    :param filepath: path to a valid factorymodel config
    :return: config as dict.
    """

    # open the specified file
    config = configparser.ConfigParser()

    # read the contained parameters
    config.read("config.ini")

    # return the dictionary
    return config

    # TODO: implement inputvalidations!!
