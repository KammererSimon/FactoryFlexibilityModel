# This file contains the basic functions required to create, save and load sessions within the factory model gui.


import csv

# IMPORTS
import os
from tkinter import filedialog
from tkinter.messagebox import askyesno

import yaml
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

import factory_flexibility_model.factory.Blueprint as bp
from factory_flexibility_model.ui.dialogs.dialog_new_session import (
    show_new_session_dialog,
)


# FUNCTIONS
def initiate_new_session(app):
    """
    This function is called when the user clicks on the "new session" button within the main menu.
    It checks, if there are unsaved changes within the session.
    If not, the show_new_session_dialog function is called to ask the user to specify the new session.
    Otherwise a dialog is created that asks the user whether he wants to cancel, save or dismiss the
    changes on the current session.
    :param app: Pointer to the current factory_GUIApp-instance
    """
    # First: Ask for user confirmation if there are unsaved changes to the currently opened factory
    if app.unsaved_changes_on_session:
        # If there are unsaved changes: create a dialog and ask the user what to do...
        # create buttons for the dialog
        btn_cancel = MDFlatButton(text="Cancel")
        btn_dismiss = MDRaisedButton(
            text="Dismiss changes and continue", md_bg_color="red"
        )
        btn_save = MDRaisedButton(text="Save changes and continue")

        # create dialog
        app.dialog = MDDialog(
            title="Unsaved changes on session",
            text="There are unsaved changes within the current session which will be deleted. ",
            buttons=[btn_cancel, btn_dismiss, btn_save],
        )

        # bind callbacks to buttons
        btn_cancel.bind(on_release=app.dialog.dismiss)  # abort without doing anything
        btn_dismiss.bind(
            on_release=lambda instance: show_new_session_dialog(app)
        )  # open the dialog to ask the user for name and path
        btn_save.bind(on_release=lambda instance: save_session(app))  # save the session
        btn_save.bind(
            on_release=lambda instance: show_new_session_dialog(app)
        )  # open the dialog to ask the user for name and path

        # open the dialog
        app.dialog.open()

    else:
        show_new_session_dialog(app)


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


def create_new_session(app):
    """
    This function creates a new session. It reads out all the user inputs from the currently opened dialog_new_session.
    If the values are valid the dialog is closed and a blank session is being created at the user given filepath.
    Then a new blueprint is created, saved under app.blueprint and the basic units and flowtypes are being initialized.
    Finally all app parameters and the gui are resettet into a neutral state.
    :param app: Pointer to the current factory_GUIApp-instance
    """
    # get requested name, description and directory
    session_name = app.dialog.content_cls.ids.textfield_new_session_name.text
    try:
        path = app.dialog.content_cls.ids.label_session_folder.text
    except:
        path = rf"{os.getcwd()}\sessions"

    # close the previous dialog
    app.dialog.dismiss()

    # create the new session directory
    create_session_folder(path, session_name=session_name)
    app.session_data["session_path"] = rf"{path}\{session_name}"

    # create an empty blueprint and add the given information
    app.blueprint = bp.Blueprint()
    app.blueprint.info["name"] = session_name

    # initialize units and flowtypes
    app.initialize_units_and_flowtypes()

    # reset the session timeseries list
    app.session_data["timeseries"] = {}
    app.session_data["show_component_config_dialog_on_creation"] = False

    # set the selected asset to none
    app.selected_asset = None

    # initialize the GUI
    app.initialize_visualization()
    app.update_flowtype_list()
    app.root.ids.asset_config_screens.current = "welcome_screen"
    app.root.ids.label_session_name.text = session_name

    # New session has not been saved yet
    app.unsaved_changes_on_session = True
    app.unsaved_changes_on_asset = False

    # inform the user
    Snackbar(
        text=f"New Session '{session_name}' created under '{app.session_data['session_path']}'"
    ).open()


