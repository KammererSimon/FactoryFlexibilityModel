# IMPORTS
from tkinter import filedialog

import pandas as pd
from kivymd.uix.snackbar import Snackbar


def import_scheduler_demands(app):
    """
    This function imports an xlsx file containing a matrix with demands and writes them as .demands for the currently selected scheduler
    :param app: pointer to the current FactoryGUI instance
    """

    # ask for filename
    filetype = [("xlsx", "*.xlsx")]
    filepath = filedialog.askopenfilename(defaultextension=filetype, filetypes=filetype)

    if not filepath == "":
        # import the excel sheet
        imported_demands = pd.read_excel(
            filepath, usecols="A:D", header=None, skiprows=1
        )

        # make sure that the key "demands" exists within the parameter list of the current compoent
        if (
            "demands"
            not in app.session_data["parameters"][app.selected_asset["key"]].keys()
        ):
            app.session_data["parameters"][app.selected_asset["key"]]["demands"] = {}

        # create a key to adress the variation
        # variation = 0
        # while variation in app.session_data["parameters"][app.selected_asset["key"]]["demands"].keys():
        #    variation += 1
        # TODO: activate multiple variations again when the model is capable of handling them

        variation = 0

        app.session_data["parameters"][app.selected_asset["key"]]["demands"][
            variation
        ] = {"type": "demands", "value": imported_demands.to_dict()}

        # inform the user
        Snackbar(text=f"Excelfile successfully imported").open()
