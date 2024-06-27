# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: Factory_Flexibility_Model
# File Name: factory_import.py
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
import logging
import pickle
from pathlib import Path

import factory_flexibility_model.factory.Factory as fm
import factory_flexibility_model.simulation.Simulation as fs


# MAIN FUNCTIONS
def import_factory(data_path: str):
    """
    This function takes a path to a stored factory_model.factory - object. The Factory is being imported and returned
    :param data_path: Path to a valid factory-object that has been created using factory.save()
    :return: factory_model.factory - object
    """

    # check, if the requested file exists
    file = Path(data_path)
    if not file.is_file():
        logging.critical(f"ERROR: The given file does not exist: {data_path}")
        raise Exception
    # open the given file
    with open(data_path, "rb") as f:
        imported_factory = pickle.load(f)

    # make sure that the imported data represents a factory-object
    if not isinstance(imported_factory, fm.factory):
        logging.critical(
            f"ERROR: The given file does not contain a factory_model.factory-object"
        )
        raise Exception

    logging.info("FACTORY IMPORT FROM FILE SUCCESSFUL")

    # Return the imported factory
    return imported_factory


def import_simulation(data_path: str):
    """
    This function takes a path to a stored Simulation - object. The Simulation is being imported and returned
    :param data_path: Path to a valid Simulation-object that has been created using Simulation.save()
    :return: fsimulation.Simulation - object
    """

    # check, if the requested file exists
    file = Path(data_path)
    if not file.is_file():
        logging.critical(f"ERROR: The given file does not exist: {data_path}")
        raise Exception
    # open the given file
    with open(data_path, "rb") as f:
        imported_simulation = pickle.load(f)

    # make sure that the imported data represents a factory-object
    if not isinstance(imported_simulation, fs.Simulation):
        logging.critical(
            f"ERROR: The given file does not contain a Simulation.Simulation-object"
        )
        raise Exception

    logging.info("SIMULATION IMPORT FROM FILE SUCCESSFUL")

    # Return the imported Simulation
    return imported_simulation
