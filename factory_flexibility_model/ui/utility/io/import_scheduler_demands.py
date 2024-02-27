# This script contains the function import_scheduler_demands. The function is being called via an callback event that is created for parameter-config.list items within the parameter config tab.
# The binding is initialized during layout_component_configuration_tab.update_update_component_configuration_tab

# IMPORTS
from tkinter import filedialog

import pandas as pd

from factory_flexibility_model.ui.utility.GUI_logging import log_event


# FUNCTIONS
def import_scheduler_demands(app):
    """
    This function imports an xlsx file containing a matrix with demands and writes them as .demands for the currently selected scheduler

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
        imported_demands = pd.read_excel(
            filepath, usecols="A:D", header=None, skiprows=1
        )
    except:
        # inform the user
        log_event(
            app,
            "Error during import of the given file. Please make sure, that the given file is in the specified standard format.",
            "ERROR",
        )

    # make sure all start and end times are integers
    if (
        not imported_demands[0].apply(lambda x: isinstance(x, int)).all()
        or not imported_demands[1].apply(lambda x: isinstance(x, int)).all()
    ):
        # inform the user
        log_event(
            app,
            "Cannot import scheduler demands, because at least one start or end time is not an integer",
            "ERROR",
        )
        return

    # make sure that no demand starts before timestep 1
    if (imported_demands[0] < 1).any():
        # inform the user
        log_event(
            app,
            "Cannot import scheduler demands, because at least one partdemand starts before timestep 1.",
            "ERROR",
        )
        return

    # write imported demands into the scenarios dict
    app.session_data["scenarios"][app.selected_scenario][app.selected_asset["key"]][
        "demands"
    ] = {"type": "demands", "value": imported_demands.to_dict()}

    # inform the user
    log_event(app, f"Given excel file with part demands successfully imported", "INFO")
