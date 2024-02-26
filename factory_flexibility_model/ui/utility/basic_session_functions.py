# This file contains the basic functions required to create, save and load sessions within the factory model gui.

# IMPORTS
import os
from tkinter import filedialog
from tkinter.messagebox import askyesno

import yaml
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar.snackbar import MDSnackbar

import factory_flexibility_model.factory.Blueprint as bp
from factory_flexibility_model.factory.Flowtype import Flowtype
from factory_flexibility_model.factory.Unit import Unit
from factory_flexibility_model.ui.gui_components.info_popup.info_popup import (
    show_info_popup,
)
from factory_flexibility_model.ui.gui_components.layout_canvas.factory_visualisation import (
    initialize_visualization,
)
from factory_flexibility_model.ui.gui_components.layout_flowtype_configuration.layout_flowtype_list import (
    update_flowtype_list,
)
from factory_flexibility_model.ui.gui_components.main_menu.dialog_new_session import (
    show_new_session_dialog,
)
from factory_flexibility_model.ui.utility.io.import_scenarios import import_scenarios
from factory_flexibility_model.ui.utility.window_handling import close_dialog

# FUNCTIONS


def initiate_new_session(app):
    """
    This function is called when the user clicks on the "new session" button within the main menu.
    It checks, if there are unsaved changes within the session.
    If not, the show_new_session_dialog function is called to ask the user to specify the new session.
    Otherwise a dialog is created that asks the user whether he wants to cancel, save or dismiss the
    changes on the current session.

    :param app: Pointer to the current factory_GUIApp-instance
    :return: None
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


def collect_timeseries_data(app):
    """
    This function is responsible for providing the actual timeseries data for component parameters within the scenario.sc files that are stored within the session folder.
    During GUI runtime only the keys of timeseries as adressable within session_data[timeseries] are handled. When saving the session for simulation the timeseries arrays have to be provided with the required number of timesteps.
    This function goes through all scenarios and searches for component-parameters that have to be defined as timeseries. For those parameters the timeseries are looked up and shortened to the length od app.blueprint.info[timeseries]
    :param app: Object of the GUI instance
    :return: None; app.session_data["scenarios"] is modified
    """

    # iterate over all scenarios
    for scenario in app.session_data["scenarios"].values():
        # iterate over all components that have parameters specified
        for component in scenario.values():
            # iterate over all parameters of the component
            for parameter in component.values():
                # check, if the parameter is a timeseries
                if parameter["type"] == "timeseries":
                    # get the actual timeseries with the required length and write it into the "value" field of the parameter
                    parameter["value"] = app.session_data["timeseries"][
                        parameter["key"]
                    ]["values"][0 : app.blueprint.info["timesteps"]]


def create_session_folder(root_folder, session_name: str = "New Session"):
    """
    This function initializes a session folder with all required files and subfolders

    :param root_folder: [str] User given path where the new session folder shall be created
    :session_name: [str] Name for the new session == Name of the subfolder to be created
    :return: None
    """

    # Create path to the new session folder
    subfolder_path = os.path.join(root_folder, session_name)
    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)

    # create a subfolder for simulations
    simulations_path = os.path.join(subfolder_path, "simulations")
    if not os.path.exists(simulations_path):
        os.makedirs(simulations_path)

    # create a subfolder for scenarios
    scenarios_path = os.path.join(subfolder_path, "scenarios")
    if not os.path.exists(scenarios_path):
        os.makedirs(scenarios_path)

    # create a subfolder for the layout
    layout_path = os.path.join(subfolder_path, "layout")
    if not os.path.exists(layout_path):
        os.makedirs(layout_path)

    # create empty Factory.factory - file
    with open(os.path.join(layout_path, "Layout.factory"), "w") as f:
        pass


def create_new_session(app):
    """
    This function creates a new session. It reads out all the user inputs from the currently opened dialog_new_session.
    If the values are valid the dialog is closed and a blank session is being created at the user given filepath.
    Then a new blueprint is created, saved under app.blueprint and the basic units and flowtypes are being initialized.
    Finally all app parameters and the gui are resettet into a neutral state.

    :param app: Pointer to the current factory_GUIApp-instance
    :return: None
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
    initialize_units_and_flowtypes(app)

    # take standard session config from config file
    app.session_data["show_component_config_dialog_on_creation"] = app.config[
        "show_component_config_dialog_on_creation"
    ]
    app.session_data["session_active"] = True

    # set the selected asset to none
    app.selected_asset = None

    # reset the session timeseries list
    app.session_data["timeseries"] = {}

    # initialize a scenario list with just an empty default scenario and select it.
    app.session_data["scenarios"] = {"default": {}}
    app.selected_scenario = "default"

    # initialize the GUI
    initialize_visualization(app)
    update_flowtype_list(app)
    app.root.ids.asset_config_screens.current = "flowtype_list"
    app.root.ids.label_session_name.text = session_name

    # New session has not been saved yet
    app.unsaved_changes_on_session = True
    app.unsaved_changes_on_asset = False

    # inform the user
    MDSnackbar(
        MDLabel(
            text=f"New Session '{session_name}' created under '{app.session_data['session_path']}'"
        )
    ).open()


