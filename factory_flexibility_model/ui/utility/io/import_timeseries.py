# IMPORTS
from tkinter import filedialog

import numpy as np
import pandas as pd
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar.snackbar import MDSnackbar

from factory_flexibility_model.ui.gui_components.info_popup.info_popup import (
    show_info_popup,
)


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
        show_info_popup(
            app,
            "Cannot import timeseries before a session has been created or imported!",
        )
        return

    # ask for filename
    filetype = [("xlsx", "*.xlsx")]
    filepath = filedialog.askopenfilename(defaultextension=filetype, filetypes=filetype)

    if not filepath == "":
        # import the excel sheet
        imported_timeseries = pd.read_excel(filepath)

        for timeseries_key, timeseries_values in imported_timeseries.items():
            # make sure, that the key is unique
            if timeseries_key in app.session_data["timeseries"].keys():
                index = 1
                while (
                    f"{timeseries_key}_{index}" in app.session_data["timeseries"].keys()
                ):
                    index += 1
                timeseries_key = f"{timeseries_key}_{index}"
            app.session_data["timeseries"][timeseries_key] = {
                "description": timeseries_values[0],
                "type": timeseries_values[1],
                "values": np.array(timeseries_values[2:].dropna()).tolist(),
            }
        # inform the user
        MDSnackbar(
            MDLabel(
                text=f"{len(app.session_data['timeseries'].keys())} new timeseries imported"
            )
        ).open()
