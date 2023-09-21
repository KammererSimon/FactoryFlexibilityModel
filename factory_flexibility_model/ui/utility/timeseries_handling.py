from tkinter import filedialog

import pandas as pd
from kivymd.uix.snackbar import Snackbar


def import_timeseries_xlsx(app):
    """
    This function lets the user choose an excel file containing timeseries and imports all of them to the tool
    """

    # ask for filename
    filetype = [("xlsx", "*.xlsx")]
    filepath = filedialog.askopenfilename(defaultextension=filetype, filetypes=filetype)

    if not filepath == "":
        # import the excel sheet
        app.timeseries = pd.read_excel(filepath)

    # inform the user
    Snackbar(text=f"{len(app.timeseries.keys())} new timeseries imported").open()