def save_session(app):
    """
    This function saves the current session within the session_path by first calling the save routine of
    the blueprint class to store the layout, units and flowtypes.
    Then the parameter-dict of the session is parsed into a .txt file and stored in the same folder.

    :param app: Pointer to the current factory_GUIApp-instance
    :return: None
    """

    # make sure that there is no open dialog
    close_dialog(app)

    # make sure that there is a session to save
    if app.session_data["session_path"] is None:
        show_info_popup(
            app, "Cannot save before a session has been created or imported!"
        )
        return

    # SAVE RELEVANT PARTS OF SESSION DATA
    data = {
        "display_scaling_factor": app.session_data["display_scaling_factor"],
        "session_path": app.session_data["session_path"],
        "show_component_config_dialog_on_creation": app.session_data[
            "show_component_config_dialog_on_creation"
        ],
        "timeseries": app.session_data["timeseries"],
    }

    with open(
        f"{app.session_data['session_path']}\\{app.blueprint.info['name']}.ffm",
        "w",
    ) as file:
        yaml.dump(data, file)

    # SAVE THE BLUEPRINT
    app.blueprint.save(path=f"{app.session_data['session_path']}\\layout")

    # Get the required timeseries-data for all parameters specified as timeseries with the correct length
    collect_timeseries_data(app)

    # Iterate over all scenarios and create scenario.txt documents
    for key_scenario, scenario in app.session_data["scenarios"].items():

        with open(
            f"{app.session_data['session_path']}/scenarios/{key_scenario}.sc", "w"
        ) as file:
            yaml.dump(scenario, file)

    # There are no more unsaved changes now...
    app.unsaved_changes_on_session = False

    # save png of layout
    app.root.ids.canvas_layout.export_to_png(
        f"{app.session_data['session_path']}\\layout\\layout.png"
    )

    MDSnackbar(
        MDLabel(
            text=f"Session successfully saved at {app.session_data['session_path']}"
        )
    ).open()


