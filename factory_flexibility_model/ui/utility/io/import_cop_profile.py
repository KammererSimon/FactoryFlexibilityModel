# This script contains the function import_scheduler_demands. The function is being called via an callback event that is created for parameter-config.list items within the parameter config tab.
# The binding is initialized during layout_component_configuration_tab.update_update_component_configuration_tab

# IMPORTS
from tkinter import filedialog

import pandas as pd

from factory_flexibility_model.ui.utility.GUI_logging import log_event


# FUNCTIONS
def import_cop_profile(app):

    """
       This function imports an xlsx file containing a vector of float values representing temperature depedant efficiencies and writes them as .cop_profile for the currently selected heatpump

       :param app: Pointer to the main factory_GUIApp-Object
       :return: None
       """

    # ask for filename
    filetype = [("xlsx", "*.xlsx")]
    filepath = filedialog.askopenfilename(defaultextension=filetype, filetypes=filetype)

    # abort if the user canceled the path-dialog
    if filepath == "":
        return

    # import the Excel sheet
    try:
        # import file under given path to a pandas dataframe
        data = pd.read_excel(
            filepath, usecols="A", header=None, skiprows=0
        )
        # convert profile to numpy array
        cop_profile = data[0].to_numpy(dtype=float).tolist()
    except:
        # inform the user
        log_event(
            app,
            "Error during import of the given file. Please make sure, that the given file is in the specified standard format.",
            "ERROR",
        )

    print(cop_profile)
    # write imported demands into the scenarios dict
    app.session_data["scenarios"][app.selected_scenario][app.selected_asset["key"]][
        "cop_profile"
    ] = {"type": "cop_profile", "value": cop_profile}

    # inform the user
    log_event(app, f"Given excel file with cop profile successfully imported", "INFO")
