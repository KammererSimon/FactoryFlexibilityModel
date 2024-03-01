# IMPORTS
from tkinter import filedialog

import numpy as np
import pandas as pd

from factory_flexibility_model.ui.utility.GUI_logging import log_event


# FUNCTIONS
def import_timeseries_xlsx(app):
    """
    This function lets the user choose an excel file containing timeseries and imports all of them to the current session.
    If keys are redundant, the timeseries from the file are enumerated to make them unique.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # make sure that there is a session initialized
    if app.session_data["session_path"] is None:
        # inform the user
        log_event(
            app,
            "Cannot import timeseries before a session has been created or imported!",
            "ERROR",
            "The user tried to import a timeseries file and got the following warning:",
        )
        return

    # ask for filename
    filetype = [("xlsx", "*.xlsx")]
    filepath = filedialog.askopenfilename(defaultextension=filetype, filetypes=filetype)

    # abort if the user didn't select any file
    if filepath == "":
        log_event(
            app, f"Aborted timeseries importing because no file was selected.", "DEBUG"
        )
        return

    # import the excel sheet
    try:
        imported_timeseries = pd.read_excel(filepath)
    except:
        log_event(
            app,
            f"Could not import file '{filepath}'. Make sure it is a valid .xlsx file with the standard timeseries format.",
            "ERROR",
            "The user tried to import a timeseries file and got the following warning:",
        )
        return

    for timeseries_key, timeseries_values in imported_timeseries.items():
        # make sure, that the key is unique
        if timeseries_key in app.session_data["timeseries"].keys():
            index = 1
            while f"{timeseries_key}_{index}" in app.session_data["timeseries"].keys():
                index += 1
            timeseries_key = f"{timeseries_key}_{index}"
        app.session_data["timeseries"][timeseries_key] = {
            "description": timeseries_values[0],
            "type": timeseries_values[1],
            "values": np.array(timeseries_values[2:].dropna()).tolist(),
        }
    # inform the user
    log_event(
        app,
        f"{len(app.session_data['timeseries'].keys())} new timeseries imported from '{filepath}'",
        "INFO",
    )
