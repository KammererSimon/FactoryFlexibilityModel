"""
This file contains the basic functions required to create, save and load sessions within the factory model gui.
"""

# IMPORTS
import os
from tkinter import filedialog
from tkinter.messagebox import askyesno

import yaml
from kivymd.uix.button import MDFlatButton

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.io.session as session
from factory_flexibility_model.ui.dialogs.unit_definition_dialog import *
from factory_flexibility_model.ui.utility.custom_widget_classes import *


# FUNCTIONS
def new_session(app, state):
    """
    This function contains everything related to the procedure of creating a new session.
    There are different paths that the function can take whoch are specified by "state".
    Some paths end up showing user selection screens that then call the function again with a different path.
    """

    # create partial functions for self recalls (necessary to suppres initial callbacks on .bind())
    def create(instance):
        new_session(app, "create")

    def safe(instance):
        new_session(app, "safe")

    def getname(instance):
        new_session(app, "getname")

    # Case distinction...
    if state == "start":  # user clicked on "new session"
        # First: Ask for user confirmation if there are unsaved changes to the currently opened factory
        if app.unsaved_changes_on_session:
            # create dialog
            btn_cancel = MDFlatButton(text="Cancel")
            btn_dismiss = MDRaisedButton(
                text="Dismiss changes and continue", md_bg_color="red"
            )
            btn_save = MDRaisedButton(text="Save changes and continue")
            app.dialog = MDDialog(
                title="Unsaved changes on session",
                text="There are unsaved changes within the current session which will be deleted. ",
                buttons=[btn_cancel, btn_dismiss, btn_save],
            )
            # bind callbacks to buttons
            btn_cancel.bind(on_release=app.dialog.dismiss)  # abort the procedure
            btn_dismiss.bind(
                on_release=getname
            )  # recall the function with the advice to directly create a new factory this time
            btn_save.bind(
                on_release=safe
            )  # recall the function with the advice to first safe the session
            app.dialog.open()
        else:
            new_session(app, "getname")

    if (
        state == "safe"
    ):  # user wants the current layout to be saved first before continuing with new session
        # close the warn dialog
        if hasattr(app, "dialog"):
            app.dialog.dismiss()

        # safe the session
        app.save_session()

        # recall the function with the advice to create new session
        app.new_session("getname")

    if state == "getname":  # create a new session
        # close the previous dialog
        if hasattr(app, "dialog"):
            if not app.dialog == None:
                app.dialog.dismiss()

        # create dialog
        btn_false = MDFlatButton(text="CANCEL")
        btn_true = MDRaisedButton(text="CREATE NEW SESSION")
        app.dialog = MDDialog(
            title="New Session",
            buttons=[btn_false, btn_true],
            type="custom",
            content_cls=dialog_new_session(),
        )
        # bind callbacks to buttons
        btn_true.bind(on_release=create)
        btn_false.bind(on_release=app.dialog.dismiss)
        app.dialog.open()

    if state == "create":  # create a new session
        # get requested name, description and directory
        session_name = app.dialog.content_cls.ids.textfield_new_session_name.text
        session_description = (
            app.dialog.content_cls.ids.textfield_new_session_description.text
        )
        try:
            path = app.dialog.content_cls.ids.filechooser_new_session.selection[0]
        except:
            path = rf"{os.getcwd()}\sessions"

        # close the previous dialog
        app.dialog.dismiss()

        # create the new session directory
        session.create_session_folder(path, session_name=session_name)
        app.session_data["session_path"] = rf"{path}\{session_name}"

        # create an empty blueprint and add the given information
        app.blueprint = bp.Blueprint()
        app.blueprint.info["name"] = session_name
        app.blueprint.info["description"] = session_description

        # initialize units and flowtypes
        app.initialize_units_and_flowtypes()

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

        # reset scenarios
        app.scenarios = {}
        app.root.ids.grid_scenarios.clear_widgets()

        # inform the user
        Snackbar(
            text=f"New Session '{session_name}' created under '{app.session_data['session_path']}'"
        ).open()


