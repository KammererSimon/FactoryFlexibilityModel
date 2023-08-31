# SCENARIO
# This script contains the scenario class wich is used to factory the outer circumstances for a Simulation

# IMPORT
import logging


# CODE START
class Scenario:
    def __init__(
        self,
        *,
        parameter_file: str = None,
        timefactor: int = 1,
        timeseries_file: str = None,
    ):

        # set timefactor
        self.timefactor = timefactor

        # read in parameters.txt
        if parameter_file is not None:
            self.import_parameters(parameter_file)
        else:
            self.parameters = {}

        # read in timeseries.txt
        if timeseries_file is not None:
            self.import_timeseries(timeseries_file)
        else:
            self.timeseries = {}

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

    def import_timeseries(self, timeseries_file: str) -> bool:
        """
        This function opens the .txt file given as "timeseries_file" and returns the contained timeseries as a dictionary with one key: [array] pair per timeseries specified
        :param timeseries_file: [string] Path to a .txt file containing the key: [array] pairs
        :return: [boolean] True if import was successfull
        """

        # initialize self.parameters
        self.timeseries = {}

        try:
            # open the given file
            with open(timeseries_file) as file:
                # iterate over all lines in the file
                for line in file:
                    # parse current line
                    items = line.split("\t")

                    # first item of the line is the key
                    key = items[0]

                    # remaining line is the value array
                    values = [float(x.replace(",", ".")) for x in items[1:]]

                    # add entry to parameters-dict
                    self.timeseries[key] = values
        except:
            logging.error(
                f"The given file is not a valid timeseries.txt-config file! ({timeseries_file})"
            )
            raise Exception