def save_session(app):
    """
    This function saves the current session within the session_path by first calling the save routine of
    the blueprint class to store the layout, units and flowtypes.
    Then the parameter-dict of the session is parsed into a .txt file and stored in the same folder.
    :param app: Pointer to the current factory_GUIApp-instance
    """

    # make sure that there is no open dialog
    app.close_dialog()

    # make sure that there is a session to save
    if app.session_data["session_path"] is None:
        app.show_info_popup(
            "Cannot save before a session has been created or imported!"
        )
        return

    # SAVE SESSION DATA
    with open(
        f"{app.session_data['session_path']}\\{app.blueprint.info['name']}.ffm",
        "w",
    ) as file:
        yaml.dump(app.session_data, file)

    # SAVE THE BLUEPRINT
    app.blueprint.save(path=app.session_data["session_path"])

    # CREATE parameters.txt, timeseries.txt and demands.txt
    entries_parameters = []
    entries_timeseries = []
    entries_demands = {}
    # iterate over all components
    for key_component, dict_parameters in app.session_data["parameters"].items():
        # make sure that there are parameters to save
        if dict_parameters is None:
            continue
        # iterate over all parameters of the current component
        for key_parameter, dict_variations in dict_parameters.items():
            # iterate over all variations given for the current parameter
            for index, variation in dict_variations.items():
                # handle static values
                if variation["type"] == "static":
                    entries_parameters.append(
                        f"{key_component}/{key_parameter}\t{variation['value']}\n"
                    )

                # handle timeseries
                elif variation["type"] == "timeseries":
                    row = [key_component, key_parameter]
                    values = app.session_data["timeseries"][variation["value"]][
                        "values"
                    ]
                    if (
                        app.session_data["timeseries"][variation["value"]]["type"]
                        == "full"
                        or len(values) >= app.blueprint.info["timesteps"]
                    ):
                        row.extend(values[0 : app.blueprint.info["timesteps"]])
                    else:
                        row.extend(values)
                    entries_timeseries.append(row)

                # handle demands
                elif variation["type"] == "demands":
                    # make sure that component key exists within entries_demands
                    if key_component not in entries_demands.keys():
                        entries_demands[key_component] = {}
                    # add values of current variation to the dict
                    entries_demands[key_component][index] = variation["value"]

    # write files
    with open(f"{app.session_data['session_path']}\\parameters.txt", "w") as file:
        for line in entries_parameters:
            file.write(line)
    with open(
        f"{app.session_data['session_path']}\\timeseries.csv", "w", newline=""
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(entries_timeseries)
    with open(
        f"{app.session_data['session_path']}\\demands.txt",
        "w",
    ) as file:
        yaml.dump(entries_demands, file)

    # There are no more unsaved changes now...
    app.unsaved_changes_on_session = False

    Snackbar(
        text=f"Session successfully saved at {app.session_data['session_path']}"
    ).open()


def save_session_as(app):
    """
    This function is used to create a copy of a session.
    The function is bein called out of the save_session_as-dialog after the user has specified a new name and path
    for the session. Those values are read out of the dialog, the dialog is closed, the info gets written into the
    sessions blueprint. Then the regular save_session() method is being called
    """

    # get requested name, description and directory
    session_name = app.dialog.content_cls.ids.textfield_new_session_name.text
    session_description = (
        app.dialog.content_cls.ids.textfield_new_session_description.text
    )
    try:
        path = app.dialog.content_cls.ids.filechooser_new_session.selection[0]
    except:
        path = rf"{os.getcwd()}\sessions"

    # close the dialog
    app.dialog.dismiss()

    # create the new session directory
    create_session_folder(path, session_name=session_name)

    # update the session info
    app.session_data["session_path"] = rf"{path}\{session_name}"
    app.blueprint.info["description"] = session_description
    app.blueprint.info["name"] = session_name
    app.root.ids.label_session_name.text = session_name

    # call the regular safe session routine
    save_session(app)


def load_session(app):
    """
    This function loads a session from a file
    :param app: Pointer to the current factory_GUIApp-instance
    """

    # ask for user confirmation if there are unsaved changes to the currently opened factory
    if app.unsaved_changes_on_session:
        if not askyesno(
            title="Unsaved Changes",
            message="There are unsaved changes in the currently opened factory which will be deleted. "
            "Do you want to continue?",
        ):
            return

    # ask for filename
    filetype = [("ffm", "*.ffm")]
    filepath = filedialog.askopenfilename(defaultextension=filetype, filetypes=filetype)

    # make sure the user didn't abort the file selection or selected something invalid
    if filepath is None or filepath == "":
        return

    # IMPORT session data
    with open(filepath) as file:
        app.session_data = yaml.load(file, Loader=yaml.SafeLoader)

    app.session_data["session_path"] = os.path.dirname(filepath)

    # IMPORT blueprint including flowtypes and units
    try:
        blueprint_new = bp.Blueprint()
        blueprint_new.import_from_file(app.session_data["session_path"])
    except:
        Snackbar(
            text=f"ERROR: Importing Blueprint from {app.session_data['session_path']} failed!"
        ).open()
        return

    # Did all imports work till here? -> Overwrite internal attributes
    app.blueprint = blueprint_new

    # There are no more unsaved changes now...
    app.unsaved_changes_on_session = False
    app.unsaved_changes_on_asset = False

    # there is no component selected initially
    app.selected_asset = None

    # update the GUI to display the data
    app.root.ids.asset_config_screens.current = "welcome_screen"
    app.root.ids.label_session_name.text = app.blueprint.info["name"]
    app.initialize_visualization()
    app.update_flowtype_list()