def save_session(app):
    """
    This function saves the current session within the session_path
    """
    # make sure that there is a factory to save:
    if len(app.blueprint.components) < 2 or len(app.blueprint.connections) < 1:
        # create dialog
        btn_ok = MDFlatButton(text="OK")
        app.dialog = MDDialog(
            title="Insufficient Components",
            text="There is no factory to safe yet! Add at least one flow, two components and a connection before saving.",
            buttons=[btn_ok],
        )
        btn_ok.bind(on_release=app.dialog.dismiss)
        app.dialog.open()
        return

    # save session data
    with open(
        f"{app.session_data['session_path']}\\{app.blueprint.info['name']}.ffm",
        "w",
    ) as file:
        yaml.dump(app.session_data, file)

    # save current blueprint
    app.blueprint.save(path=app.session_data["session_path"])

    # save parameters
    with open(f"{app.session_data['session_path']}\\parameters.txt", "w") as file:
        for key_outer, inner_dict in app.parameters.items():
            for key_inner, values in inner_dict.items():
                for value in values.values():
                    line = f"{key_outer}/{key_inner}\t{value}\n"
                    file.write(line)

    # There are no more unsaved changes now...
    app.unsaved_changes_on_session = False

    Snackbar(
        text=f"Session successfully saved at {app.session_data['session_path']}"
    ).open()

    def load_session(self):
        """
        This function loads a session from a file
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
        filepath = filedialog.askopenfilename(
            defaultextension=filetype, filetypes=filetype
        )

        # make sure the user didn't abort the file selection or selected something invalid
        if filepath == None or filepath == "":
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

        # IMPORT parameters
        try:
            # open the given file
            with open(f"{app.session_data['session_path']}\\parameters.txt") as file:
                parameters_new = {}
                for component_key in blueprint_new.components.keys():
                    parameters_new[component_key] = {}

                # initialize a counter that ensures, that every parameter within the factory gets a unique key assigned
                value_key = 0
                # iterate over all lines in the file
                for line in file:
                    # split line into key and value
                    key, value = line.strip().split("\t")
                    # split key into component and parameter
                    key = key.split("/")
                    # make sure that the parameters dict has an entry for the component and parameter
                    if key[1] not in parameters_new[key[0]].keys():
                        parameters_new[key[0]][key[1]] = {}
                    # add entry to parameters-dict
                    parameters_new[key[0]][key[1]][value_key] = float(
                        value.replace(",", ".")
                    )
                    # increment value_key to prevent double usage of keys
                    value_key += 1
        except:
            Snackbar(
                text=f"The given parameters.txt-config file is invalid, has a wrong format or is corrupted! ({app.session_data['session_path']}\\parameters.txt)"
            ).open()
            return

        # IMPORT timeseries
        try:
            # open the given file
            with open(f"{app.session_data['session_path']}\\timeseries.txt") as file:
                timeseries_new = {}
                # iterate over all lines in the file
                for line in file:
                    # parse current line
                    items = line.split("\t")

                    # first item of the line is the key
                    key = items[0].split("/")

                    # remaining line is the value array
                    values = [float(x.replace(",", ".")) for x in items[1:]]

                    # add a component entry in the parameters dict if this is the first setting for a component
                    if not key[0] in timeseries_new:
                        timeseries_new[key[0]] = {}
                    # add entry to parameters-dict
                    timeseries_new[key[0]][key[1]] = values
        except:
            Snackbar(
                text=f"The given timeseries.txt-config file is invalid, has a wrong format or is corrupted! ({app.session_data['session_path']}\\timeseries.txt)"
            ).open()
            return

        # Did all imports work till here? -> Overwrite internal attributes
        app.blueprint = blueprint_new
        app.parameters = parameters_new
        app.timeseries = timeseries_new

        # There are no more unsaved changes now...
        app.unsaved_changes_on_session = False
        app.unsaved_changes_on_asset = False

        # there is no component selected initially
        app.selected_asset = None

        # update the GUI to display the data
        app.root.ids.scenario_screens.current = "scenario_selection_screen"
        app.root.ids.asset_config_screens.current = "welcome_screen"
        app.root.ids.label_session_name.text = app.blueprint.info["name"]
        app.initialize_visualization()
        app.update_flowtype_list()


def load_session(app):
    """
    This function loads a session from a file
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
    if filepath == None or filepath == "":
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

    # IMPORT parameters
    try:
        # open the given file
        with open(f"{app.session_data['session_path']}\\parameters.txt") as file:
            parameters_new = {}
            for component_key in blueprint_new.components.keys():
                parameters_new[component_key] = {}

            # initialize a counter that ensures, that every parameter within the factory gets a unique key assigned
            value_key = 0
            # iterate over all lines in the file
            for line in file:
                # split line into key and value
                key, value = line.strip().split("\t")
                # split key into component and parameter
                key = key.split("/")
                # make sure that the parameters dict has an entry for the component and parameter
                if key[1] not in parameters_new[key[0]].keys():
                    parameters_new[key[0]][key[1]] = {}
                # add entry to parameters-dict
                parameters_new[key[0]][key[1]][value_key] = float(
                    value.replace(",", ".")
                )
                # increment value_key to prevent double usage of keys
                value_key += 1
    except:
        Snackbar(
            text=f"The given parameters.txt-config file is invalid, has a wrong format or is corrupted! ({app.session_data['session_path']}\\parameters.txt)"
        ).open()
        return

    # IMPORT timeseries
    try:
        # open the given file
        with open(f"{app.session_data['session_path']}\\timeseries.txt") as file:
            timeseries_new = {}
            # iterate over all lines in the file
            for line in file:
                # parse current line
                items = line.split("\t")

                # first item of the line is the key
                key = items[0].split("/")

                # remaining line is the value array
                values = [float(x.replace(",", ".")) for x in items[1:]]

                # add a component entry in the parameters dict if this is the first setting for a component
                if not key[0] in timeseries_new:
                    timeseries_new[key[0]] = {}
                # add entry to parameters-dict
                timeseries_new[key[0]][key[1]] = values
    except:
        Snackbar(
            text=f"The given timeseries.txt-config file is invalid, has a wrong format or is corrupted! ({app.session_data['session_path']}\\timeseries.txt)"
        ).open()
        return

    # Did all imports work till here? -> Overwrite internal attributes
    app.blueprint = blueprint_new
    app.parameters = parameters_new
    app.timeseries = timeseries_new

    # There are no more unsaved changes now...
    app.unsaved_changes_on_session = False
    app.unsaved_changes_on_asset = False

    # there is no component selected initially
    app.selected_asset = None

    # update the GUI to display the data
    app.root.ids.scenario_screens.current = "scenario_selection_screen"
    app.root.ids.asset_config_screens.current = "welcome_screen"
    app.root.ids.label_session_name.text = app.blueprint.info["name"]
    app.initialize_visualization()
    app.update_flowtype_list()
