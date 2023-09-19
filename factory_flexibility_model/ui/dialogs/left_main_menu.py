# IMPORTS
import copy
import os
from collections import defaultdict
from tkinter import filedialog
from tkinter.messagebox import askyesno

import numpy as np
import pandas as pd
import yaml
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Triangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy_garden.graph import LinePlot
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFlatButton, MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    IconLeftWidget,
    IconLeftWidgetWithoutTouch,
    IconRightWidget,
    ImageLeftWidgetWithoutTouch,
    OneLineIconListItem,
    OneLineListItem,
    TwoLineAvatarIconListItem,
    TwoLineAvatarListItem,
    TwoLineIconListItem,
    TwoLineListItem,
)
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDColorPicker
from kivymd.uix.snackbar import Snackbar

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.factory.Flowtype as ft
import factory_flexibility_model.factory.Unit as Unit
import factory_flexibility_model.io.session as session
import factory_flexibility_model.ui.color as color
import factory_flexibility_model.ui.flowtype_determination as fd
from factory_flexibility_model.ui.dialogs.parameter_config_dialog import *
from factory_flexibility_model.ui.dialogs.unit_definition_dialog import *
from factory_flexibility_model.ui.utility.custom_widget_classes import *


# LAYOUTS
Builder.load_file(r"factory_flexibility_model\ui\dialogs\left_main_menu.kv")

# CLASSES
class left_main_menu(BoxLayout):
    pass

# FUNCTIONS
def new_session(self, state):
    """
    This function contains everything related to the procedure of creating a new session.
    There are different paths that the function can take whoch are specified by "state".
    Some paths end up showing user selection screens that then call the function again with a different path.
    """

    # create partial functions for self recalls (necessary to suppres initial callbacks on .bind())
    def create(instance):
        self.new_session("create")

    def safe(instance):
        self.new_session("safe")

    def getname(instance):
        self.new_session("getname")

    # Case distinction...
    if state == "start":  # user clicked on "new session"
        # First: Ask for user confirmation if there are unsaved changes to the currently opened factory
        if self.unsaved_changes_on_session:
            # create dialog
            btn_cancel = MDFlatButton(text="Cancel")
            btn_dismiss = MDRaisedButton(
                text="Dismiss changes and continue", md_bg_color="red"
            )
            btn_save = MDRaisedButton(text="Save changes and continue")
            self.dialog = MDDialog(
                title="Unsaved changes on session",
                text="There are unsaved changes within the current session which will be deleted. ",
                buttons=[btn_cancel, btn_dismiss, btn_save],
            )
            # bind callbacks to buttons
            btn_cancel.bind(on_release=self.dialog.dismiss)  # abort the procedure
            btn_dismiss.bind(
                on_release=getname
            )  # recall the function with the advice to directly create a new factory this time
            btn_save.bind(
                on_release=safe
            )  # recall the function with the advice to first safe the session
            self.dialog.open()
        else:
            self.new_session("getname")

    if (
            state == "safe"
    ):  # user wants the current layout to be saved first before continuing with new session
        # close the warn dialog
        if hasattr(self, "dialog"):
            self.dialog.dismiss()

        # safe the session
        self.save_session()

        # recall the function with the advice to create new session
        self.new_session("getname")

    if state == "getname":  # create a new session
        # close the previous dialog
        if hasattr(self, "dialog"):
            if not self.dialog == None:
                self.dialog.dismiss()

        # create dialog
        btn_false = MDFlatButton(text="CANCEL")
        btn_true = MDRaisedButton(text="CREATE NEW SESSION")
        self.dialog = MDDialog(
            title="New Session",
            buttons=[btn_false, btn_true],
            type="custom",
            content_cls=dialog_new_session(),
        )
        # bind callbacks to buttons
        btn_true.bind(on_release=create)
        btn_false.bind(on_release=self.dialog.dismiss)
        self.dialog.open()

    if state == "create":  # create a new session
        # get requested name, description and directory
        session_name = self.dialog.content_cls.ids.textfield_new_session_name.text
        session_description = (
            self.dialog.content_cls.ids.textfield_new_session_description.text
        )
        try:
            path = self.dialog.content_cls.ids.filechooser_new_session.selection[0]
        except:
            path = rf"{os.getcwd()}\sessions"

        # close the previous dialog
        self.dialog.dismiss()

        # create the new session directory
        session.create_session_folder(path, session_name=session_name)
        self.session_data["session_path"] = rf"{path}\{session_name}"

        # create an empty blueprint and add the given information
        self.blueprint = bp.Blueprint()
        self.blueprint.info["name"] = session_name
        self.blueprint.info["description"] = session_description

        # initialize units and flowtypes
        self.initialize_units_and_flowtypes()

        # set the selected asset to none
        self.selected_asset = None

        # initialize the GUI
        self.initialize_visualization()
        self.update_flowtype_list()
        self.root.ids.asset_config_screens.current = "welcome_screen"
        self.root.ids.label_session_name.text = session_name

        # New session has not been saved yet
        self.unsaved_changes_on_session = True
        self.unsaved_changes_on_asset = False

        # reset scenarios
        self.scenarios = {}
        self.root.ids.grid_scenarios.clear_widgets()

        # inform the user
        Snackbar(
            text=f"New Session '{session_name}' created under '{self.session_data['session_path']}'"
        ).open()


