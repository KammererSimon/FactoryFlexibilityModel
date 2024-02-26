# SCENARIO

import csv
import os

import numpy as np
import yaml


# CODE START
class Scenario:
    """
    .. _Scenario:
        Represents a scenario for a simulation.

        This class defines a simulation scenario and provides methods for importing parameters,
        timeseries data, and scheduler demands.

        Attributes:
            +-----------------+--------------------------------------------------------+
            | Attribute       | Description                                            |
            +=================+========================================================+
            | session_folder  | A string representing the session folder path.         |
            +-----------------+--------------------------------------------------------+
            | timefactor      | An integer representing the time factor (default: 1).  |
            +-----------------+--------------------------------------------------------+
            | cost_co2_per_kg | The cost of CO2 per kilogram (default: 0).             |
            +-----------------+--------------------------------------------------------+
            | configurations  | A dictionary to store simulation configurations.       |
            +-----------------+--------------------------------------------------------+

        Methods:
            +-------------------+--------------------------------------------------------+
            | Method            | Description                                            |
            +===================+========================================================+
            | _import_parameters| Import parameters from 'parameters.txt' in the session |
            |                   | folder and populate the 'configurations' dictionary.   |
            +-------------------+--------------------------------------------------------+
            | _import_timeseries| Import timeseries data from 'timeseries.csv' in the    |
            |                   | session folder.                                        |
            +-------------------+--------------------------------------------------------+
            | _import_demands   | Import scheduler demands from 'demands.txt' in the     |
            |                   | session folder.                                        |
            +-------------------+--------------------------------------------------------+

        Example:
            Creating Scenario object:

            >>> my_scenario = Scenario(session_folder="path/to/session")
    """

    def __init__(
        self,
        scenario_file: str,
        *,
        timefactor: int = 1,
    ):

        # set timefactor
        self.timefactor = timefactor

        # set co2-costs
        self.cost_co2_per_kg = 0

        self.configurations = {}

        # read in parameters.txt
        if scenario_file is not None:
            self._import_scenario(scenario_file)

        # # read in timeseries.txt
        # timeseries_file = rf"{session_folder}\timeseries.csv"
        # if timeseries_file is not None:
        #     self._import_timeseries(timeseries_file)
        #
        # # read in scheduler demands
        # demands_file = rf"{session_folder}\demands.txt"
        # if timeseries_file is not None:
        #     self._import_demands(demands_file)

    def _import_scenario(self, scenario_file: str) -> bool:
        """
        This function opens the .txt file given as "parameter_file" and returns the contained parameters as a dictionary with one key/value pair per parameter specified
        :param parameter_file: [string] Path to a .txt file containing the key/value pairs
        :return: [boolean] True if import was successfull
        """

        # Make sure that the requested file exists
        if not os.path.exists(scenario_file):
            raise FileNotFoundError(
                f"Requested timeseries.txt-file does not exists: {scenario_file}"
            )

        try:
            # open the given file
            with open(scenario_file) as file:
                # write the imported dict with specified parameters to self.configurations
                self.configurations = yaml.load(file, Loader=yaml.SafeLoader)
        except:
            raise ValueError(
                f"The given parameters.txt-config file is invalid, has a wrong format or is corrupted! ({scenario_file})"
            )

        # iterate over all components + their parameters and reduce them to just the relevant numerical or boolean value
        for component_key, component_parameters in self.configurations.items():
            for parameter_key, parameter_data in component_parameters.items():
                self.configurations[component_key][parameter_key] = parameter_data[
                    "value"
                ]

    def _import_timeseries(self, timeseries_file: str) -> bool:
        """
        This function opens the .txt file given as "timeseries_file" and returns the contained timeseries as a dictionary with one key: [array] pair per timeseries specified
        :param timeseries_file: [string] Path to a .txt file containing the key: [array] pairs
        :return: [boolean] True if import was successfull
        """

        # Make sure that the requested file exists
        if not os.path.exists(timeseries_file):
            raise FileNotFoundError(
                f"Requested timeseries.txt-file does not exists: {timeseries_file}"
            )

        with open(timeseries_file) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                print(row)
                key_component, key_parameter = row[0], row[1]
                values = np.array([float(value) for value in row[2:]])
                # make sure that the component key exists in the configurations dict
                if not key_component in self.configurations:
                    self.configurations[key_component] = {}
                self.configurations[key_component][key_parameter] = values
