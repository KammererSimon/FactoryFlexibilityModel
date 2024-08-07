# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: Scenario.py
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

# SCENARIO

import os
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

        self.global_co2_limit = None

        # read in parameters.txt
        if scenario_file is not None:
            self._import_scenario(scenario_file)

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
