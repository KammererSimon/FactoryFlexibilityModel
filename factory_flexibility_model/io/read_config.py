# This script fulfills the single task to read in config files for the factory
# and to return the contained parameters as a dictionary

# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: Factory_Flexibility_Model
# File Name: read_config.py
#
# Copyright (c) [2024]
# [Institute of Energy Systems, Energy Efficiency and Energy Economics
#  TU Dortmund
#  Simon Kammerer (simon.kammerer@tu-dortmund.de)]
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------

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
