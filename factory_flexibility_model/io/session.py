# this file contains all scripts used to create new session directories and to evaluate, if a directory is a valid session folder

# IMPORTS
import os


def create_session_folder(root_folder, session_name: str = "New Session"):
    """
    This function initializes a session folder with all required files and subfolders
    :param root_folder: [str] User given path where the new session folder shall be created
    :session_name: [str] Name for the new session == Name of the subfolder to be created
    """

    # Create path to the new session folder
    subfolder_path = os.path.join(root_folder, session_name)
    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)

    # create list of files to be initialized
    files = [
        "parameters.txt",
        "timeseries.txt",
        "flowtypes.txt",
        "units.txt",
        "Layout.factory",
    ]

    # create empty files
    for file in files:
        with open(os.path.join(subfolder_path, file), "w") as f:
            pass

    # create a subfolder for simulations
    simulations_path = os.path.join(subfolder_path, "simulations")
    if not os.path.exists(simulations_path):
        os.makedirs(simulations_path)
