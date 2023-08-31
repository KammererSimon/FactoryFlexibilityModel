# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations

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
    This function takes a path to a stored simulation - object. The Simulation is being imported and returned
    :param data_path: Path to a valid simulation-object that has been created using simulation.save()
    :return: fsimulation.simulation - object
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
    if not isinstance(imported_simulation, fs.simulation):
        logging.critical(
            f"ERROR: The given file does not contain a simulation.simulation-object"
        )
        raise Exception

    logging.info("SIMULATION IMPORT FROM FILE SUCCESSFUL")

    # Return the imported simulation
    return imported_simulation
