from tkinter import filedialog

import pandas as pd
from kivymd.uix.snackbar import Snackbar


def import_timeseries_xlsx(app):
    """
    This function lets the user choose an excel file containing timeseries and imports all of them to the current session.
    If keys are redundant, the timeseries from the file are enumerated to make them unique.
    """

    # ask for filename
    filetype = [("xlsx", "*.xlsx")]
    filepath = filedialog.askopenfilename(defaultextension=filetype, filetypes=filetype)

    if not filepath == "":
        # import the excel sheet
        imported_timeseries = pd.read_excel(filepath)

        for timeseries_key, timeseries_values in imported_timeseries.items():
            # make sure, that the key is unique
            if timeseries_key in app.timeseries.keys():
                index = 1
                while f"{timeseries_key}_{index}" in app.timeseries.keys():
                    index += 1
                timeseries_key = f"{timeseries_key}_{index}"
            app.timeseries[timeseries_key] = timeseries_values

        # inform the user
        Snackbar(text=f"{len(app.timeseries.keys())} new timeseries imported").open()