def save_session_as(app):
    """
    This function is used to create a copy of a session.
    The function is bein called out of the save_session_as-dialog after the user has specified a new name and path
    for the session. Those values are read out of the dialog, the dialog is closed, the info gets written into the
    sessions blueprint. Then the regular save_session() method is being called

    :param app: Pointer to the current factory_GUIApp-instance
    :return: None
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
    close_dialog(app)

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
    :return: None
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

    # set session path
    app.session_data["session_path"] = os.path.dirname(filepath)

    # there is an active session now
    app.session_data["session_active"] = True

    # IMPORT blueprint including flowtypes and units
    try:
        blueprint_new = bp.Blueprint()
        blueprint_new.import_from_file(
            f'{app.session_data["session_path"]}\\layout\\Layout.factory'
        )
    except:
        MDSnackbar(
            MDLabel(
                text=f"ERROR: Importing Blueprint from '{app.session_data['session_path']}\\layout\\Layout.factory' failed!"
            )
        ).open()
        return

    # IMPORT Scenarios
    app.session_data["scenarios"] = import_scenarios(
        f"{app.session_data['session_path']}/scenarios"
    )

    # Did all imports work till here? -> Overwrite internal attributes
    app.blueprint = blueprint_new

    # There are no more unsaved changes now...
    app.unsaved_changes_on_session = False
    app.unsaved_changes_on_asset = False

    # there is no component selected initially
    app.selected_asset = None

    # select the default scenario of the session
    app.selected_scenario = "default"

    # update the GUI to display the data
    app.root.ids.asset_config_screens.current = "flowtype_list"
    app.root.ids.label_session_name.text = app.blueprint.info["name"]
    initialize_visualization(app)
    update_flowtype_list(app)


def initialize_units_and_flowtypes(app):
    """
    This function creates the basic set of units and flowtypes required
    """
    # initialize the basic units
    app.blueprint.units["energy"] = Unit(
        key="energy",
        quantity_type="energy",
        conversion_factor=1,
        magnitudes=[1, 1000, 1000000, 1000000000, 1000000000000],
        units_flow=["kWh", "MWh", "GWh", "TWh", "PWh"],
        units_flowrate=["kW", "MW", "GW", "TW", "PW"],
        name="Energy [kW]",
    )
    app.blueprint.units["joule"] = Unit(
        key="joule",
        quantity_type="energy",
        conversion_factor=1 / 3600,
        magnitudes=[1, 1000, 1000000, 1000000000],
        units_flow=["kJ", "MJ", "GJ", "PJ"],
        units_flowrate=["kJ/h", "MJ/h", "GJ/h", "PJ/h"],
        name="Energy [Joule]",
    )
    app.blueprint.units["mmBTU"] = Unit(
        key="mmBTU",
        quantity_type="energy",
        conversion_factor=293.071070,
        magnitudes=[1],
        units_flow=["mmBTU"],
        units_flowrate=["mmBTU/h"],
        name="Energy [mmBTU]",
    )
    app.blueprint.units["mass"] = Unit(
        key="mass",
        quantity_type="mass",
        conversion_factor=1,
        magnitudes=[1, 1000, 1000000, 1000000000, 1000000000000],
        units_flow=["kg", "t", "kt", "mt", "gt"],
        units_flowrate=["kg/h", "t/h", "kt/h", "mt/h", "gt/h"],
        name="Mass [kg]",
    )
    app.blueprint.units["unit"] = Unit(
        key="unit",
        quantity_type="other",
        conversion_factor=1,
        magnitudes=[1],
        units_flow=["units"],
        units_flowrate=["units/h"],
        name="Unspecified Unit",
    )

    # initialize basic flowtypes
    app.blueprint.flowtypes["material_losses"] = Flowtype(
        "material_losses",
        unit=app.blueprint.units["mass"],
        color="#555555",
        represents_losses=True,
        name="Material Losses",
        description="Built in default flowtype used to represent all kinds of material losses",
    )
    app.blueprint.flowtypes["energy_losses"] = Flowtype(
        "energy_losses",
        unit=app.blueprint.units["energy"],
        color="#555555",
        represents_losses=True,
        name="Energy Losses",
        description="Built in default flowtype used to represent all kinds of energy losses",
    )

    app.blueprint.flowtypes["heat"] = Flowtype(
        "heat",
        unit=app.blueprint.units["energy"],
        color="#996666",
        name="Heat",
        description="Built in default flowtype used to represent all kinds of heat",
    )

    app.blueprint.flowtypes["unknown"] = Flowtype(
        "unknown",
        unit=app.blueprint.units["unit"],
        color="#999999",
        name="Unknown Flow",
        description="Built in default flowtype used as a fallback option for unspecified situations",
    )