def save_session(self):
    """
    This function saves the current session within the session_path
    """
    # make sure that there is a factory to save:
    if len(self.blueprint.components) < 2 or len(self.blueprint.connections) < 1:
        # create dialog
        btn_ok = MDFlatButton(text="OK")
        self.dialog = MDDialog(
            title="Insufficient Components",
            text="There is no factory to safe yet! Add at least one flow, two components and a connection before saving.",
            buttons=[btn_ok],
        )
        btn_ok.bind(on_release=self.dialog.dismiss)
        self.dialog.open()
        return

    # save session data
    with open(
            f"{self.session_data['session_path']}\\{self.blueprint.info['name']}.ffm",
            "w",
    ) as file:
        yaml.dump(self.session_data, file)

    # save current blueprint
    self.blueprint.save(path=self.session_data["session_path"])

    # save parameters
    with open(f"{self.session_data['session_path']}\\parameters.txt", "w") as file:
        for key_outer, inner_dict in self.parameters.items():
            for key_inner, values in inner_dict.items():
                for value in values.values():
                    line = f"{key_outer}/{key_inner}\t{value}\n"
                    file.write(line)

    # There are no more unsaved changes now...
    self.unsaved_changes_on_session = False

    Snackbar(
        text=f"Session successfully saved at {self.session_data['session_path']}"
    ).open()

    def load_session(self):
        """
        This function loads a session from a file
        """

        # ask for user confirmation if there are unsaved changes to the currently opened factory
        if self.unsaved_changes_on_session:
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
            self.session_data = yaml.load(file, Loader=yaml.SafeLoader)

        self.session_data["session_path"] = os.path.dirname(filepath)

        # IMPORT blueprint including flowtypes and units
        try:
            blueprint_new = bp.Blueprint()
            blueprint_new.import_from_file(self.session_data["session_path"])
        except:
            Snackbar(
                text=f"ERROR: Importing Blueprint from {self.session_data['session_path']} failed!"
            ).open()
            return

        # IMPORT parameters
        try:
            # open the given file
            with open(f"{self.session_data['session_path']}\\parameters.txt") as file:
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
                    parameters_new[key[0]][key[1]][value_key] = float(value.replace(",", "."))
                    # increment value_key to prevent double usage of keys
                    value_key += 1
        except:
            Snackbar(
                text=f"The given parameters.txt-config file is invalid, has a wrong format or is corrupted! ({self.session_data['session_path']}\\parameters.txt)"
            ).open()
            return

        # IMPORT timeseries
        try:
            # open the given file
            with open(f"{self.session_data['session_path']}\\timeseries.txt") as file:
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
                text=f"The given timeseries.txt-config file is invalid, has a wrong format or is corrupted! ({self.session_data['session_path']}\\timeseries.txt)"
            ).open()
            return

        # Did all imports work till here? -> Overwrite internal attributes
        self.blueprint = blueprint_new
        self.parameters = parameters_new
        self.timeseries = timeseries_new

        # There are no more unsaved changes now...
        self.unsaved_changes_on_session = False
        self.unsaved_changes_on_asset = False

        # there is no component selected initially
        self.selected_asset = None

        # update the GUI to display the data
        self.root.ids.scenario_screens.current = "scenario_selection_screen"
        self.root.ids.asset_config_screens.current = "welcome_screen"
        self.root.ids.label_session_name.text = self.blueprint.info["name"]
        self.initialize_visualization()
        self.update_flowtype_list()