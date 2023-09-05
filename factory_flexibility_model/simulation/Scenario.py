# SCENARIO

# IMPORT
import os


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

        self.configurations = {}

        # read in parameters.txt
        if parameter_file is not None:
            self.import_parameters(parameter_file)

        # read in timeseries.txt
        if timeseries_file is not None:
            self.import_timeseries(timeseries_file)

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

        try:
            # open the given file
            with open(timeseries_file) as file:
                # iterate over all lines in the file
                for line in file:
                    # parse current line
                    items = line.split("\t")

                    # first item of the line is the key
                    key = items[0].split("/")

                    # remaining line is the value array
                    values = [float(x.replace(",", ".")) for x in items[1:]]

                    # add a component entry in the parameters dict if this is the first setting for a component
                    if not key[0] in self.configurations:
                        self.configurations[key[0]] = {}
                    # add entry to parameters-dict
                    self.configurations[key[0]][key[1]] = values
        except:
            raise ValueError(
                f"The given timeseries.txt-config file is invalid, has a wrong format or is corrupted! ({timeseries_file})"
            )
