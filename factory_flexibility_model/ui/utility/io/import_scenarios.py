# This script contains the function "import_scenarios()" which is being called from basic_session_functions.load_session() when the user imports an old session into the GUI
import logging

# IMPORTS
import os

import yaml


# CODE START
def import_scenarios(folder_path):
    r"""
    This function checks the scenario folder under the folder_path for scenarios stored as .sc files.
    First an empty dict for storing scenarios is initialized
    Then all files found in folder_path are imported and the contained scenarios are transformed into a dictionary entry within the scenario dict.
    There must be a scenario "default.sc" within the folder. If none is found, an empty scenario is added to the scenario dict under the key "defaul".

    :param folder_path: [str] filepath to the \scenarios subfolder of the current session
    :return: [dict] containing all scenarios as sub-dicts
    """

    # initialize empty scenario dict
    scenario_dict = {}

    # iterate over all files within the scenario-dict
    for scenario_file in os.listdir(folder_path):

        # only consider .sc files
        if not scenario_file.endswith(".sc"):
            # create debug logger message for unknown file
            logging.debug(
                f"Invalid file found in scenario folder: '{scenario_file}' is not a valid scenario file"
            )
            continue

        # open file
        with open(f"{folder_path}/{scenario_file}") as file:
            # set the key for the new scenario as the string in front of the .sc suffix
            dict_key = os.path.splitext(scenario_file)[0]
            # import the parameters of the scenario to the scenario dict under the defined key
            scenario_dict[dict_key] = yaml.load(file, Loader=yaml.SafeLoader)

    # make sure that there is a default scenario
    if "default" not in scenario_dict:
        scenario_dict["default"] = {}
        logging.debug(
            f"No default file was found for the imported session. The default scenario is being initialized as empty"
        )

    # return scenario dict
    return scenario_dict
