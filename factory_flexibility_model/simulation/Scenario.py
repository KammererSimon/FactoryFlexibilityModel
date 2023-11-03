# SCENARIO

# IMPORT
import csv
import os

import numpy as np
import pandas as pd
import yaml


# CODE START
class Scenario:
    def __init__(
        self,
        session_folder: str,
        *,
        timefactor: int = 1,
    ):

        # set timefactor
        self.timefactor = timefactor

        # set co2-costs
        self.cost_co2_per_kg = 0

        self.configurations = {}

        # read in parameters.txt
        parameter_file = rf"{session_folder}\parameters.txt"
        if parameter_file is not None:
            self.import_parameters(parameter_file)

        # read in timeseries.txt
        timeseries_file = rf"{session_folder}\timeseries.csv"
        if timeseries_file is not None:
            self.import_timeseries(timeseries_file)

        # read in scheduler demands
        demands_file = rf"{session_folder}\demands.txt"
        if timeseries_file is not None:
            self.import_demands(demands_file)

    def import_parameters(self, parameter_file: str) -> bool:
        """
        This function opens the .txt file given as "parameter_file" and returns the contained parameters as a dictionary with one key/value pair per parameter specified
        :param parameter_file: [string] Path to a .txt file containing the key/value pairs
        :return: [boolean] True if import was successfull
        """

        # Make sure that the requested file exists
        if not os.path.exists(parameter_file):
            raise FileNotFoundError(
                f"Requested timeseries.txt-file does not exists: {parameter_file}"
            )

        try:
            # open the given file
            with open(parameter_file) as file:
                # iterate over all lines in the file
                for line in file:
                    # split line into key and value
                    key, value = line.strip().split("\t")
                    # split key into component and parameter
                    key = key.split("/")

                    # add a component entry in the parameters dict if this is the first setting for a component
                    if not key[0] in self.configurations:
                        self.configurations[key[0]] = {}
                    # add entry to parameters-dict
                    self.configurations[key[0]][key[1]] = float(value.replace(",", "."))
        except:
            raise ValueError(
                f"The given parameters.txt-config file is invalid, has a wrong format or is corrupted! ({parameter_file})"
            )

    def import_timeseries(self, timeseries_file: str) -> bool:
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

    def import_demands(self, demands_file: str) -> bool:
        """
        This function opens the .txt file given as "demands_file" and returns the contained demandlist as a dictionary with one key: [pd.df] pair per demand specified
        :param demand_file: [string] Path to a .txt file containing the key: [pd.df] pairs
        :return: [boolean] True if import was successfull
        """
        # open file
        with open(demands_file) as file:
            demands_data = yaml.load(file, Loader=yaml.SafeLoader)

        for key_component, demands in demands_data.items():
            for values in demands.values():
                # make sure that the component key exists in the configurations dict
                if not key_component in self.configurations:
                    self.configurations[key_component] = {}

                # write the dataframe to the configurations dict
                self.configurations[key_component]["demands"] = pd.DataFrame(
                    values
                ).to_numpy()

                print(self.configurations[key_component]["demands"])
