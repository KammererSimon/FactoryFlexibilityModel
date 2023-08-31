# SCENARIO
# This script contains the scenario class wich is used to factory the outer circumstances for a simulation

# IMPORT
import logging


# CODE START
class Scenario:
    def __init__(self, *, parameter_file: str = None, timeseries_file: str = None):
        # read in parameter.txt
        if parameter_file is not None:
            self.import_parameters(parameter_file)

    def import_parameters(self, parameter_file: str) -> bool:
        """
        This function opens the .txt file given as "parameter_file" and returns the contained parameters as a dictionary with one key/value pair per parameter specified
        :param parameter_file: [string] Path to a .txt file containing the key/value pairs
        :return: [boolean] True if import was successfull
        """

        # initialize self.parameters
        self.parameters = {}

        try:
            # open the given file
            with open(parameter_file) as file:
                # iterate over all lines in the file
                for line in file:
                    key, value = line.strip().split("\t")
                    # add entry to parameters-dict
                    self.parameters[key] = float(value.replace(",", "."))
        except:
            logging.error(
                f"The given file is not a valid parameters.txt-config file! ({parameter_file})"
            )
            raise Exception
