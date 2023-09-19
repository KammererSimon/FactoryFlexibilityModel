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


# IMPORT 3RD PARTY PACKAGES

main_color = "#1D4276"
colors = {
    "Red": {
        "50": "FFEBEE",
        "100": "FFCDD2",
        "200": "EF9A9A",
        "300": "E57373",
        "400": "EF5350",
        "500": "F44336",
        "600": "E53935",
        "700": "D32F2F",
        "800": "C62828",
        "900": "B71C1C",
        "A100": "FF8A80",
        "A200": "FF5252",
        "A400": "FF1744",
        "A700": "D50000",
    },
    "Pink": {
        "50": "FCE4EC",
        "100": "F8BBD0",
        "200": "F48FB1",
        "300": "F06292",
        "400": "EC407A",
        "500": "E91E63",
        "600": "D81B60",
        "700": "C2185B",
        "800": "AD1457",
        "900": "880E4F",
        "A100": "FF80AB",
        "A200": "FF4081",
        "A400": "F50057",
        "A700": "C51162",
    },
    "Purple": {
        "50": "F3E5F5",
        "100": "E1BEE7",
        "200": "CE93D8",
        "300": "BA68C8",
        "400": "AB47BC",
        "500": "9C27B0",
        "600": "8E24AA",
        "700": "7B1FA2",
        "800": "6A1B9A",
        "900": "4A148C",
        "A100": "EA80FC",
        "A200": "E040FB",
        "A400": "D500F9",
        "A700": "AA00FF",
    },
    "DeepPurple": {
        "50": "EDE7F6",
        "100": "D1C4E9",
        "200": "B39DDB",
        "300": "9575CD",
        "400": "7E57C2",
        "500": "673AB7",
        "600": "5E35B1",
        "700": "512DA8",
        "800": "4527A0",
        "900": "311B92",
        "A100": "B388FF",
        "A200": "7C4DFF",
        "A400": "651FFF",
        "A700": "6200EA",
    },
    "Indigo": {
        "50": "E8EAF6",
        "100": "C5CAE9",
        "200": "9FA8DA",
        "300": "7986CB",
        "400": "5C6BC0",
        "500": "3F51B5",
        "600": "3949AB",
        "700": "303F9F",
        "800": "283593",
        "900": "1A237E",
        "A100": "8C9EFF",
        "A200": "536DFE",
        "A400": "3D5AFE",
        "A700": "304FFE",
    },
    "Blue": {
        "50": "1D4276",
        "100": "1D4276",
        "200": "1D4276",
        "300": "1D4276",
        "400": "1D4276",
        "500": "1D4276",
        "600": "1D4276",
        "700": "1D4276",
        "800": "11D4276",
        "900": "1D4276",
        "A100": "1D4276",
        "A200": "1D4276",
        "A400": "1D4276",
        "A700": "1D4276",
    },
    "LightBlue": {
        "50": "E1F5FE",
        "100": "B3E5FC",
        "200": "81D4FA",
        "300": "4FC3F7",
        "400": "29B6F6",
        "500": "03A9F4",
        "600": "039BE5",
        "700": "0288D1",
        "800": "0277BD",
        "900": "01579B",
        "A100": "80D8FF",
        "A200": "40C4FF",
        "A400": "00B0FF",
        "A700": "0091EA",
    },
    "Cyan": {
        "50": "E0F7FA",
        "100": "B2EBF2",
        "200": "80DEEA",
        "300": "4DD0E1",
        "400": "26C6DA",
        "500": "00BCD4",
        "600": "00ACC1",
        "700": "0097A7",
        "800": "00838F",
        "900": "006064",
        "A100": "84FFFF",
        "A200": "18FFFF",
        "A400": "00E5FF",
        "A700": "00B8D4",
    },
    "Teal": {
        "50": "E0F2F1",
        "100": "B2DFDB",
        "200": "80CBC4",
        "300": "4DB6AC",
        "400": "26A69A",
        "500": "009688",
        "600": "00897B",
        "700": "00796B",
        "800": "00695C",
        "900": "004D40",
        "A100": "A7FFEB",
        "A200": "64FFDA",
        "A400": "1DE9B6",
        "A700": "00BFA5",
    },
    "Green": {
        "50": "E8F5E9",
        "100": "C8E6C9",
        "200": "A5D6A7",
        "300": "81C784",
        "400": "66BB6A",
        "500": "4CAF50",
        "600": "43A047",
        "700": "388E3C",
        "800": "2E7D32",
        "900": "1B5E20",
        "A100": "B9F6CA",
        "A200": "69F0AE",
        "A400": "00E676",
        "A700": "00C853",
    },
    "LightGreen": {
        "50": "F1F8E9",
        "100": "DCEDC8",
        "200": "C5E1A5",
        "300": "AED581",
        "400": "9CCC65",
        "500": "8BC34A",
        "600": "7CB342",
        "700": "689F38",
        "800": "558B2F",
        "900": "33691E",
        "A100": "CCFF90",
        "A200": "B2FF59",
        "A400": "76FF03",
        "A700": "64DD17",
    },
    "Lime": {
        "50": "F9FBE7",
        "100": "F0F4C3",
        "200": "E6EE9C",
        "300": "DCE775",
        "400": "D4E157",
        "500": "CDDC39",
        "600": "C0CA33",
        "700": "AFB42B",
        "800": "9E9D24",
        "900": "827717",
        "A100": "F4FF81",
        "A200": "EEFF41",
        "A400": "C6FF00",
        "A700": "AEEA00",
    },
    "Yellow": {
        "50": "FFFDE7",
        "100": "FFF9C4",
        "200": "FFF59D",
        "300": "FFF176",
        "400": "FFEE58",
        "500": "FFEB3B",
        "600": "FDD835",
        "700": "FBC02D",
        "800": "F9A825",
        "900": "F57F17",
        "A100": "FFFF8D",
        "A200": "FFFF00",
        "A400": "FFEA00",
        "A700": "FFD600",
    },
    "Amber": {
        "50": "FFF8E1",
        "100": "FFECB3",
        "200": "FFE082",
        "300": "FFD54F",
        "400": "FFCA28",
        "500": "FFC107",
        "600": "FFB300",
        "700": "FFA000",
        "800": "FF8F00",
        "900": "FF6F00",
        "A100": "FFE57F",
        "A200": "FFD740",
        "A400": "FFC400",
        "A700": "FFAB00",
    },
    "Orange": {
        "50": "FFF3E0",
        "100": "FFE0B2",
        "200": "FFCC80",
        "300": "FFB74D",
        "400": "FFA726",
        "500": "FF9800",
        "600": "FB8C00",
        "700": "F57C00",
        "800": "EF6C00",
        "900": "E65100",
        "A100": "FFD180",
        "A200": "FFAB40",
        "A400": "FF9100",
        "A700": "FF6D00",
    },
    "DeepOrange": {
        "50": "FBE9E7",
        "100": "FFCCBC",
        "200": "FFAB91",
        "300": "FF8A65",
        "400": "FF7043",
        "500": "FF5722",
        "600": "F4511E",
        "700": "E64A19",
        "800": "D84315",
        "900": "BF360C",
        "A100": "FF9E80",
        "A200": "FF6E40",
        "A400": "FF3D00",
        "A700": "DD2C00",
    },
    "Brown": {
        "50": "EFEBE9",
        "100": "D7CCC8",
        "200": "BCAAA4",
        "300": "A1887F",
        "400": "8D6E63",
        "500": "795548",
        "600": "6D4C41",
        "700": "5D4037",
        "800": "4E342E",
        "900": "3E2723",
        "A100": "000000",
        "A200": "000000",
        "A400": "000000",
        "A700": "000000",
    },
    "Gray": {
        "50": "FAFAFA",
        "100": "F5F5F5",
        "200": "EEEEEE",
        "300": "E0E0E0",
        "400": "BDBDBD",
        "500": "9E9E9E",
        "600": "757575",
        "700": "616161",
        "800": "424242",
        "900": "212121",
        "A100": "000000",
        "A200": "000000",
        "A400": "000000",
        "A700": "000000",
    },
    "BlueGray": {
        "50": "ECEFF1",
        "100": "CFD8DC",
        "200": "B0BEC5",
        "300": "90A4AE",
        "400": "78909C",
        "500": "607D8B",
        "600": "546E7A",
        "700": "455A64",
        "800": "37474F",
        "900": "263238",
        "A100": "000000",
        "A200": "000000",
        "A400": "000000",
        "A700": "000000",
    },
    "Light": {
        "StatusBar": "E0E0E0",
        "AppBar": "F5F5F5",
        "Background": "FAFAFA",
        "CardsDialogs": "FFFFFF",
        "FlatButtonDown": "cccccc",
    },
    "Dark": {
        "StatusBar": "000000",
        "AppBar": "1f1f1f",
        "Background": "121212",
        "CardsDialogs": "212121",
        "FlatButtonDown": "999999",
    },
}


class factory_GUIApp(MDApp):
    # TODO: checken ob das hier notwendig ist
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def abort_new_connection(self, touch):
        self.connection_edit_mode = False
        Window.unbind(mouse_pos=self.update_visualization)
        self.initialize_visualization()

    def add_component(self, instance, touch):

        # check, if the function call actually came from an object that has been clicked/moved
        if not instance.collide_point(*touch.pos):
            # abort if not
            return

        # only continue if the dummy has been moved out of the right column
        if instance.pos[0] < self.root.ids.component_shelf.width:
            self.show_component_creation_menu()
            return

        # abort if there is no session yet
        if self.session_data["session_path"] is None:
            self.show_info_popup(
                "Cannot create components before initializing or importing a session!"
            )
            # close the component selection menu
            self.root.ids.component_shelf.set_state("closed")
            return

        # determine component_type
        component_type = instance.key

        # assign a key to the new component
        i = 1
        while f"component_{i}" in self.blueprint.components.keys():
            i += 1
        component_key = f"component_{i}"

        # assign a name to the new component
        i = 1
        while self.get_key(f"Unspecified {component_type} {i}"):
            i += 1
        component_name = f"Unspecified {component_type} {i}"

        # create a blueprint entry for the component with dummy values
        self.blueprint.components[component_key] = {
            "key": component_key,
            "name": component_name,
            "GUI": {
                "position_x": 0,
                "position_y": 0,
                "icon": self.default_icons[component_type],
            },
            "description": "",
            "type": component_type,
            "flowtype": self.blueprint.flowtypes["unknown"],
        }

        # create a temporary widget on the main canvas to store the position until self.save_component_positions()
        component_framelabel = DragLabel(id=component_key)
        component_framelabel.pos = instance.pos

        self.root.ids.canvas_layout.add_widget(component_framelabel)
        self.root.ids[f"frame_{component_key}"] = component_framelabel

        # add parameter-dict for the new component
        self.parameters[component_key] = {}

        # close the component selection menu
        self.root.ids.component_shelf.set_state("closed")

        # catch the position of the new component and update the visualisation to show it in the correct place
        self.save_component_positions()
        self.initialize_visualization()

        # select the new asset
        self.change_selected_asset(component_key)

        # set unsaved changes to true
        self.unsaved_changes_on_session = True

    def add_connection(self, destination_key):
        """
        This function is being called when the user confirms the creation of a new connection within the new_connection_dialog.
        """

        # disable connection edit mode
        self.connection_edit_mode = False
        Window.unbind(mouse_pos=self.update_visualization)

        # get the origin
        origin_name = self.selected_asset["name"]
        origin_key = self.get_key(origin_name)
        origin_flowtype = self.blueprint.components[origin_key]["flowtype"]
        destination_name = self.blueprint.components[destination_key]["name"]
        destination_flowtype = self.blueprint.components[destination_key]["flowtype"]

        # make sure that the connection is not already existing:
        for connection in self.blueprint.connections.values():
            # check all connections in the blueprint
            if connection["from"] == origin_key and connection["to"] == destination_key:
                # if current connection is equal to the one to be created: abort and warn the user
                self.show_info_popup(
                    f"There is already a connection from {origin_name} to {destination_name}!"
                )
                return

        # check flowtype compatibility of origin and destination
        connection_flowtype = self.blueprint.flowtypes["unknown"]
        if origin_flowtype.is_unknown():
            # if the origin flowtype is unknown: check the destination flowtype
            if not destination_flowtype.is_unknown():
                #  if the destination has a flowtype set: adapt it!
                connection_flowtype = destination_flowtype
                fd.set_component_flowtype(
                    self.blueprint, origin_key, destination_flowtype
                )
        else:
            connection_flowtype = origin_flowtype
            # if the origin flowtype is known: check compatibility with destination flowtype
            if destination_flowtype.is_unknown():
                # if destination flowtype is unknown -> define it as origin flowtype
                fd.set_component_flowtype(
                    self.blueprint, destination_key, origin_flowtype
                )
            elif not destination_flowtype.key == origin_flowtype.key:
                # if destination flowtype diverges from origin flowtype -> abort and show an error
                self.show_info_popup(
                    f"Cannot create this connection, because {origin_name} and {destination_name} already have different flowtypes assigned!"
                )
                return

        # create adressing key for new connection
        i = 0
        while f"connection_{i}" in self.blueprint.connections.keys():
            i += 1
        connection_key = f"connection_{i}"

        # create a new connection:
        self.blueprint.connections[connection_key] = {}
        self.blueprint.connections[connection_key][
            "name"
        ] = f"{origin_name} -> {destination_name}"
        self.blueprint.connections[connection_key]["from"] = origin_key
        self.blueprint.connections[connection_key]["to"] = destination_key
        self.blueprint.connections[connection_key]["flowtype"] = connection_flowtype
        self.blueprint.connections[connection_key]["key"] = connection_key
        self.blueprint.connections[connection_key]["weight_source"] = 1
        self.blueprint.connections[connection_key]["weight_sink"] = 1
        self.blueprint.connections[connection_key]["to_losses"] = False
        self.blueprint.connections[connection_key]["type"] = "connection"

        # update the configuration card, visualisation and asset list
        self.initialize_visualization()

        # set unsaved changes to true
        self.unsaved_changes_on_session = True

    def add_flowtype(self, *args):
        """
        This function ads a generic new flowtype to the factory and selects it for configuration
        """

        # create key for the new flow
        i = 0
        while f"flowtype_{i}" in self.blueprint.flowtypes.keys():
            i += 1
        flowtype_key = f"flowtype_{i}"

        # create initial name for the flowtype
        i = 1
        while self.get_key(f"Unspecified Flowtype {i}"):
            i += 1
        flowtype_name = f"Unspecified Flowtype {i}"

        # create a new flowtype:
        self.blueprint.flowtypes[flowtype_key] = ft.Flowtype(
            key=flowtype_key,
            name=flowtype_name,
            unit=self.blueprint.units["energy"],
            color="#999999",
        )

        # update list of flowtypes on screen
        self.update_flowtype_list()

        # set unsaved changes to true
        self.unsaved_changes_on_session = True

    def app_add_static_parameter_value(self):
        add_static_parameter_value(self)

    def app_show_converter_ratio_dialog(self):
        show_converter_ratio_dialog(self)

    def app_save_converter_ratios(self):
        save_converter_ratios(self)

    def app_add_magnitude_to_unit(self):
        add_magnitude_to_unit(self)

    def app_add_unit(self):
        add_unit(self)

    def app_save_changes_on_unit(self):
        save_changes_on_unit(self)

    def app_show_unit_config_dialog(self):
        show_unit_config_dialog(self)

    def app_select_unit_list_item(self, list_item, touch):
        select_unit_list_item(self, list_item, touch)

    def app_select_unit(self, unit):
        select_unit(self, unit)

    def app_add_unit(self, *args):
        add_unit(self, *args)

    def app_update_unit_list(self):
        update_unit_list(self)

    def app_show_magnitude_creation_popup(self):
        show_magnitude_creation_popup(self)

    def app_delete_unit(self):
        delete_unit(self)

    def build(self):
        """
        This function is the main function that is called when creating a new instance of the GUI. It creates the Screen
        and initializes all functional variables for the GUI
        """
        # create root object for the app
        screen = Builder.load_file(r"factory_flexibility_model\ui\FactoryModelGUI.kv")

        # Background variables for GUI
        self.blueprint = bp.Blueprint()  # Stores the current factory layout
        self.connection_edit_mode = (
            False  # is set to true while the user is building a new connection
        )
        self.popup = None
        self.unsaved_changes_on_session = False  # indicated if there have been changes to the session since opening or saving
        self.unsaved_changes_on_asset = False  # indicates if there have been changes to the current asset since selecting or saving
        self.scenarios = {}  # List of existing scenarios in the current session
        self.selected_asset = None  # the asset that the user has currently selected
        self.selected_parameter = (
            ""  # the scenarioparameter that the user has currently selected
        )
        self.selected_scenario = {
            "timesteps": 168,
            "name": "Testscenario",
            "time_factor": 1,
        }
        self.selected_timeseries = np.zeros(168)  # the currently activated timeseries
        self.session_data = {
            "display_scaling_factor": 0.6,
            "session_path": None,
        }
        self.timeseries = []  # List of imported timeseries within the session

        # Style Config for GUI
        self.main_color = "#1D4276"
        self.main_color_rgba = [0.1137, 0.2588, 0.463, 1]
        self.dialog = None  # keeps track of currently opened dialogs
        self.display_grid_size = [
            45,
            30,
        ]  # number of grid points underlying the visualisation
        self.theme_cls.colors = colors
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        self.parameters = {}

        # paths to used .png-assets
        def get_files_in_directory(directory_path):
            files_dict = {}
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    filename, extension = os.path.splitext(file)
                    files_dict[filename] = os.path.join(root, file)
            return files_dict

        self.component_icons = get_files_in_directory("Assets\\components")
        self.source_icons = get_files_in_directory("Assets\\sources")
        self.sink_icons = get_files_in_directory("Assets\\sinks")
        self.highlight_icons = get_files_in_directory("Assets\\highlights")
        self.default_icons = get_files_in_directory("Assets\\defaults")

        # set window configuration
        Window.maximize()
        Window.bind(on_resize=self.initialize_visualization)  # start in fullscreen
        Window.bind(
            on_maximize=self.initialize_visualization
        )  # update the visualization when changing the window size
        Window.bind(
            on_restore=self.initialize_visualization
        )  # update the visualization when changing the window size
        return screen

    def change_selected_asset(self, key):
        """
        This function takes a component key and sets the asset adressed by the key as the currently selected asset.
        """

        if not self.dialog == None:
            self.dialog.dismiss()

        if key is None:
            self.selected_asset = None

        # get the asset adressed by the key and store it in self.selected_asset
        if key in self.blueprint.components:
            if not self.blueprint.components[key] == None:
                self.selected_asset = self.blueprint.components[key]
        if key in self.blueprint.flowtypes:
            self.selected_asset = self.blueprint.flowtypes[key]

        # there can't be any changes on the current asset now
        self.unsaved_changes_on_asset = False

        # update the config_tab to show the selected asset
        self.update_config_tab()

        # update visualisation to highlight selected asset
        self.update_visualization()

    def click_on_component(self, instance, touch):
        """
        This function is triggered everytime when the user clicks on the component (or on the canvas if it is still buggy)
        This function will select the clicked component as the current asset.
        If the user moves the component the new position will be stored using self.save_component_positions
        """

        # check, if the function call actually came from an object that has been clicked/moved
        if not instance.collide_point(*touch.pos):
            # abort if not
            return

        # check if the user wants to create a new connection
        if not self.selected_asset == None:
            if (
                self.connection_edit_mode
                and not instance.id == self.selected_asset["key"]
            ):
                self.add_connection(instance.id)
                self.connection_edit_mode = False
                return

        # otherwise just select the component that has been clicked on
        self.initiate_asset_selection(instance.id)
        self.save_component_positions()

    def close_dialog(self):
        """
        This function closes any dialog that is still opened
        """
        if not self.dialog == None:
            self.dialog.dismiss()

    def close_popup(self):
        """
        This function closes any popup that is still opened
        """
        if not self.popup == None:
            self.popup.dismiss()

    def copy_scenario(self, instance):
        """
        This function duplicates a scenario
        """
        # get key of the scenario to be douplicated
        parent_scenario_key = instance.parent.parent.scenario_key

        # determine a key for the new scenario
        i = 1
        while f"{parent_scenario_key}_{i}" in self.scenarios.keys():
            i += 1
        new_scenario_key = f"{parent_scenario_key}_{i}"

        # create copy of the original scenario and store it under the new key
        # -> pointer to card widget of parent cant be deepcopied and has to be stored
        card_widget_parent = self.scenarios[parent_scenario_key]["card_widget"]
        self.scenarios[parent_scenario_key]["card_widget"] = None
        self.scenarios[new_scenario_key] = copy.deepcopy(
            self.scenarios[parent_scenario_key]
        )
        self.scenarios[parent_scenario_key]["card_widget"] = card_widget_parent

        # change the key within the copy of the scenario
        self.scenarios[new_scenario_key]["key"] = new_scenario_key
        self.scenarios[new_scenario_key][
            "name"
        ] = f"Copy of {self.scenarios[parent_scenario_key]['name']}"

        # create a card widget to show the new scenario in UI
        card_widget = ScenarioCard(scenario_key=new_scenario_key)
        card_widget.id = new_scenario_key
        card_widget.ids.image.source = self.scenarios[parent_scenario_key]["image"]
        card_widget.ids.title.text = (
            f"Copy of {self.scenarios[parent_scenario_key]['name']}"
        )
        card_widget.ids.description.text = self.scenarios[parent_scenario_key][
            "description"
        ]
        card_widget.bind(
            on_press=lambda instance: self.update_scenario_config_screen(instance)
        )
        card_widget.ids.icon_copy.bind(
            on_release=lambda instance: self.copy_scenario(instance)
        )
        card_widget.ids.icon_delete.bind(
            on_release=lambda instance: self.show_scenario_deletion_dialog(instance)
        )
        self.root.ids.grid_scenarios.add_widget(card_widget)
        self.scenarios[new_scenario_key][
            "card_widget"
        ] = card_widget  # store the pointer to the card widget in the scenario_dict

        # session contains unsaved chaanges now
        self.unsaved_changes_on_session = True

    def create_main_menu(self, master):
        # TODO: auslagern in .kv file
        self.button_new_session = Button(
            text="New Session", background_color=self.main_color
        )
        self.button_new_session.bind(on_press=self.new_session)
        master.add_widget(self.button_new_session)

        self.button_open_session = Button(
            text="Open Session", background_color=self.main_color
        )
        self.button_open_session.bind(on_press=self.load_session)
        master.add_widget(self.button_open_session)

        self.button_save_session = Button(
            text="Save Session", background_color=self.main_color
        )
        self.button_save_session.bind(on_press=self.save_session)
        master.add_widget(self.button_save_session)

        self.button_create_demo_session = Button(
            text="Create Demo Session", background_color=self.main_color
        )
        self.button_create_demo_session.bind(on_press=self.create_demo_session)
        master.add_widget(self.button_create_demo_session)

    def decrease_scaling_factor(self):
        self.session_data["display_scaling_factor"] = (
            self.session_data["display_scaling_factor"] * 0.95
        )
        self.initialize_visualization()

    def delete_component(self, *args):

        self.close_dialog()

        # check, which connections need to be removed along with the component
        delete_list = []
        for connection in self.blueprint.connections:
            if (
                self.blueprint.connections[connection]["from"]
                == self.selected_asset["key"]
            ) or (
                self.blueprint.connections[connection]["to"]
                == self.selected_asset["key"]
            ):
                delete_list.append(connection)

        for connection in delete_list:
            Snackbar(
                text=f"Connection {self.blueprint.connections[connection]['name']} has been deleted!"
            ).open()
            del self.blueprint.connections[connection]

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} has been deleted!").open()

        # delete the component out of the blueprint
        del self.blueprint.components[self.selected_asset["key"]]

        # now there is no more selected component
        self.selected_asset = None
        self.root.ids.asset_config_screens.current = "welcome_screen"

        # redraw the visualisation without the selected component
        self.initialize_visualization()

    def delete_connection(self, key):
        """
        This function deletes the currently selected connection
        """

        # close the opened dialog
        self.close_dialog()

        # remove connection from blueprint
        del self.blueprint.connections[key]

        # delete currently selected asset
        self.selected_asset = None

        # show neutral screen on the right
        self.root.ids.asset_config_screens.current = "welcome_screen"

        # there are no more unsaved changes on the selected asset, but therefore on the session
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the preview without the connection
        self.initialize_visualization()

    def delete_scenario(self, scenario_key):
        """
        This function deletes the scenario given as scenario_key
        """

        # close the dialog
        self.dialog.dismiss()

        self.root.ids.grid_scenarios.remove_widget(
            self.scenarios[scenario_key]["card_widget"]
        )

        # delete the scenario from the root scenariolist:
        self.scenarios[scenario_key] = []

        # session contains unsaved changes now:
        self.unsaved_changes_on_session = True

    def flowtype_used(self, flowtype_key):
        """
        This function takes a key to a flowtype and checks, wether the flowtype is currently being used within the factory
        :param flowtype_key: [str] key of a flowtype to analyze
        :return: [bool] True, if flowtype is used somewhere in the current setup, otherwise False
        """
        for component in self.blueprint.components.values():
            if component["flowtype"].key == flowtype_key:
                return True
        for connection in self.blueprint.connections.values():
            if connection["flowtype"].key == flowtype_key:
                return True
        return False

    def get_key(self, given_name):
        """
        This method takes an asset name and returns the corresponding key that the component can be adressed with in the blueprint
        """

        # search name in component dict
        for component in self.blueprint.components.values():
            if component["name"] == given_name:
                return component["key"]

        # search name in connection dict
        for connection in self.blueprint.connections.values():
            if connection["name"] == given_name:
                return connection["key"]

        # search name in flow dict
        for flowtype in self.blueprint.flowtypes.values():
            if flowtype.name == given_name:
                return flowtype.key

        # search for name in unit dict
        for unit in self.blueprint.units.values():
            if unit.name == given_name:
                return unit.key

        return None

    def import_timeseries(self):
        """
        This function lets the user choose an excel file containing timeseries and imports all of them to the tool
        """

        # ask for filename
        filetype = [("xlsx", "*.xlsx")]
        filepath = filedialog.askopenfilename(
            defaultextension=filetype, filetypes=filetype
        )

        if not filepath == "":
            # import the excel sheet
            self.timeseries = pd.read_excel(filepath, sheet_name="Timeseries")

            if not self.dialog == None:
                # update the list of available timeseries
                self.update_timeseries_list()

        # inform the user
        Snackbar(text=f"{len(self.timeseries.keys())} new timeseries imported").open()

    def increase_scaling_factor(self):
        self.session_data["display_scaling_factor"] = (
            self.session_data["display_scaling_factor"] * 1.05
        )
        self.initialize_visualization()

    def initialize_visualization(self, *args):
        """
        This script builds the basic energy system visualisation out of the given blueprint on the Canvas within the system layout tab of the GUI
        """

        scaling_factor = (
            self.session_data["display_scaling_factor"]
            * self.root.ids.canvas_layout.size[0]
            / 1000
            / (len(self.blueprint.components) + 1) ** (0.25)
        )

        # specify height of components in px. Standard is 100px, the blueprint provides an additional scaling factor
        component_height = 100 * scaling_factor

        # specify display widths of components in px depending on their type
        component_width = {
            "source": component_height,
            "sink": component_height,
            "pool": component_height,
            "storage": component_height * 1.5,
            "converter": component_height * 1.5,
            "deadtime": component_height * 1.5,
            "thermalsystem": component_height * 1.5,
            "triggerdemand": component_height * 1.5,
            "schedule": component_height * 1.5,
        }

        # specify canvas dimensions
        self.root.ids.canvas_layout.pos = self.root.ids.layout_area.pos
        self.root.ids.canvas_layout.size = self.root.ids.layout_area.size

        # store pointer to canvas to make following code better readable
        canvas = self.root.ids.canvas_layout.canvas

        # clear the canvas
        canvas.clear()

        # predefine lines for connections
        # TODO: This step is needed to have them at the background under the component labels
        #  ...change this if there is a better way to get this behaviour
        for connection in self.blueprint.connections.values():
            # get connection color from blueprint
            connection_color = connection["flowtype"].color.rgba

            # set line color
            canvas.add(
                Color(
                    connection_color[0],
                    connection_color[1],
                    connection_color[2],
                    connection_color[3],
                )
            )

            # create a new line object (with random points - they will be defined correctly later)
            new_line = Line(
                points=(0, 0, 1000, 1000),
                width=8 * self.session_data["display_scaling_factor"],
            )  #

            # place it on the canvas
            canvas.add(new_line)

            # inititalize small rectangles to display the directions of the flows
            # make them a little darker than the flow itself
            canvas.add(
                Color(
                    connection_color[0] * 0.6,
                    connection_color[1] * 0.6,
                    connection_color[2] * 0.6,
                    connection_color[3],
                )
            )
            pointer_start = Triangle(points=(0, 0, 0, 0, 0, 0))
            pointer_end = Triangle(points=(0, 0, 0, 0, 0, 0))
            canvas.add(pointer_start)
            canvas.add(pointer_end)

            # store pointer to line and rectangles in the app to make it adressable later
            self.root.ids[f"line_{connection['key']}"] = new_line
            self.root.ids[f"pointer_start_{connection['key']}"] = pointer_start
            self.root.ids[f"pointer_end_{connection['key']}"] = pointer_end

        # add a line to be used for connection preview while creating new connections
        canvas.add(Color(0.5, 0.5, 0.5, 1))
        new_line = Line(
            points=(-10, -10, -10, -10),
            width=8 * self.session_data["display_scaling_factor"],
        )
        canvas.add(new_line)
        self.root.ids[f"line_preview"] = new_line

        # add a label to highlight components
        highlight_label = Image()
        self.root.ids.canvas_layout.add_widget(highlight_label)
        self.root.ids["highlight"] = highlight_label
        self.root.ids["highlight"].pos = [
            -1000,
            -1000,
        ]  # move the highlight out of sight on startup

        # create assets according to the blueprint:
        for component in self.blueprint.components.values():
            # create draglabel for the icon of the component
            component_framelabel = DragLabel(
                source=component["GUI"]["icon"],
                size=(component_width[component["type"]], component_height),
                id=component["key"],
            )
            # place it on the canvas and add it to the id-list of the application
            self.root.ids.canvas_layout.add_widget(component_framelabel)
            self.root.ids[f"frame_{component['key']}"] = component_framelabel

            # create a textlabel and place it on the canvas + add it to the id list
            component_textlabel = MDLabel(
                text=component["name"].upper(), halign="center"
            )
            self.root.ids.canvas_layout.add_widget(component_textlabel)
            self.root.ids[f"text_{component['key']}"] = component_textlabel

            # assign the correct position to the new asset
            component_framelabel.pos = (
                self.root.ids.canvas_layout.pos[0]
                - component_width[component["type"]] / 2
                + (self.root.ids.canvas_layout.width - 100)
                * component["GUI"]["position_x"]
                / self.display_grid_size[0]
                + 50,
                self.root.ids.canvas_layout.pos[1]
                - component_height / 2
                + (self.root.ids.canvas_layout.height - 100)
                * component["GUI"]["position_y"]
                / self.display_grid_size[1]
                + 50,
            )

            # if the component is a pool: create a circle in the correct color
            if component["type"] == "pool":
                # exchange the icon with an empty one
                component_framelabel.source = "Assets\\empty_rectangle.png"
                # determine of the color of the pool
                if component["flowtype"].key == "unknown":
                    canvas.add(Color(0.1137, 0.2588, 0.463, 1))
                else:
                    pool_color = component["flowtype"].color.rgba
                    canvas.add(
                        Color(
                            pool_color[0], pool_color[1], pool_color[2], pool_color[3]
                        )
                    )
                outer_circle = Ellipse(
                    pos=(800, 800), size=(component_height, component_height)
                )
                canvas.add(outer_circle)

                # create a second circle to fill the middle
                canvas.add(Color(0.98, 0.98, 0.98, 1))
                inner_circle = Ellipse(
                    pos=(820, 820),
                    size=(
                        component_height
                        - 32 * self.session_data["display_scaling_factor"],
                        component_height
                        - 32 * self.session_data["display_scaling_factor"],
                    ),
                )
                canvas.add(inner_circle)

                # give them IDs
                self.root.ids[f"outer_circle_{component['key']}"] = outer_circle
                self.root.ids[f"inner_circle_{component['key']}"] = inner_circle

                # place them correctly
                self.root.ids[
                    f"outer_circle_{component['key']}"
                ].pos = component_framelabel.pos
                self.root.ids[f"inner_circle_{component['key']}"].pos = (
                    component_framelabel.pos[0]
                    + 16 * self.session_data["display_scaling_factor"],
                    component_framelabel.pos[1]
                    + 16 * self.session_data["display_scaling_factor"],
                )

        # assign callback to all icons (this line calls update_visualization each time as well)
        for component in self.blueprint.components.values():
            self.root.ids[
                f"text_{component['key']}"
            ].on_touch_move = self.update_visualization
            self.root.ids[f"frame_{component['key']}"].bind(
                on_touch_up=lambda touch, instance: self.click_on_component(
                    touch, instance
                )
            )

        # add the new-connection-button
        new_connection_button = MDFillRoundFlatIconButton(
            icon="plus",
            text="Add connection",
            icon_size=20,
            pos=(800, 800),
            on_release=self.initiate_new_connection,
        )
        self.root.ids.canvas_layout.add_widget(new_connection_button)
        self.root.ids["new_connection"] = new_connection_button

        self.update_visualization()

    def initiate_asset_selection(self, key):
        # was the calling asset already selected?-> do nothing
        if not self.selected_asset == None and self.selected_asset["key"] == key:
            return

        # -> no unsaved changes? -> change asset
        elif not self.unsaved_changes_on_asset:
            self.change_selected_asset(key)

        # unsaved changes -> ask the user what to do
        else:
            # create dialog
            btn_false = MDFlatButton(text="Cancel")
            btn_true = MDRaisedButton(text="Dismiss Changes")
            self.dialog = MDDialog(
                title="Unsaved changes on current asset",
                text="There are unsaved changes on the current asset which will be deleted. Continue?",
                buttons=[btn_false, btn_true],
            )
            btn_false.bind(on_release=self.dialog.dismiss)
            btn_true.bind(on_release=lambda instance: self.change_selected_asset(key))
            self.dialog.open()

    def initiate_new_connection(self, *args):
        print("NEW CONNECTION BUTTON PRESSED")
        self.connection_edit_mode = True
        Window.bind(mouse_pos=lambda _, pos: self.update_visualization(mouse_pos=pos))

        self.root.ids["new_connection"].text = "Cancel"
        self.root.ids["new_connection"].icon = "cancel"
        self.root.ids["new_connection"].unbind(on_release=self.initiate_new_connection)
        self.root.ids["new_connection"].bind(on_release=self.abort_new_connection)

    def initialize_units_and_flowtypes(self):
        """
        This function creates the basic set of units and flowtypes required
        """
        # initialize the basic units
        self.blueprint.units["energy"] = Unit.Unit(
            key="energy",
            quantity_type="energy",
            conversion_factor=1,
            magnitudes=[1, 1000, 1000000, 1000000000, 1000000000000],
            units_flow=["kWh", "MWh", "GWh", "TWh", "PWh"],
            units_flowrate=["kW", "MW", "GW", "TW", "PW"],
            name="Energy [kW]",
        )
        self.blueprint.units["joule"] = Unit.Unit(
            key="joule",
            quantity_type="energy",
            conversion_factor=1 / 3600,
            magnitudes=[1, 1000, 1000000, 1000000000],
            units_flow=["kJ", "MJ", "GJ", "PJ"],
            units_flowrate=["kJ/h", "MJ/h", "GJ/h", "PJ/h"],
            name="Energy [Joule]",
        )
        self.blueprint.units["mmBTU"] = Unit.Unit(
            key="mmBTU",
            quantity_type="energy",
            conversion_factor=293.071070,
            magnitudes=[1],
            units_flow=["mmBTU"],
            units_flowrate=["mmBTU/h"],
            name="Energy [mmBTU]",
        )
        self.blueprint.units["mass"] = Unit.Unit(
            key="mass",
            quantity_type="mass",
            conversion_factor=1,
            magnitudes=[1, 1000, 1000000, 1000000000, 1000000000000],
            units_flow=["kg", "t", "kt", "mt", "gt"],
            units_flowrate=["kg/h", "t/h", "kt/h", "mt/h", "gt/h"],
            name="Mass [kg]",
        )
        self.blueprint.units["unit"] = Unit.Unit(
            key="unit",
            quantity_type="other",
            conversion_factor=1,
            magnitudes=[1],
            units_flow=["units"],
            units_flowrate=["units/h"],
            name="Unspecified Unit",
        )

        # initialize basic flowtypes
        self.blueprint.flowtypes["material_losses"] = ft.Flowtype(
            "material_losses",
            unit=self.blueprint.units["mass"],
            color="#555555",
            represents_losses=True,
            name="Material Losses",
            description="Built in default flowtype used to represent all kinds of material losses",
        )
        self.blueprint.flowtypes["energy_losses"] = ft.Flowtype(
            "energy_losses",
            unit=self.blueprint.units["energy"],
            color="#555555",
            represents_losses=True,
            name="Energy Losses",
            description="Built in default flowtype used to represent all kinds of energy losses",
        )

        self.blueprint.flowtypes["heat"] = ft.Flowtype(
            "heat",
            unit=self.blueprint.units["energy"],
            color="#996666",
            name="Heat",
            description="Built in default flowtype used to represent all kinds of heat",
        )

        self.blueprint.flowtypes["unknown"] = ft.Flowtype(
            "unknown",
            unit=self.blueprint.units["unit"],
            color="#999999",
            name="Unknown Flow",
            description="Built in default flowtype used as a fallback option for unspecified situations",
        )

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

    def new_scenario(self, *args, **kwargs):
        """
        This function creates a new empty scenario within the current session
        """

        # check if a scenario has been handed over
        if "data" in kwargs:
            new_scenario = kwargs["data"]
            scenario_name = new_scenario["name"]
            scenario_description = new_scenario["description"]

        else:
            # otherwise continue with given data

            # if no: take the data from the gui
            # get entered name and description
            scenario_name = self.dialog.content_cls.ids.textfield_new_scenario_name.text
            scenario_description = (
                self.dialog.content_cls.ids.textfield_new_scenario_description.text
            )

            # check that name entry field was not left empty and the name is not assigned yet
            if scenario_name == "" or scenario_name in self.scenarios.keys():
                btn_ok = MDFlatButton(text="OK")
                self.dialog = MDDialog(
                    title="Invalid Name",
                    text="Please enter a unique name for the new scenario",
                    buttons=[btn_ok],
                )
                self.dialog.open()
                btn_ok.bind(on_release=self.dialog.dismiss)
                return

            # close the naming dialog
            self.dialog.dismiss()

            # create new scenario as dict
            new_scenario = {
                "blueprint": {},
                "description": scenario_description,
                "image": "Assets\\scenarios\\scenario_default.jpg",
                "key": scenario_name,
                "location": [0, 0],
                "location_name": "Dortmund, Germany",
                "name": scenario_name,
                "result": {},
                "time_factor": 1,
                "timesteps": 168,
                "timestep_start": 1,
                "parameters": {},
                "year": 2023,
            }

        # create a card widget to show the scenario in UI
        card_widget = ScenarioCard(scenario_key=scenario_name)
        card_widget.id = scenario_name
        card_widget.ids.title.text = scenario_name
        card_widget.ids.description.text = scenario_description
        card_widget.ids.image.source = new_scenario["image"]
        card_widget.bind(
            on_press=lambda instance: self.update_scenario_config_screen(instance)
        )
        card_widget.ids.icon_copy.bind(
            on_release=lambda instance: self.copy_scenario(instance)
        )
        card_widget.ids.icon_delete.bind(
            on_release=lambda instance: self.show_scenario_deletion_dialog(instance)
        )
        self.root.ids.grid_scenarios.add_widget(card_widget)

        # assign the cardwidget to the scenario
        new_scenario["card_widget"] = card_widget

        # add new scenario to the global scenario list
        self.scenarios.update({scenario_name: new_scenario})

        # set the new scenario as the selected one
        self.selected_scenario = new_scenario

        # session contains unsaved changes now:
        self.unsaved_changes_on_session = True

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

    def save_session_as(self):
        """
        This function is used to create a copy of a session. First the user is asked to provide a directory where the new session shall be created. Then the regular save_session() method is being called
        """
        # ask for filepath
        filepath_new = filedialog.askdirectory()

        # make sure the user didn't abort the file selection or selected something invalid
        if filepath_new == None or filepath_new == "":
            return

        # set the filepath as the new session_path
        self.session_data["session_path"] = filepath_new

        # call the regular safe session routine
        self.save_session()

    def save_changes_on_flowtype(self):
        """
        This function checks the current user inputs in the flowetype definition window for validity and writes the values
        into the currently selected flowtype object
        """
        # get the current flowtype
        flowtype = self.blueprint.flowtypes[
            self.get_key(self.dialog.content_cls.ids.label_flowtype_name.text)
        ]

        # check, that the given name is unique
        if (
            not self.dialog.content_cls.ids.textfield_flowtype_name.text
            == flowtype.name
        ):
            if self.get_key(self.dialog.content_cls.ids.textfield_flowtype_name.text):
                self.dialog.content_cls.ids.textfield_flowtype_name.error = True
                return
        self.dialog.content_cls.ids.textfield_flowtype_name.error = False

        # write values from GUI to the flowtype
        flowtype.name = self.dialog.content_cls.ids.textfield_flowtype_name.text
        flowtype.description = (
            self.dialog.content_cls.ids.textfield_flowtype_description.text
        )
        flowtype.unit = self.blueprint.units[
            self.get_key(self.dialog.content_cls.ids.textfield_flowtype_unit.text)
        ]
        flowtype.color = color.color(
            self.dialog.content_cls.ids.icon_flowtype_color.icon_color
        )
        flowtype.represents_losses = (
            self.dialog.content_cls.ids.checkbox_flowtype_losses.active
        )

        # update name-label of the gui
        self.dialog.content_cls.ids.label_flowtype_name.text = (
            self.dialog.content_cls.ids.textfield_flowtype_name.text
        )

        # no more unsaved changes on the current flow
        self.dialog.content_cls.ids.button_flowtype_save.disabled = True

        # set unsaved changes to true
        self.unsaved_changes_on_session = True

        # refresh list on screen
        self.update_flowtype_list()

        # refresh visualisation to adapt new color
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{flowtype.name} updated!").open()

    def save_changes_on_converter(self):
        """
        This function takes the user input from the converter configuration tab and stores it in the blueprint
        """

        # store key of old version
        key = self.selected_asset["key"]

        # make sure that the given name is not taken yet
        if not self.blueprint.components[key][
            "name"
        ] == self.root.ids.textfield_converter_name.text and self.get_key(
            self.root.ids.textfield_converter_name.text
        ):
            self.show_info_popup(
                "The given name is already assigned within the factory!"
            )
            return

        if (
            not (self.root.ids.textfield_converter_power_max.value_valid)
            and (self.root.ids.textfield_converter_power_min.value_valid)
            and (self.root.ids.textfield_converter_availability.value_valid)
            and (self.root.ids.textfield_converter_rampup.value_valid)
            and (self.root.ids.textfield_converter_rampdown.value_valid)
            and (self.root.ids.textfield_converter_eta_max.value_valid)
            and (self.root.ids.textfield_converter_power_nominal.value_valid)
            and (self.root.ids.textfield_converter_delta_eta_high.value_valid)
            and (self.root.ids.textfield_converter_delta_eta_low.value_valid)
        ):
            self.show_info_popup(
                "Changes can not be stored due to invalid values remaining"
            )
            return

        self.blueprint.components[key].update(
            {
                "name": self.root.ids.textfield_converter_name.text,
                "description": self.root.ids.textfield_converter_description.text,
            }
        )
        self.blueprint.components[key]["GUI"].update(
            {"icon": self.root.ids.image_converter_configuration.source}
        )

        # go through all numerical parameters
        for parameter in [
            "power_max",
            "power_min",
            "availability",
            "max_pos_ramp_power",
            "max_neg_ramp_power",
            "eta_max",
            "power_nominal",
            "delta_eta_high",
            "delta_eta_low",
        ]:
            # get the pointer to the corresponding textfield
            textfield = getattr(self.root.ids, f"textfield_converter_{parameter}")
            # check if the user specified it
            if not textfield.text == "":
                # if yes: safe the value in the parameters dict
                self.parameters[key][parameter] = float(textfield.text)

        # update connection names to adapt changes if the name of the converter has changed
        self.update_connection_names()

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the visualisation:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

        # storage doppelt vorhanden
        """
    def save_changes_on_storage(self):
        """
        # This function takes the user input from the storage configuration tab and stores it in the blueprint
        """

        # store key of old version
        component_key = self.get_key(self.selected_asset["name"])

        # create a new blueprint entry with given values
        storage_new = {}
        storage_new = {"name": self.root.ids.textfield_storage_name.text,
                       "key": component_key,
                       "type": "storage",
                       "description": self.root.ids.textfield_storage_description.text,
                       #"flow": self.get_key(self.root.ids.textfield_storage_flowtype.text),
                       "Maximum charging power": self.root.ids.textfield_storage_charge_max.text,
                       "Minimum charging power": self.root.ids.textfield_storage_charge_min.text,
                       "Maximum discharging power": self.root.ids.textfield_storage_discharge_max.text,
                       "Minimum discharging power": self.root.ids.textfield_storage_discharge_min.text,
                       "Capacity": self.root.ids.textfield_storage_capacity.text,
                       "SoC Start": self.root.ids.textfield_storage_start.text,
                       "leakage time": self.root.ids.textfield_storage_leakage_time.text,
                       "leakage SoC": self.root.ids.textfield_storage_leakage_SoC.text,
                       "Maximum efficiency": self.root.ids.textfield_storage_efficiency_max.text,
                       "icon": self.root.ids.image_storage_configuration.source,
                       "position_x": self.selected_asset["GUI"]["position_x"],
                       "position_y": self.selected_asset["GUI"]["position_y"]}

        # overwrite old entry
        self.blueprint.components[component_key] = storage_new

        # set selected asset to the updated storage
        self.selected_asset = storage_new

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the visualisation:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()
    """

    def save_changes_on_deadtime(self):
        """
        This function takes the user input from the deadtime configuration tab and stores it in the blueprint
        """

        # get component_key
        key = self.selected_asset["key"]

        # make sure that the given name is not taken yet
        if not self.blueprint.components[key][
            "name"
        ] == self.root.ids.textfield_sink_name.text and self.get_key(
            self.root.ids.textfield_sink_name.text
        ):
            self.show_info_popup(
                "The given name is already assigned within the factory!"
            )
            return

        if not (self.root.ids.textfield_deadtime_delay.value_valid):
            self.show_info_popup(
                "Changes can not be stored due to invalid values remaining"
            )
            return

        # update general attributes and icon
        self.blueprint.components[key].update(
            {
                "name": self.root.ids.textfield_deadtime_name.text,
                "description": self.root.ids.textfield_deadtime_description.text,
            }
        )
        self.blueprint.components[key]["GUI"].update(
            {"icon": self.root.ids.image_deadtime_configuration.source}
        )
        # change the flowtype if the user specified a new one
        flowtype_key = self.get_key(self.root.ids.textfield_deadtime_flowtype.text)
        if not self.blueprint.components[key]["flowtype"].key == flowtype_key:
            fd.set_component_flowtype(
                self.blueprint, key, self.blueprint.flowtypes[flowtype_key]
            )

        if not self.root.ids.textfield_deadtime_delay.text == "":
            self.parameters[key]["delay"] = int(
                self.root.ids.textfield_deadtime_delay.text
            )

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the visualisation:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_schedule(self):
        """
        This function takes the user input from the schedule configuration tab and stores it in the blueprint
        """

        # store key of old version
        component_key = self.get_key(self.selected_asset["name"])

        if not (self.root.ids.textfield_schedule_power_max.value_valid):
            self.show_info_popup(
                "Changes can not be stored due to invalid values remaining"
            )
            return

        # create a new blueprint entry with given values
        schedule_new = {}
        schedule_new = {
            "name": self.root.ids.textfield_schedule_name.text,
            "key": component_key,
            "type": "schedule",
            "description": self.root.ids.textfield_schedule_description.text,
            # "flow": self.get_key(self.root.ids.textfield_schedule_flowtype.text),
            "Maximum power flow": self.root.ids.textfield_schedule_power_max.text,
            "icon": self.root.ids.image_schedule_configuration.source,
            "position_x": self.selected_asset["GUI"]["position_x"],
            "position_y": self.selected_asset["GUI"]["position_y"],
        }

        # overwrite old entry
        self.blueprint.components[component_key] = schedule_new

        # set selected asset to the updated schedule
        self.selected_asset = schedule_new

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the visualisation:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_pool(self):
        """
        This function takes the user input from the pool configuration tab and stores it in the blueprint
        """

        # get component_key
        key = self.selected_asset["key"]

        # make sure that the given name is not taken yet
        if not self.blueprint.components[key][
            "name"
        ] == self.root.ids.textfield_pool_name.text and self.get_key(
            self.root.ids.textfield_pool_name.text
        ):
            self.show_info_popup(
                "The given name is already assigned within the factory!"
            )
            return

        # create new blueprint entry
        self.blueprint.components[key].update(
            {
                "name": self.root.ids.textfield_pool_name.text,
                "description": self.root.ids.textfield_pool_description.text,
            }
        )

        # change the flowtype if the user specified a new one
        flowtype_key = self.get_key(self.root.ids.textfield_pool_flowtype.text)
        if not self.blueprint.components[key]["flowtype"].key == flowtype_key:
            fd.set_component_flowtype(
                self.blueprint, key, self.blueprint.flowtypes[flowtype_key]
            )

        # update connection names to adapt changes if the name of the pool has changed
        self.update_connection_names()
        # update flowtype list to adapt changes if a flowtype has to be locked or unlocked
        self.update_flowtype_list()

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the preview:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_sink(self):
        """
        This function takes the user input from the sink configuration tab and stores it in the blueprint
        """

        # get component_key
        key = self.selected_asset["key"]

        # make sure that the given name is not taken yet
        if not self.blueprint.components[key][
            "name"
        ] == self.root.ids.textfield_sink_name.text and self.get_key(
            self.root.ids.textfield_sink_name.text
        ):
            self.show_info_popup(
                "The given name is already assigned within the factory!"
            )
            return

        # Check, that all user inputs are valid
        if (
            not (self.root.ids.textfield_sink_cost.value_valid)
            and (self.root.ids.textfield_sink_refund.value_valid)
            and (self.root.ids.textfield_sink_co2_emission.value_valid)
            and (self.root.ids.textfield_sink_co2_refund.value_valid)
            and (self.root.ids.textfield_sink_power_max.value_valid)
            and (self.root.ids.textfield_sink_power_min.value_valid)
            and (self.root.ids.textfield_sink_demand.value_valid)
        ):
            self.show_info_popup(
                "Changes can not be stored due to invalid values remaining"
            )
            return

        # update general attributes and icon
        self.blueprint.components[key].update(
            {
                "name": self.root.ids.textfield_sink_name.text,
                "description": self.root.ids.textfield_sink_description.text,
            }
        )
        self.blueprint.components[key]["GUI"].update(
            {"icon": self.root.ids.image_sink_configuration.source}
        )

        # change the flowtype if the user specified a new one
        flowtype_key = self.get_key(self.root.ids.textfield_sink_flowtype.text)
        if not self.blueprint.components[key]["flowtype"].key == flowtype_key:
            fd.set_component_flowtype(
                self.blueprint, key, self.blueprint.flowtypes[flowtype_key]
            )

        # go through all numerical parameters
        for parameter in [
            "cost",
            "power_max",
            "power_min",
            "demand",
            "revenue",
            "co2_emission_per_unit",
            "co2_refund_per_unit",
        ]:
            # get the pointer to the corresponding textfield
            textfield = getattr(self.root.ids, f"textfield_sink_{parameter}")
            # check if the user specified it
            if not textfield.text == "":
                # if yes: safe the value in the parameters dict
                self.parameters[key][parameter] = float(textfield.text)

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # update connection names to adapt changes if the name of the sink has changed
        self.update_connection_names()
        # update flowtype list to adapt changes if a flowtype has to be locked or unlocked
        self.update_flowtype_list()

        # redraw the preview:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_source(self):
        """
        This function takes the user input from the source configuration tab and stores it in the blueprint
        """

        # get component_key
        key = self.selected_asset["key"]

        # make sure that the given name is not taken yet
        if not self.blueprint.components[self.selected_asset["key"]][
            "name"
        ] == self.root.ids.textfield_source_name.text and self.get_key(
            self.root.ids.textfield_source_name.text
        ):
            self.show_info_popup(
                "The given name is already assigned within the factory!"
            )
            return

            # Check, that all user inputs are valid
            if (
                not (self.root.ids.textfield_source_power_max.value_valid)
                and (self.root.ids.textfield_source_power_min.value_valid)
                and (self.root.ids.textfield_source_determined_power.value_valid)
                and (self.root.ids.textfield_source_availability.value_valid)
                and (self.root.ids.textfield_source_capacity_charge.value_valid)
                and (self.root.ids.textfield_source_emissions.value_valid)
                and (self.root.ids.textfield_source_cost.value_valid)
            ):
                self.show_info_popup(
                    "Changes can not be stored due to invalid values remaining"
                )
                return

        # update general attributes and icon
        self.blueprint.components[key].update(
            {
                "name": self.root.ids.textfield_source_name.text,
                "description": self.root.ids.textfield_source_description.text,
            }
        )
        self.blueprint.components[key]["GUI"].update(
            {"icon": self.root.ids.image_source_configuration.source}
        )

        # change the flowtype if the user specified a new one
        flowtype_key = self.get_key(self.root.ids.textfield_source_flowtype.text)
        if not self.blueprint.components[key]["flowtype"].key == flowtype_key:
            fd.set_component_flowtype(
                self.blueprint, key, self.blueprint.flowtypes[flowtype_key]
            )

        # update parameter list
        # costs
        if not self.root.ids.textfield_source_cost.text == "":
            self.parameters[key]["cost"] = self.root.ids.textfield_source_cost.text
        # power_max
        if not self.root.ids.textfield_source_power_max.text == "":
            self.parameters[key][
                "power_max"
            ] = self.root.ids.textfield_source_power_max.text
        # power_min
        if not self.root.ids.textfield_source_power_min.text == "":
            self.parameters[key][
                "power_min"
            ] = self.root.ids.textfield_source_power_min.text
        # determined_power
        if not self.root.ids.textfield_source_determined_power.text == "":
            self.parameters[key][
                "determined_power"
            ] = self.root.ids.textfield_source_determined_power.text
        # availability
        if not self.root.ids.textfield_source_availability.text == "":
            self.parameters[key][
                "availability"
            ] = self.root.ids.textfield_source_availability.text
        # co2_emission_per_unit
        if not self.root.ids.textfield_source_co2_emission_per_unit.text == "":
            self.parameters[key][
                "co2_emission_per_unit"
            ] = self.root.ids.textfield_source_co2_emission_per_unit.text
        # capacity_charge
        if not self.root.ids.textfield_source_capacity_charge.text == "":
            self.parameters[key][
                "capacity_charge"
            ] = self.root.ids.textfield_source_capacity_charge.text

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # update connection names to adapt changes if the name of the source has changed
        self.update_connection_names()
        # update flowtype list to adapt changes if a flowtype has to be locked or unlocked
        self.update_flowtype_list()

        # redraw the preview:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_storage(self):
        """
        This function takes the user input from the storage configuration tab and stores it in the blueprint
        """

        # get component_key
        key = self.selected_asset["key"]

        # make sure that the given name is not taken yet
        if not self.blueprint.components[key][
            "name"
        ] == self.root.ids.textfield_storage_name.text and self.get_key(
            self.root.ids.textfield_storage_name.text
        ):
            self.show_info_popup(
                "The given name is already assigned within the factory!"
            )
            return

        # Check, that all user inputs are valid
        if (
            not (self.root.ids.textfield_storage_capacity.value_valid)
            and (self.root.ids.textfield_storage_power_max_charge.value_valid)
            and (self.root.ids.textfield_storage_power_max_discharge.value_valid)
            and (self.root.ids.textfield_storage_soc_start.value_valid)
            and (self.root.ids.textfield_storage_efficiency.value_valid)
            and (self.root.ids.textfield_storage_leakage_time.value_valid)
            and (self.root.ids.textfield_storage_leakage_soc.value_valid)
        ):
            self.show_info_popup(
                "Changes can not be stored due to invalid values remaining"
            )
            return

        # update general attributes and icon
        self.blueprint.components[key].update(
            {
                "description": self.root.ids.textfield_storage_description.text,
                "name": self.root.ids.textfield_storage_name.text,
            }
        )
        self.blueprint.components[key]["GUI"].update(
            {"icon": self.root.ids.image_storage_configuration.source}
        )
        # change the flowtype if the user specified a new one
        flowtype_key = self.get_key(self.root.ids.textfield_storage_flowtype.text)
        if not self.blueprint.components[key]["flowtype"].key == flowtype_key:
            fd.set_component_flowtype(
                self.blueprint, key, self.blueprint.flowtypes[flowtype_key]
            )

        # go through all numerical parameters
        for parameter in [
            "capacity",
            "power_max_charge",
            "power_max_discharge",
            "soc_start",
            "efficiency",
            "leakage_time",
            "leakage_soc",
        ]:
            # get the pointer to the corresponding textfield
            textfield = getattr(self.root.ids, f"textfield_storage_{parameter}")
            # check if the user specified it
            if not textfield.text == "":
                # if yes: safe the value in the parameters dict
                self.parameters[key][parameter] = float(textfield.text)

        # update connection names to adapt changes if the name of the storage has changed
        self.update_connection_names()

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the preview:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_thermalsystem(self):
        """
        This function takes the user input from the thermal system configuration tab and stores it in the blueprint
        """

        # alle textfelder der komponente durchgehen
        # wenn textfeld.aktueller wert gültig = False -> Error popup
        # if not (textfield1.valid AND textfield2.valied AND...)
        #     error
        # Check, that all user inputs are valid
        if (
            not (self.root.ids.textfield_thermalsystem_temperature_start.value_valid)
            and (self.root.ids.textfield_thermalsystem_temperature_.value_valid)
            and (self.root.ids.textfield_thermalsystem_temperature_max.value_valid)
            and (self.root.ids.textfield_thermalsystem_temperature_min.value_valid)
            and (self.root.ids.textfield_thermalsystem_sustainable.value_valid)
            and (self.root.ids.textfield_thermalsystem_R.value_valid)
            and (self.root.ids.textfield_thermalsystem_C.value_valid)
        ):
            self.show_info_popup(
                "Changes can not be stored due to invalid values remaining"
            )
            return

        # store key of old version
        component_key = self.get_key(self.selected_asset["name"])

        # create a new blueprint entry with given values
        thermalsystem_new = {}
        thermalsystem_new = {
            "name": self.root.ids.textfield_thermalsystem_name.text,
            "key": component_key,
            "type": "thermalsystem",
            "description": self.root.ids.textfield_thermalsystem_description.text,
            # "flow": self.get_key(self.root.ids.textfield_thermalsystem_flowtype.text),
            "Start temperature": self.root.ids.textfield_thermalsystem_temperature_start.text,
            "ambient temperature": self.root.ids.textfield_thermalsystem_temperature_ambient.text,
            "maximum temperature": self.root.ids.textfield_thermalsystem_temperature_max.text,
            "minimum temperature": self.root.ids.textfield_thermalsystem_temperature_min.text,
            "sustainable": self.root.ids.textfield_thermalsystem_sustainable.text,
            "R": self.root.ids.textfield_thermalsystem_R.text,
            "C": self.root.ids.textfield_thermalsystem_C.text,
            "icon": self.root.ids.image_thermalsystem_configuration.source,
            "position_x": self.selected_asset["GUI"]["position_x"],
            "position_y": self.selected_asset["GUI"]["position_y"],
            "scenario_temperature_ambient": self.root.ids.switch_thermalsystem_temperature_ambient.active,
            "scenario_temperature_max": self.root.ids.switch_thermalsystem_temperature_max.active,
            "scenario_temperature_min": self.root.ids.switch_thermalsystem_temperature_min.active,
        }

        # overwrite old entry
        self.blueprint.components[component_key] = thermalsystem_new

        # set selected asset to the updated thermalsystem
        self.selected_asset = thermalsystem_new

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the visualisation:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

        # textfield_thermalsystem_temperature_start = self.screen.ids.textfield_thermalsystem_temperature_start
        # textfield_thermalsystem_temperature_ambient = self.screen.ids.textfield_thermalsystem_temperature_ambient

    def save_component_positions(self):
        """
        This function is called everytime when a component has been moven by the user within the layout visualisation.
        It checks the current positions of all components for deviations from their last known location.
        If a position deviates more than the expected rounding error the new position is stored in the blueprint
        """

        # create a factor that determines the size of displayed components depending on the canvas size and the number
        # of elements to be displayed. The concrete function is try and error and my be changed during development
        scaling_factor = (
            self.session_data["display_scaling_factor"]
            * self.root.ids.canvas_layout.size[0]
            / 1000
            / (len(self.blueprint.components) + 1) ** (0.3)
        )

        # specify size of the components depending on the determined scaling factor
        component_height = 100 * scaling_factor  # height in px

        # specify display widths of components in px depending on their type and the scaling factor
        component_width = {
            "source": component_height,
            "sink": component_height,
            "pool": component_height,
            "storage": component_height * 1.5,
            "converter": component_height * 1.5,
            "deadtime": component_height * 1.5,
            "thermalsystem": component_height * 1.5,
            "triggerdemand": component_height * 1.5,
            "schedule": component_height * 1.5,
        }

        # keep track if there had been any changes
        changes_done = False

        # iterate over all components
        for component in self.blueprint.components.values():
            # calculate the current relative position on the canvas for the component
            current_pos_x = round(
                (
                    self.root.ids[f"frame_{component['key']}"].pos[0]
                    - 50
                    - self.root.ids.canvas_layout.pos[0]
                    + component_width[component["type"]] / 2
                )
                / (self.root.ids.canvas_layout.width - 100)
                * self.display_grid_size[0],
                0,
            )
            current_pos_y = round(
                (
                    self.root.ids[f"frame_{component['key']}"].pos[1]
                    - 50
                    - self.root.ids.canvas_layout.pos[1]
                    + component_height / 2
                )
                / (self.root.ids.canvas_layout.height - 100)
                * self.display_grid_size[1],
                0,
            )

            # make sure that the new position is within the grid. If not: move tho component to the closest border
            if current_pos_x < 0:
                current_pos_x = 0
            if current_pos_x > self.display_grid_size[0]:
                current_pos_x = self.display_grid_size[0]
            if current_pos_y < 0:
                current_pos_y = 0
            if current_pos_y > self.display_grid_size[1]:
                current_pos_y = self.display_grid_size[1]

            # check, if window size is big enough to avoid rounding errors
            if (
                self.root.ids.canvas_layout.width > 800
                and self.root.ids.canvas_layout.height > 500
            ):

                # Check, if the component has been dragged on top of the recycle bin to delete it..
                if (
                    self.root.ids[f"frame_{component['key']}"].pos[0]
                    < self.root.ids.icon_delete_component.pos[0]
                    + self.root.ids.icon_delete_component.size[0]
                ) and (
                    self.root.ids[f"frame_{component['key']}"].pos[1]
                    < self.root.ids.icon_delete_component.pos[1]
                    + self.root.ids.icon_delete_component.size[1]
                ):
                    # if yes: select the asset
                    self.selected_asset = self.blueprint.components[component["key"]]

                    # call deletion method
                    self.show_component_deletion_dialog()

                    self.update_visualization()

                else:
                    # if x coordinate of the component has changed more than expected rounding error:
                    if not current_pos_x - component["GUI"]["position_x"] == 0:
                        component["GUI"]["position_x"] = current_pos_x
                        changes_done = True

                    # if y coordinate of the component has changed more than expected rounding error: store it
                    if not current_pos_y - component["GUI"]["position_y"] == 0:
                        component["GUI"]["position_y"] = current_pos_y
                        changes_done = True

        # mark session as changed if changes have been done:
        if changes_done:
            self.unsaved_changes_on_session = True
            self.initialize_visualization()

    def select_flowtype_list_item(self, list_item, touch):
        """
        This function is called whenever the user clicks on a flowtype within the flowtype list on the flowtypet dialog. It checks, if there are any unsaved changes on the current selection. If yes the user is asked to save or discard them. Then a new flowtype is created or another flowtype is selected based on the list item clicked by the user.
        """

        # check, if the function call actually came from an object that has been clicked/moved
        if not list_item.collide_point(*touch.pos):
            # abort if not
            return

        if list_item.text == "Add Flowtype":
            self.add_flowtype()
        else:
            self.show_flowtype_config_dialog()
            self.select_flowtype(self.blueprint.flowtypes[self.get_key(list_item.text)])

    def select_flowtype(self, flowtype):
        """
        This function configures the flowtype-definition gui in a way that it displays all the values of the flowtype handed over
        """
        # write values of unit into the gui
        self.dialog.content_cls.ids.label_flowtype_name.text = flowtype.name
        self.dialog.content_cls.ids.textfield_flowtype_name.text = flowtype.name
        self.dialog.content_cls.ids.textfield_flowtype_description.text = (
            flowtype.description
        )
        self.dialog.content_cls.ids.textfield_flowtype_unit.text = flowtype.unit.name
        self.dialog.content_cls.ids.icon_flowtype_color.icon_color = (
            flowtype.color.tuple
        )
        self.dialog.content_cls.ids.checkbox_flowtype_losses.active = (
            flowtype.represents_losses
        )

        # no more unsaved changes -> disable save button
        self.dialog.content_cls.ids.button_flowtype_save.disabled = True

    def select_timeseries_list_item(self, list_item, touch):
        """
        This function is called everytime when the user selects a timeseries in the scenarioparameter definition.
        The selected timeseries is displayed in the preview window
        """

        # check, if the function call actually came from an object that has been clicked/moved
        if not list_item.collide_point(*touch.pos):
            # abort if not
            return

        # write the name of selected timeseries in the GUI
        self.root.ids.label_selected_timeseries.text = list_item.text

        # get data for selected timeseries and write it into self.selected_timeseries
        self.selected_timeseries = np.array(
            self.timeseries[list_item.text][1 : self.selected_scenario["timesteps"] + 1]
        )

        # set the scaling method to "Peak"
        self.root.ids.textfield_timeseries_scaling.text = "with a peak value of"

        # set the scaling value to the peak value of the selected timeseries
        self.root.ids.textfield_custom_timeseries.text = str(
            round(np.amax(self.selected_timeseries), 3)
        )

        # update preview
        self.update_timeseries_preview("Custom Timeseries")

    def select_parameter_list_item(self, list_item):
        """
        This function is called everytime when the user clicks on a configurable parameter within the parameter selction
        list in the scenario configuration window. The selected parameter is being loaded for editing
        """

        # get/create key for parameter
        parameter_key = f"{self.get_key(list_item.text)}_{list_item.secondary_text}"
        self.selected_parameter = {
            "key": parameter_key,
            "component": self.get_key(list_item.text),
            "attribute": list_item.secondary_text,
        }

        # Write the name of the parameter in the header of the configuration card
        self.root.ids.label_selected_parameter.text = (
            f"{list_item.text} | {list_item.secondary_text}"
        )

        # reset all UI elements
        self.root.ids.textfield_static_value.text = ""
        self.root.ids.textfield_static_value_unit.text = "kW"
        self.root.ids.textfield_custom_timeseries.text = ""
        self.root.ids.textfield_custom_timeseries_unit.text = "kW"

        # check, if the parameter has already been set within the scenario
        if parameter_key in self.selected_scenario["parameters"].keys():

            # get parameter data from the scenario
            parameter_data = self.selected_scenario["parameters"][parameter_key]
            # set the selected timeseries to the new values
            self.selected_timeseries = parameter_data["timeseries"]

            # check, which type of parameter is given
            if parameter_data["type"] == "static_value":
                # write the given values into the correct UI elements
                self.root.ids.textfield_static_value.text = str(
                    parameter_data["timeseries"][0]
                )
                self.root.ids.textfield_static_value_unit.text = parameter_data["unit"]

                # show the correct parameter type tab
                self.root.ids.parameter_tabs.switch_tab(
                    "Static Value", search_by="title"
                )
                self.update_timeseries_preview("Static Value")

            elif parameter_data["type"] == "custom_timeseries":
                # write the timeseries values into the correct UI elements, choose peak-mode for this
                self.root.ids.textfield_custom_timeseries.text = str(
                    round(np.amax(parameter_data["timeseries"]), 3)
                )
                self.root.ids.textfield_custom_timeseries_unit.text = parameter_data[
                    "unit"
                ]
                self.root.ids.textfield_timeseries_scaling.text = "with a peak value of"
                self.root.ids.label_selected_timeseries.text = parameter_data[
                    "description"
                ]

                # show the correct parameter type tab
                self.root.ids.parameter_tabs.switch_tab(
                    "Custom Timeseries", search_by="title"
                )
                self.update_timeseries_preview("Custom Timeseries")

        else:
            # if not: initialize the standard window
            # show the static value screen
            self.root.ids.parameter_tabs.switch_tab("Static Value", search_by="title")

            # initialize the value
            self.selected_timeseries = np.ones(self.selected_scenario["timesteps"])
            self.root.ids.textfield_static_value.text = "1"
            self.root.ids.textfield_static_value_unit.text = "kW"
            self.update_timeseries_preview("Static Value")

    def set_display_scaling_factor(self, *args):
        self.session_data["display_scaling_factor"] = (
            self.root.ids.layout_size_slider.value / 100 + 0.4
        )
        self.initialize_visualization()
        self.update_visualization()

    def set_parameter(self):
        """
        This function stores the currently displayed parameter configuration into the selected parameter of the selected scenario
        """

        # get value type
        value_type = self.root.ids.parameter_tabs.get_current_tab().title

        # set points depending on given user information
        if value_type == "Static Value":
            # write the currently given parameter specification into the scenario
            self.selected_scenario["parameters"][self.selected_parameter["key"]] = {
                "type": "static_value",
                "timeseries": self.selected_timeseries,
                "unit": self.root.ids.textfield_static_value_unit.text,
                "component": self.selected_parameter["component"],
                "attribute": self.selected_parameter["attribute"],
            }
        if value_type == "Custom Timeseries":
            # write the currently given parameter specification into the scenario
            self.selected_scenario["parameters"][self.selected_parameter["key"]] = {
                "type": "custom_timeseries",
                "timeseries": self.selected_timeseries,
                "unit": self.root.ids.textfield_custom_timeseries_unit.text,
                "component": self.selected_parameter["component"],
                "attribute": self.selected_parameter["attribute"],
                "description": self.root.ids.label_selected_timeseries.text,
            }

        # update the list of required scenario parameters
        self.update_scenario_parameter_list()

        # inform the user
        Snackbar(text=f"Parameter Set").open()

    def set_scenario_image(self, instance, touch):
        """
        This event is triggered when the user clicks on an image in the scenario image selection dialog.
        The selected image will be taken as the visualisation image for the current scenario
        """
        # abort if the event has not been triggered by the touched component
        if not instance.collide_point(*touch.pos):
            # abort if not
            return

        # set the image within the scenario card on the scenario overview screen
        self.selected_scenario["card_widget"].ids.image.source = instance.source

        # set the image in the current scenario
        self.selected_scenario["image"] = instance.source

        # display the image in the scenario configuration screen
        self.root.ids.image_scenario.source = instance.source

        # close the dialog
        self.dialog.dismiss()

    def set_unsaved_changes_on_asset(self, boolean):
        self.unsaved_changes_on_asset = boolean

    def show_color_picker(self):
        self.popup = MDColorPicker(size_hint=(0.3, 0.5), background_color=[1, 1, 1, 1])
        self.popup.open()
        self.popup.bind(
            on_release=self.update_flowtype_color,
        )

    def show_component_creation_menu(self):

        # COMPONENTS

        # define the component dummys to be created
        component_dummys = {
            "thermalsystem": {
                "id": "dummy_thermalsystem",
                "source": "Assets\\defaults\\thermalsystem.png",
            },
            "deadtime": {
                "id": "dummy_deadtime",
                "source": "Assets\\defaults\\deadtime.png",
            },
            "schedule": {
                "id": "dummy_schedule",
                "source": "Assets\\defaults\\schedule.png",
            },
            "storage": {
                "id": "dummy_storage",
                "source": "Assets\\defaults\\storage.png",
            },
            "converter": {
                "id": "dummy_converter",
                "source": "Assets\\defaults\\converter.png",
            },
            "pool": {
                "id": "dummy_pool",
                "source": "Assets\\defaults\\pool.png",
            },
            "sink": {"id": "dummy_sink", "source": "Assets\\defaults\\sink.png"},
            "source": {
                "id": "dummy_source",
                "source": "Assets\\defaults\\source.png",
            },
        }

        # get available height of the component canvas
        canvas_height = self.root.ids.canvas_shelf.size[1]
        canvas_width = self.root.ids.canvas_shelf.size[0]

        # calculate height for components
        component_height = canvas_height / (len(component_dummys) + 3)
        component_pos_x = (canvas_width - component_height * 1.5) / 2

        # clear component dummy canvas
        self.root.ids.canvas_shelf.canvas.clear()

        # iterate over all specified dummys and create them
        i = 0
        for type in component_dummys:
            # create draglabel for the icon of the component
            component_dummy = DragLabel(
                source=component_dummys[type]["source"],
                id=component_dummys[type]["id"],
                key=type,
                on_touch_up=lambda touch, instance: self.add_component(touch, instance),
            )
            component_dummy.pos = (
                component_pos_x + component_height * 0.25,
                canvas_height / len(component_dummys) * i + canvas_height * 0.15,
            )
            component_dummy.size = (component_height * 1.5, component_height)
            self.root.ids.canvas_shelf.add_widget(component_dummy)
            i += 1

        # show the component shelf
        self.root.ids.component_shelf.set_state("open")

    def show_component_deletion_dialog(self):

        # abort if there is no asset or a flow or connection selected
        if self.selected_asset == None or self.selected_asset["type"] in [
            "energy",
            "material",
            "connection",
        ]:
            return

        # create dialog
        btn_false = MDFlatButton(text="CANCEL")
        btn_true = MDRaisedButton(text="DELETE COMPONENT")
        self.dialog = MDDialog(
            title="Delete Component",
            buttons=[btn_false, btn_true],
            text="Do you really want to delete the component with all its adherent connections?",
        )
        btn_false.bind(on_release=self.dialog.dismiss)
        btn_true.bind(on_release=self.delete_component)
        self.dialog.open()

    def show_component_selection_dropdown(self, caller, exceptions=[]):
        """
        This function creates a dropdown menu giving the user the option to select one of the components in the blueprint.
        """

        def set_text(caller, text):
            # this function returns the user selection to the object that the dialog has been called from
            caller.text = text
            self.menu.dismiss()

        # initialize empty list
        dropdown_items = []
        # iterate over all components in the blueprint
        for component in self.blueprint.components.values():
            # filter sources
            if not component["type"] in exceptions:
                # append a dropdown item to the list
                dropdown_items.append(
                    {
                        "viewclass": "ImageDropDownItem",
                        "source": component["GUI"]["icon"],
                        "text": component["name"],
                        "on_release": lambda x=component["name"]: set_text(caller, x),
                    }
                )

        # create list widget
        self.menu = MDDropdownMenu(
            caller=caller,
            items=dropdown_items,
            position="bottom",
            width_mult=4,
        )
        # append widget to the UI
        self.menu.bind()
        self.menu.open()

    def show_connection_deletion_dialog(self):
        """
        This function shows the warndiealog that asks the user if he really wants to delete the selcted connection.
        If the user confirms the delete_connection method is called. Otherwise nothing will happen
        """

        # prepar helper function to suppress initial callback
        def delete(instance):
            self.delete_connection(connection_key)

        # get key of the scenario to be deleted
        connection_key = self.selected_asset["key"]

        # create dialog
        btn_false = MDFlatButton(text="CANCEL")
        btn_true = MDRaisedButton(text="DELETE CONNECTION")
        self.dialog = MDDialog(
            title="Delete Connection",
            text=f"Do you really want to delete the Connection '{self.selected_asset['name']}'?",
            buttons=[btn_false, btn_true],
        )
        btn_false.bind(on_release=self.dialog.dismiss)
        btn_true.bind(on_release=delete)
        self.dialog.open()

    def show_flowtype_config_dialog(self):
        """
        This function oipens the dialog for configuring flowtypes.
        """

        self.dialog = MDDialog(
            title="Flowtype Definition",
            type="custom",
            content_cls=dialog_flowtype_definition(),
            auto_dismiss=False
        )

        self.dialog.size_hint = (None, None)
        self.dialog.width = dp(850)
        self.dialog.height = dp(700)

        self.select_flowtype(self.blueprint.flowtypes["unknown"])
        self.dialog.open()
        self.dialog.background_click = False

    def show_flowtype_selection_dropdown(self, caller):
        """
        This function creates a dropdown menu giving the user the option to select one of the existing flowtypes.
        The name of the selected flowtype is being set as text to the component that this function is being called from.
        """

        def set_text(caller, text):
            # this function returns the user selection to the object that the dialog has been called from
            caller.text = text
            self.menu.dismiss()

        # initialize empty list
        dropdown_items = []
        # iterate over all flowtypes in the blueprint
        for flowtype in self.blueprint.flowtypes.values():
            # append a dropdown item to the list
            dropdown_items.append(
                {
                    "viewclass": "IconListItem",
                    "icon": "circle",
                    "icon_color": flowtype.color.rgba,
                    "text": flowtype.name,
                    "on_release": lambda x=flowtype.name: set_text(caller, x),
                }
            )

        # create list widget
        self.menu = MDDropdownMenu(
            caller=caller,
            items=dropdown_items,
            position="center",
            width_mult=4,
        )

        # append widget to the UI
        self.menu.bind()
        self.menu.open()

    def show_icon_selection_dropdown(self, caller):
        """
        This function creates a dropdown menu giving the user the option to select one of the predefined icons.
        The filepath of the selected icon is being set as text to the component that this function is being called from.
        """

        def set_image(caller, path):
            # return the selected icon to the iconlabel in the config-tab
            caller.source = path
            self.selected_asset["GUI"]["icon"] = caller.source
            self.initialize_visualization()

            # close icon selection dialog
            self.menu.dismiss()

        # determine which selection of icons is displayed
        if self.selected_asset["type"] == "source":
            icon_list = self.source_icons
        elif self.selected_asset["type"] == "sink":
            icon_list = self.sink_icons
        else:
            icon_list = self.component_icons

        # initialize empty list
        dropdown_items = []

        # iterate over all icons in the list
        for icon_name, icon_source in icon_list.items():
            dropdown_items.append(
                {
                    "viewclass": "ImageDropDownItem",
                    "source": icon_source,
                    "text": icon_name,
                    "on_release": lambda x=icon_source: set_image(caller, x),
                }
            )
        # create list widget
        self.menu = MDDropdownMenu(
            caller=caller,
            items=dropdown_items,
            position="center",
            width_mult=4,
        )
        # append widget to the UI
        self.menu.bind()
        self.menu.open()

    def show_image_selection_dialog(self):
        """
        This function displays a dialog with all predefined scenario artworks for the user
        to select one for the current scenario
        """
        # create dialog

        self.dialog = MDDialog(
            title="Select scenario image",
            type="custom",
            content_cls=dialog_image_selection(),
        )

        for image in self.scenario_images.keys():
            image_tile = Image(
                source=self.scenario_images[image],
                on_touch_down=lambda instance, touch: self.set_scenario_image(
                    instance, touch
                ),
            )
            image_tile.bind()
            self.dialog.content_cls.ids.image_grid.add_widget(image_tile)
        self.dialog.open()

    def show_info_popup(self, text):
        """
        This function creates an overlay popup that displays the user a handed over text message.
        The user can only confirm by clicking OK
        """
        # create popup
        btn_ok = MDRaisedButton(text="OK")
        self.popup = MDDialog(title="Warning", buttons=[btn_ok], text=text)
        btn_ok.bind(on_release=self.popup.dismiss)
        self.popup.open()

    def show_parameter_config_dialog(self, caller):
        parameter_config_dialog(self, caller)

    def show_scaling_selection_dialog(self, *args):
        def set_text(text):
            # this function returns the user selection to the object that the dialog has been called from
            self.root.ids.textfield_timeseries_scaling.text = text

            self.menu.dismiss()

        # initialize empty list
        dropdown_items = []

        # append a dropdown item to the list
        dropdown_items.append(
            {
                "viewclass": "OneLineListItem",
                "text": "with a peak value of",
                "on_release": lambda x="with a peak value of": set_text(x),
            }
        )
        dropdown_items.append(
            {
                "viewclass": "OneLineListItem",
                "text": "with an average value of",
                "on_release": lambda x="with an average value of": set_text(x),
            }
        )
        dropdown_items.append(
            {
                "viewclass": "OneLineListItem",
                "text": "with a total value of",
                "on_release": lambda x="with a total value of": set_text(x),
            }
        )

        # create list widget
        self.menu = MDDropdownMenu(
            caller=self.root.ids.textfield_timeseries_scaling,
            items=dropdown_items,
            position="center",
            width_mult=4,
        )
        # append widget to the UI
        self.menu.bind()
        self.menu.open()

    def show_scenario_configuration_dialog(self):
        def edit_scenario(*args):
            # write given information into the GUI and into the scenario
            self.selected_scenario[
                "name"
            ] = self.dialog.content_cls.ids.textfield_new_scenario_name.text
            self.root.ids.label_scenario_title.text = self.selected_scenario["name"]
            self.selected_scenario[
                "description"
            ] = self.dialog.content_cls.ids.textfield_new_scenario_description.text
            self.root.ids.label_scenario_description.text = self.selected_scenario[
                "description"
            ]
            # close dialog
            self.dialog.dismiss()

        # create dialog
        btn_false = MDFlatButton(text="CANCEL")
        btn_true = MDRaisedButton(text="SAVE")
        self.dialog = MDDialog(
            title="Edit Scenario",
            buttons=[btn_false, btn_true],
            type="custom",
            content_cls=dialog_update_scenario(),
        )

        # write current name and description into the dialog
        self.dialog.content_cls.ids.textfield_new_scenario_name.text = (
            self.selected_scenario["name"]
        )
        self.dialog.content_cls.ids.textfield_new_scenario_description.text = (
            self.selected_scenario["description"]
        )

        # bind functions and open dialog
        btn_false.bind(on_release=self.dialog.dismiss)
        btn_true.bind(on_release=edit_scenario)
        self.dialog.open()

    def show_scenario_creation_dialog(self):
        # create dialog
        btn_false = MDFlatButton(text="CANCEL")
        btn_true = MDRaisedButton(text="CREATE NEW SCENARIO")
        self.dialog = MDDialog(
            title="New Scenario",
            buttons=[btn_false, btn_true],
            type="custom",
            content_cls=dialog_new_scenario(),
        )
        btn_false.bind(on_release=self.dialog.dismiss)
        btn_true.bind(on_release=self.new_scenario)
        self.dialog.open()

    def show_scenario_seletion_dialog(self, instance):
        """
        This function creates a dialog that asks the user to confirm the deletion of a scenario

        """

        # prepare helper function to suppress initial callback
        def delete(instance):
            self.delete_scenario(scenario_key)

        # get key of the scenario to be deleted
        scenario_key = instance.parent.parent.scenario_key

        # create dialog
        btn_false = MDFlatButton(text="CANCEL")
        btn_true = MDRaisedButton(text="DELETE SCENARIO")
        self.dialog = MDDialog(
            title="Delete Scenario",
            text=f"Do you really want to delete the scenario '{self.scenarios[scenario_key]['name']}'?",
            buttons=[btn_false, btn_true],
        )
        btn_false.bind(on_release=self.dialog.dismiss)
        btn_true.bind(on_release=delete)
        self.dialog.open()

    def show_timeseries_selection_dialog(self, *args):
        """
        This function opens a dialog, in which the user can select one of the timeseries that are currently opened within self.timeseries.
        The style of the window is defined as <dialog_timeseries_selection> within the kivy file.
        It contains a button to call the excel-inport routine for timeseries as well.
        """
        self.dialog = MDDialog(
            title="Select Timeseries",
            type="custom",
            content_cls=dialog_timeseries_selection(),
        )

        # iterate over all imported timeseries
        for key in self.timeseries:
            # apply filter given by search textfield
            if (
                self.dialog.content_cls.ids.search_field_timeseries.text == ""
                or self.dialog.content_cls.ids.search_field_timeseries.text.upper()
                in key.upper()
                or self.dialog.content_cls.ids.search_field_timeseries.text.upper()
                in self.timeseries[key][0].upper()
            ):

                # create list item
                item = TwoLineListItem(
                    text=key,
                    secondary_text=self.timeseries[key][0],
                    on_touch_down=self.select_timeseries_list_item,
                )

                # append item to list
                self.dialog.content_cls.ids.list_timeseries.add_widget(item)
        self.dialog.open()

    def show_unit_selection_dropdown(self, caller):
        """
        This function creates a dropdown menu giving the user the option to select one of the existing units.
        The name of the selected unit is being set as text to the flow that this function is being called from.
        """

        def set_text(caller, text):
            # this function returns the user selection to the object that the dialog has been called from
            caller.text = text
            self.menu.dismiss()

        # initialize empty list
        dropdown_items = []
        # iterate over all components in the blueprint
        for unit in self.blueprint.units.values():
            # append a dropdown item to the list
            dropdown_items.append(
                {
                    "viewclass": "OneLineListItem",
                    "icon": "cog",
                    "text": unit.name,
                    "on_release": lambda x=unit.name: set_text(caller, x),
                }
            )

        # create list widget
        self.menu = MDDropdownMenu(
            caller=caller,
            items=dropdown_items,
            position="center",
            width_mult=4,
        )
        # append widget to the UI
        self.menu.bind()
        self.menu.open()

    def update_scenario_parameter_list(self):
        """
        This function creates a list of all parameters that the user has to specify during scenario setup
        """
        # clear existing list
        self.root.ids.list_scenario_parameters.clear_widgets()
        self.parameters_missing = 0
        self.parameters_ok = 0

        def append_item(frame, component_name, parameter_name):
            """
            This subfunction creates a list entry representing a single component parameter that has to be specified
            for the simulation. The Item is being attached to the list_scenario_parameters-object
            """

            # create list entry with basic parameter description
            parameter_description = TwoLineAvatarListItem(
                text=component_name,
                secondary_text=parameter_name,
                on_release=self.select_parameter_list_item,
            )

            # create an image object with the correct image and append it to the list item
            image = ImageLeftWidgetWithoutTouch(source=frame)
            parameter_description.add_widget(image)

            # create an label for the list entry that shows the number of specified varietions for the parameter
            label_variation_count = OneLineListItem(text="No variations specified")

            # create a button to enable editing the components variations
            button = RightButton(text="EDIT")

            # create the final list item with all prepared components and attach it to the list
            item = BoxLayout(orientation="horizontal", size_hint_y=None, height="70dp")
            item.add_widget(parameter_description)
            item.add_widget(label_variation_count)
            item.add_widget(button)
            self.root.ids.list_scenario_parameters.add_widget(item)

        for component in self.blueprint.components.values():
            if component["type"] == "source":
                if component["scenario_availability"]:
                    append_item(
                        component["GUI"]["icon"], component["name"], "availability"
                    )
                if component["scenario_cost"]:
                    append_item(component["GUI"]["icon"], component["name"], "cost")
                if component["scenario_determined"]:
                    append_item(
                        component["GUI"]["icon"], component["name"], "determined_power"
                    )
                if component["scenario_emissions"]:
                    append_item(
                        component["GUI"]["icon"], component["name"], "emissions"
                    )
            elif component["type"] == "sink":
                if component["scenario_revenue"]:
                    append_item(component["GUI"]["icon"], component["name"], "revenue")
                if component["scenario_cost"]:
                    append_item(component["GUI"]["icon"], component["name"], "cost")
                if component["scenario_determined"]:
                    append_item(component["GUI"]["icon"], component["name"], "demand")
                if component["scenario_co2_emission_per_unit"]:
                    append_item(
                        component["GUI"]["icon"], component["name"], "Emissions Created"
                    )
                if component["scenario_co2_refund_per_unit"]:
                    append_item(
                        component["GUI"]["icon"], component["name"], "Emissions Avoided"
                    )

        # update progress information on GUI
        self.root.ids.label_scenario_simulation_parameters_specified.secondary_text = (
            f"{self.parameters_ok} / {self.parameters_ok + self.parameters_missing}"
        )

        if self.parameters_missing == 0:
            self.root.ids.button_run_simulation.disabled = False
        else:
            self.root.ids.button_run_simulation.disabled = True

    def update_config_tab(self):
        """
        This function is called, when the user clicks on a component. It openes the corresponding configuration-screen in the card on the right and fills in all the values from the selected asset into the textfields and labels.
        """

        if self.selected_asset is None:
            # if no asset is selected: show the standard screen
            self.root.ids.asset_config_screens.current = "welcome_screen"
        elif self.selected_asset["type"] == "source":
            # switch to the correct screen of the component tab
            self.root.ids.asset_config_screens.current = "source_config"

            # get data from blueprint and add it to the screen
            self.root.ids.label_source_name.text = self.selected_asset["name"]
            self.root.ids.textfield_source_name.text = self.selected_asset["name"]
            self.root.ids.textfield_source_description.text = self.selected_asset[
                "description"
            ]
            self.root.ids.textfield_source_flowtype.text = self.selected_asset[
                "flowtype"
            ].name
            self.root.ids.image_source_configuration.source = self.selected_asset[
                "GUI"
            ]["icon"]

            for parameter in [
                "capacity_charge",
                "cost",
                "power_max",
                "power_min",
                "availability",
                "co2_emission_per_unit",
                "determined_power",
            ]:
                textfield = getattr(self.root.ids, f"textfield_source_{parameter}")
                if parameter in self.parameters[self.selected_asset["key"]].keys():

                    textfield.text = str(
                        self.parameters[self.selected_asset["key"]][parameter]
                    )
                else:
                    textfield.text = ""

            # Adapt hint texts to the specified flowtype-unit
            self.root.ids.textfield_source_power_max.hint_text = f"Maximum Output Flowrate [{self.selected_asset['flowtype'].unit.get_unit_flowrate()}]"
            self.root.ids.textfield_source_power_min.hint_text = f"Minimum Output Flowrate [{self.selected_asset['flowtype'].unit.get_unit_flowrate()}]"
            self.root.ids.textfield_source_determined_power.hint_text = f"Fixed Output Level [{self.selected_asset['flowtype'].unit.get_unit_flowrate()}]"
            self.root.ids.textfield_source_cost.hint_text = f"Cost per Unit [€/{self.selected_asset['flowtype'].unit.get_unit_flow()}]"
            self.root.ids.textfield_source_capacity_charge.hint_text = f"Capacity Charge [€/{self.selected_asset['flowtype'].unit.get_unit_flowrate()}_peak]"
            self.root.ids.textfield_source_co2_emission_per_unit.hint_text = f"CO2 Emissions per Unit [kgCO2/{self.selected_asset['flowtype'].unit.get_unit_flow()}]"

        elif self.selected_asset["type"] == "pool":
            # show the pool configuration screen
            self.root.ids.asset_config_screens.current = "pool_config"
            self.root.ids.label_pool_name.text = self.selected_asset["name"].upper()
            self.root.ids.textfield_pool_flowtype.text = self.selected_asset[
                "flowtype"
            ].name
            self.root.ids.textfield_pool_name.text = self.selected_asset["name"]
            self.root.ids.textfield_pool_description.text = self.selected_asset[
                "description"
            ]

        elif self.selected_asset["type"] == "converter":
            # show the converter configuration screen
            self.root.ids.asset_config_screens.current = "converter_config"

            # get data from blueprint and add it to the screen
            self.root.ids.label_converter_name.text = self.selected_asset[
                "name"
            ].upper()
            self.root.ids.textfield_converter_name.text = self.selected_asset["name"]
            self.root.ids.textfield_converter_description.text = self.selected_asset[
                "description"
            ]
            self.root.ids.image_converter_configuration.source = self.selected_asset[
                "GUI"
            ]["icon"]

            # go through all numerical parameters
            for parameter in [
                "power_max",
                "power_min",
                "availability",
                "max_pos_ramp_power",
                "max_neg_ramp_power",
                "eta_max",
                "power_nominal",
                "delta_eta_high",
                "delta_eta_low",
            ]:
                # get the pointer to the corresponding textfield
                textfield = getattr(self.root.ids, f"textfield_converter_{parameter}")
                # check if there is a value for the parameter in the parameters dict
                if parameter in self.parameters[self.selected_asset["key"]].keys():
                    # if yes: write value into the textfield
                    textfield.text = str(
                        self.parameters[self.selected_asset["key"]][parameter]
                    )
                else:
                    textfield.text = ""

            self.validate_textfield_input(self.root.ids.textfield_converter_power_min)
            self.validate_textfield_input(self.root.ids.textfield_converter_power_max)
            self.validate_textfield_input(
                self.root.ids.textfield_converter_max_pos_ramp_power
            )
            self.validate_textfield_input(
                self.root.ids.textfield_converter_max_neg_ramp_power
            )
            self.validate_textfield_input(self.root.ids.textfield_converter_eta_max)
            self.validate_textfield_input(
                self.root.ids.textfield_converter_power_nominal
            )
            self.validate_textfield_input(
                self.root.ids.textfield_converter_availability
            )

        elif self.selected_asset["type"] == "sink":
            # switch to the correct screen of the component tab
            self.root.ids.asset_config_screens.current = "sink_config"

            # get data from blueprint and add it to the screen
            self.root.ids.label_sink_name.text = self.selected_asset["name"].upper()
            self.root.ids.textfield_sink_name.text = self.selected_asset["name"]
            self.root.ids.textfield_sink_description.text = self.selected_asset[
                "description"
            ]
            self.root.ids.textfield_sink_flowtype.text = self.selected_asset[
                "flowtype"
            ].name
            self.root.ids.image_sink_configuration.source = self.selected_asset["GUI"][
                "icon"
            ]

            for parameter in [
                "cost",
                "revenue",
                "power_max",
                "power_min",
                "demand",
                "co2_refund_per_unit",
                "co2_emission_per_unit",
            ]:
                textfield = getattr(self.root.ids, f"textfield_sink_{parameter}")

                if parameter in self.parameters[self.selected_asset["key"]].keys():
                    textfield.text = str(
                        self.parameters[self.selected_asset["key"]][parameter]
                    )
                else:
                    textfield.text = ""

            # Adapt hint texts to the specified flowtype-unit
            self.root.ids.textfield_sink_cost.hint_text = f"Cost of Utilization [€/{self.selected_asset['flowtype'].unit.get_unit_flow()}]"
            self.root.ids.textfield_sink_revenue.hint_text = f"Revenue of Utilization [€/{self.selected_asset['flowtype'].unit.get_unit_flow()}]"
            self.root.ids.textfield_sink_co2_emission_per_unit.hint_text = f"CO2 Emissions [kgCO2/{self.selected_asset['flowtype'].unit.get_unit_flow()}]"
            self.root.ids.textfield_sink_co2_refund_per_unit.hint_text = f"CO2 Compensation [kgCO2/{self.selected_asset['flowtype'].unit.get_unit_flow()}]"
            self.root.ids.textfield_sink_power_max.hint_text = f"Maximum Input Power [{self.selected_asset['flowtype'].unit.get_unit_flowrate()}]"
            self.root.ids.textfield_sink_power_min.hint_text = f"Minimum Input Power [{self.selected_asset['flowtype'].unit.get_unit_flowrate()}]"
            self.root.ids.textfield_sink_demand.hint_text = f"Fixed Demand [{self.selected_asset['flowtype'].unit.get_unit_flowrate()}]"

        elif self.selected_asset["type"] == "storage":
            # switch to the correct screen of the component tab
            self.root.ids.asset_config_screens.current = "storage_config"

            # get data from blueprint and add it to the screen
            self.root.ids.label_storage_name.text = self.selected_asset["name"].upper()
            self.root.ids.textfield_storage_name.text = self.selected_asset["name"]
            self.root.ids.textfield_storage_description.text = self.selected_asset[
                "description"
            ]
            self.root.ids.textfield_storage_flowtype.text = self.selected_asset[
                "flowtype"
            ].name
            self.root.ids.image_storage_configuration.source = self.selected_asset[
                "GUI"
            ]["icon"]

            for parameter in [
                "power_max_charge",
                "power_max_discharge",
                "capacity",
                "soc_start",
                "efficiency",
                "leakage_time",
                "leakage_soc",
            ]:
                textfield = getattr(self.root.ids, f"textfield_storage_{parameter}")

                if parameter in self.parameters[self.selected_asset["key"]].keys():
                    textfield.text = str(
                        self.parameters[self.selected_asset["key"]][parameter]
                    )
                else:
                    textfield.text = ""

            # Adapt hint texts to the specified flowtype-unit
            self.root.ids.textfield_storage_capacity.hint_text = f"Storage Capacity [{self.selected_asset['flowtype'].unit.get_unit_flow()}]"
            self.root.ids.textfield_storage_power_max_charge.hint_text = f"Maximum Charging Power [{self.selected_asset['flowtype'].unit.get_unit_flowrate()}]"
            self.root.ids.textfield_storage_power_max_discharge.hint_text = f"Maximum Discharging Power [{self.selected_asset['flowtype'].unit.get_unit_flowrate()}]"
            self.root.ids.textfield_storage_leakage_time.hint_text = f"Fixed Absolute Leakage [{self.selected_asset['flowtype'].unit.get_unit_flow()}/h]"

        elif self.selected_asset["type"] == "thermalsystem":
            # show the thermal system configuration screeen in the box on the bottom of the screen
            self.root.ids.asset_config_screens.current = "thermalsystem_config"
            # read values from the blueprint and initialize the input fields
            self.root.ids.label_thermalsystem_name.text = self.selected_asset[
                "name"
            ].upper()
            self.root.ids.textfield_thermalsystem_name.text = self.selected_asset[
                "name"
            ]
            self.root.ids.textfield_thermalsystem_description.text = (
                self.selected_asset["description"]
            )
            self.root.ids.textfield_thermalsystem_temperature_start.text = (
                self.selected_asset["Start temperature"]
            )
            self.validate_textfield_input(
                self.root.ids.textfield_thermalsystem_temperature_start
            )
            self.validate_textfield_input(
                self.root.ids.textfield_thermalsystem_temperature_ambient
            )
            self.validate_textfield_input(
                self.root.ids.textfield_thermalsystem_temperature_max
            )
            self.validate_textfield_input(
                self.root.ids.textfield_thermalsystem_temperature_min
            )
            self.validate_textfield_input(self.root.ids.textfield_thermalsystem_R)
            self.validate_textfield_input(self.root.ids.textfield_thermalsystem_C)
            # self.on_checkbox_active(self.root.ids.switch_thermalsystem_temperature_max, self.root.ids.textfield_thermalsystem_temperature_max, self.root.ids.switch_thermalsystem_temperature_max.active)
            # self.on_checkbox_active(self.root.ids.switch_thermalsystem_temperature_max, self.root.ids.textfield_thermalsystem_temperature_max)
            self.root.ids.textfield_thermalsystem_temperature_ambient.text = (
                self.selected_asset["ambient temperature"]
            )
            self.root.ids.textfield_thermalsystem_temperature_ambient.text = (
                self.selected_asset["ambient temperature"]
            )
            self.root.ids.textfield_thermalsystem_temperature_max.text = (
                self.selected_asset["maximum temperature"]
            )
            self.root.ids.textfield_thermalsystem_temperature_min.text = (
                self.selected_asset["minimum temperature"]
            )
            self.root.ids.textfield_thermalsystem_sustainable.text = (
                self.selected_asset["sustainable"]
            )
            self.root.ids.textfield_thermalsystem_R.text = self.selected_asset["R"]
            self.root.ids.textfield_thermalsystem_C.text = self.selected_asset["C"]
            self.root.ids.switch_thermalsystem_temperature_ambient.active = (
                self.selected_asset["scenario_temperature_ambient"]
            )
            self.root.ids.switch_thermalsystem_temperature_max.active = (
                self.selected_asset["scenario_temperature_max"]
            )
            self.root.ids.switch_thermalsystem_temperature_min.active = (
                self.selected_asset["scenario_temperature_min"]
            )

            # display the correct icon
            self.root.ids.image_thermalsystem_configuration.source = (
                self.selected_asset["GUI"]["icon"]
            )

        elif self.selected_asset["type"] == "schedule":
            # show the schedule configuration screeen in the box on the bottom of the screen
            self.root.ids.asset_config_screens.current = "schedule_config"
            # read values from the blueprint and initialize the input fields
            self.root.ids.label_schedule_name.text = self.selected_asset["name"].upper()
            self.root.ids.textfield_schedule_name.text = self.selected_asset["name"]
            self.root.ids.textfield_schedule_description.text = self.selected_asset[
                "description"
            ]
            self.root.ids.textfield_schedule_power_max.text = self.selected_asset[
                "Maximum power flow"
            ]
            # display the correct icon
            self.root.ids.image_schedule_configuration.source = self.selected_asset[
                "icon"
            ]

        elif self.selected_asset["type"] == "triggerdemand":
            pass

        elif self.selected_asset["type"] == "deadtime":
            # switch to the correct screen of the component tab
            self.root.ids.asset_config_screens.current = "deadtime_config"

            # read values from the blueprint and initialize the input fields
            self.root.ids.label_deadtime_name.text = self.selected_asset["name"].upper()
            self.root.ids.textfield_deadtime_name.text = self.selected_asset["name"]
            self.root.ids.textfield_deadtime_description.text = self.selected_asset[
                "description"
            ]
            self.root.ids.textfield_deadtime_flowtype.text = self.selected_asset[
                "flowtype"
            ].name

            # display the correct icon
            self.root.ids.image_deadtime_configuration.source = self.selected_asset[
                "GUI"
            ]["icon"]

            if "delay" in self.parameters[self.selected_asset["key"]].keys():
                self.root.ids.textfield_deadtime_delay.text = str(
                    self.parameters[self.selected_asset["key"]]["delay"]
                )
            else:
                self.root.ids.textfield_deadtime_delay.text = ""

        # since the asset just got updated there are no unsaved changes anymore
        self.unsaved_changes_on_asset = False

    def update_connection_names(self):
        for connection in self.blueprint.connections.values():
            connection[
                "name"
            ] = f'{self.blueprint.components[connection["from"]]["name"]} -> {self.blueprint.components[connection["to"]]["name"]} '

    def update_flowtype_color(
        self, instance_color_picker: MDColorPicker, type_color: str, selected_color
    ):
        """
        This function updates the color of the component_color_button in the flow-tab
        by giving the user a colorpicker-interface
        """
        self.dialog.content_cls.ids.icon_flowtype_color.icon_color = selected_color[
            :-1
        ] + [1]
        self.popup.dismiss()
        self.dialog.content_cls.ids.button_flowtype_save.disabled = False

    def update_flowtype_list(self):
        # predefine icons for list entries
        icons = {"energy": "lightning-bolt", "mass": "weight", "other": "help"}

        # clear existing list
        self.root.ids.list_flowtypes.clear_widgets()

        # iterate over all units
        for flowtype in self.blueprint.flowtypes.values():
            # create list item
            item = TwoLineAvatarIconListItem(
                IconLeftWidgetWithoutTouch(
                    icon="circle",
                    theme_icon_color="Custom",
                    icon_color=flowtype.color.rgba,
                ),
                text=flowtype.name,
                secondary_text=flowtype.unit.quantity_type,
                on_touch_down=self.select_flowtype_list_item,
            )
            if self.flowtype_used(flowtype.key):
                lock_icon = IconRightWidget(icon="lock")
                item.add_widget(lock_icon)

            # append item to list
            self.root.ids.list_flowtypes.add_widget(item)

        item = OneLineIconListItem(
            IconLeftWidget(icon="plus"),
            text="Add Flowtype",
            on_touch_down=self.select_flowtype_list_item,
        )
        # append item to list
        self.root.ids.list_flowtypes.add_widget(item)

    def update_scenario_config_screen(self, instance):
        """
        This function is called everytime when the user clicks on one of the scenario cards.
        It sets the currently selected scenario to the one that the user clicked on and shows up the scenario config screen
        """

        # if not instance.collide_point(*touch.pos):
        #     # abort if not
        #     return

        # change selected scenario to the one that the function call came from
        self.selected_scenario = self.scenarios[instance.scenario_key]

        # switch to the scenario config screen
        self.root.ids.scenario_screens.current = "parameter_configuration_screen"

        # update the list of required parameters:
        self.update_scenario_parameter_list()

        # write the information on the current scenario into the infobox on the scenario screen
        self.root.ids.image_scenario.source = self.selected_scenario["image"]
        self.root.ids.label_scenario_title.text = self.selected_scenario["name"]
        self.root.ids.label_scenario_description.text = self.selected_scenario[
            "description"
        ]
        # self.root.ids.label_scenario_location.secondary_text = self.selected_scenario["location_name"]
        # self.root.ids.label_scenario_year.secondary_text = f"{self.selected_scenario['year']}"
        # self.root.ids.label_scenario_timestep_start.secondary_text = f"{self.selected_scenario['timestep_start']}"
        self.root.ids.label_scenario_timestep_width.secondary_text = (
            f"{self.selected_scenario['time_factor']} Hour(s)"
        )
        self.root.ids.label_scenario_timesteps.secondary_text = (
            f"{self.selected_scenario['timesteps']}"
        )

    def update_scenario_selection_screen(self):
        self.root.ids.scenario_screens.current = "scenario_selection_screen"

    def update_timeseries_list(self):
        # clear existing list
        self.dialog.content_cls.ids.list_timeseries.clear_widgets()

        # iterate over all imported timeseries
        for key in self.timeseries:
            # apply filter given by search textfield
            if (
                self.dialog.content_cls.ids.search_field_timeseries.text == ""
                or self.dialog.content_cls.ids.search_field_timeseries.text.upper()
                in key.upper()
                or self.dialog.content_cls.ids.search_field_timeseries.text.upper()
                in self.timeseries[key][0].upper()
            ):

                # create list item
                item = TwoLineListItem(
                    text=key,
                    secondary_text=self.timeseries[key][0],
                    on_touch_down=self.select_timeseries_list_item,
                )

                # append item to list
                self.dialog.content_cls.ids.list_timeseries.add_widget(item)

    def update_timeseries_preview(self, value_type):
        """
        This function creates a graph of a timeseries and hands it over to the preview canvas
        """
        # initialize the timeseries plot if not done yet
        if not hasattr(self, "timeseries_plot"):
            self.timeseries_plot = LinePlot(color=self.main_color_rgba, line_width=2)
            self.root.ids.timeseries_preview.add_plot(self.timeseries_plot)

        # set points depending on given user information
        if value_type == "Static Value":

            # if user wants a static value: just read out the value from gui
            value = float(self.root.ids.textfield_static_value.text)
            max_value = value

            # update plot points for the graph
            self.selected_timeseries = (
                np.ones(self.selected_scenario["timesteps"]) * value
            )
            self.timeseries_plot.points = [
                (x, y) for x, y in enumerate(self.selected_timeseries)
            ]
            self.root.ids.timeseries_preview.ylabel = (
                self.root.ids.textfield_static_value_unit.text
            )

            # update Y-axis_label:
            self.root.ids.timeseries_preview.ylabel = (
                self.root.ids.textfield_static_value_unit.text
            )

        elif value_type == "Custom Timeseries":
            # if user wants a timeseries: take the currently selected timeseries and scale it as demanded
            if (
                self.root.ids.textfield_timeseries_scaling.text
                == "with a peak value of"
            ):
                # scale timeseries to given peak value
                self.selected_timeseries = (
                    self.selected_timeseries
                    / float(np.amax(self.selected_timeseries))
                    * float(self.root.ids.textfield_custom_timeseries.text)
                )

            elif (
                self.root.ids.textfield_timeseries_scaling.text
                == "with an average value of"
            ):
                # scale timeseries to given average value
                self.selected_timeseries = (
                    self.selected_timeseries
                    / np.mean(self.selected_timeseries)
                    * float(self.root.ids.textfield_custom_timeseries.text)
                )

            else:
                # scale timeseries to given integral value
                self.selected_timeseries = (
                    self.selected_timeseries
                    / np.sum(self.selected_timeseries)
                    * float(self.root.ids.textfield_custom_timeseries.text)
                )

            # update Y-axis_label:
            self.root.ids.timeseries_preview.ylabel = (
                self.root.ids.textfield_custom_timeseries_unit.text
            )

            # update plot points for the graph
            self.timeseries_plot.points = [
                (x, y) for x, y in enumerate(self.selected_timeseries)
            ]
            max_value = float(np.amax(self.selected_timeseries))
        # update graph properties:
        self.root.ids.timeseries_preview.xlabel = "Hours"

        # set scaling of X-Axes
        self.root.ids.timeseries_preview.xmax = self.selected_scenario["timesteps"]
        self.root.ids.timeseries_preview.xmin = 1
        self.root.ids.timeseries_preview.x_ticks_major = 24

        # set scaling of Y-Axes
        self.root.ids.timeseries_preview.ymin = 0
        if max_value == 0:
            self.root.ids.timeseries_preview.ymax = 1
            self.root.ids.timeseries_preview.y_ticks_major = 0.2
        else:
            # determine dimension of value
            x = max_value
            i = 0
            while x > 1:
                x = x / 10
                i += 1

            # set y scale of graph
            self.root.ids.timeseries_preview.ymax = 10**i * round(x + 0.1, 1)

            self.root.ids.timeseries_preview.y_ticks_major = 10**i / 5

    def update_visualization(self, *args, **kwargs):
        """
        This function updates the position of connections and labels of the factory layout visualization.
        It is being called on startup once and everytime a component gets moved by the user
        """

        # Specify a scaling factor depending on the size of the canvas and the number of components to be displayed
        # scaling factor = width_of_canvas / sqrt(number_of_components+1) / adjustment_factor
        scaling_factor = (
            self.session_data["display_scaling_factor"]
            * self.root.ids.canvas_layout.size[0]
            / 1000
            / (len(self.blueprint.components) + 1) ** (0.25)
        )
        # TODO: the adjustment factor and the exponent need to be tweaked in a way that it results in well scaled diagrams when the number of components can be varied

        # specify size of the components depending on the size of the canvas
        line_width = 7 * scaling_factor  # line width in px
        component_height = 100 * scaling_factor  # height in px

        # specify display widths of components in px depending on their type
        component_width = {
            "source": component_height,
            "sink": component_height,
            "pool": component_height,
            "storage": component_height * 1.5,
            "converter": component_height * 1.5,
            "deadtime": component_height * 1.5,
            "thermalsystem": component_height * 1.5,
            "triggerdemand": component_height * 1.5,
            "schedule": component_height * 1.5,
        }

        # specify canvas dimensions
        self.root.ids.canvas_layout.pos = self.root.ids.layout_area.pos
        self.root.ids.canvas_layout.size = self.root.ids.layout_area.size

        # store pointer to canvas to make following code better readable

        # create dataset with the incoming and outgoing connections per component, sorted by the direction
        # initialize a dict to store the information per direction
        connection_data = defaultdict(lambda: None)
        for component in self.blueprint.components:
            connection_data[component] = {
                "top": [],
                "bottom": [],
                "left": [],
                "right": [],
            }

        # iterate over all connections to determine the involved components and the directions
        connection_list = {}
        for connection in self.blueprint.connections.values():

            # initialize connection list for later (just to safe a loop)
            connection_list[connection["key"]] = {}

            # calculate distance between roots of source and sink on the canvas
            diff_x = (
                self.root.ids[f'frame_{connection["from"]}'].pos[0]
                - self.root.ids[f'frame_{connection["to"]}'].pos[0]
            )
            diff_y = (
                self.root.ids[f'frame_{connection["from"]}'].pos[1]
                - self.root.ids[f'frame_{connection["to"]}'].pos[1]
            )

            if abs(diff_x) > abs(diff_y) and diff_x < 0:
                # the source is left of the sink -> Connection is mostly horizontal
                # connection must go from right of the source to left of the sink
                # -> Store key of connection in the direction-lists of the components + coordinate difference
                connection_data[connection["from"]]["right"].append(
                    [diff_y / diff_x, connection["key"], "out"]
                )
                connection_data[connection["to"]]["left"].append(
                    [-diff_y / diff_x, connection["key"], "in"]
                )

            elif diff_y > 0:
                # the source is over the sink -> connection is mostly vertical and going downwards
                # connection must go from bottom of the source to the top of the sink
                # -> Store key of connection in the direction-lists of the components + coordinate difference
                connection_data[connection["from"]]["bottom"].append(
                    [-diff_x, connection["key"], "out"]
                )
                connection_data[connection["to"]]["top"].append(
                    [diff_x, connection["key"], "in"]
                )

            elif diff_y <= 0:
                # the source is under the sink -> connection is mostly vertical and going upwards
                # connection must go from top of the source to the bottom of the sink
                # -> Store key of connection in the direction-lists of the components + coordinate difference
                connection_data[connection["from"]]["top"].append(
                    [-diff_x, connection["key"], "out"]
                )
                connection_data[connection["to"]]["bottom"].append(
                    [diff_x, connection["key"], "in"]
                )

        # calculate how many connections are going in and out at every side of the components and sort them by the
        # relative coordinate difference to their origins/destinations to avoid crossings

        for component in connection_data.values():
            for direction in component:
                component[direction].sort(key=lambda x: x[0])

                i = 0
                number_of_connections = len(component[direction])
                for connection_end in component[direction]:
                    # set the id of the current connection at the component
                    i += 1

                    # set the offset of the connections breaking points
                    connection_list[connection_end[1]].update(
                        {"offset": (number_of_connections - 1) / 2 + 1 - i}
                    )

                    # define the connection as horizontal or vertical
                    if direction == "left":
                        connection_list[connection_end[1]].update(
                            {"direction": "horizontal", "key": connection_end[1]}
                        )
                    elif direction == "bottom":
                        connection_list[connection_end[1]].update(
                            {"direction": "vertical", "key": connection_end[1]}
                        )

                    # get the component that the connection has to start/end from
                    if connection_end[2] == "in":
                        act_component = self.blueprint.components[
                            self.blueprint.connections[connection_end[1]]["to"]
                        ]
                    else:
                        act_component = self.blueprint.components[
                            self.blueprint.connections[connection_end[1]]["from"]
                        ]

                    # determine the point where the current end of the connection has to be located
                    if direction == "bottom":
                        point_x = (
                            self.root.ids[f'frame_{act_component["key"]}'].pos[0]
                            + component_width[act_component["type"]]
                            / (number_of_connections + 1)
                            * i
                        )
                        point_y = (
                            self.root.ids[f'frame_{act_component["key"]}'].pos[1]
                            + component_height / 2
                        )
                    elif direction == "top":
                        point_x = (
                            self.root.ids[f'frame_{act_component["key"]}'].pos[0]
                            + component_width[act_component["type"]]
                            / (number_of_connections + 1)
                            * i
                        )
                        point_y = (
                            self.root.ids[f'frame_{act_component["key"]}'].pos[1]
                            + component_height / 2
                        )
                    elif direction == "left":
                        point_x = (
                            self.root.ids[f'frame_{act_component["key"]}'].pos[0]
                            + component_width[act_component["type"]] / 2
                        )
                        point_y = (
                            self.root.ids[f'frame_{act_component["key"]}'].pos[1]
                            + component_height / (number_of_connections + 1) * i
                        )
                    elif direction == "right":
                        point_x = (
                            self.root.ids[f'frame_{act_component["key"]}'].pos[0]
                            + component_width[act_component["type"]] / 2
                        )
                        point_y = (
                            self.root.ids[f'frame_{act_component["key"]}'].pos[1]
                            + component_height / (number_of_connections + 1) * i
                        )

                    if connection_end[2] == "out":
                        connection_list[connection_end[1]].update(
                            {"start_x": point_x, "start_y": point_y}
                        )
                    else:
                        connection_list[connection_end[1]].update(
                            {"end_x": point_x, "end_y": point_y}
                        )

        # finally: go over the list of connections again and plot the lines!
        for connection in connection_list.values():
            # adjust the line width
            self.root.ids[f"line_{connection['key']}"].width = line_width

            # check, which type of connection has to be created:
            if connection["direction"] == "horizontal":
                self.root.ids[f"line_{connection['key']}"].points = (
                    connection["start_x"],
                    connection["start_y"],
                    connection["start_x"]
                    + (connection["end_x"] - connection["start_x"]) / 2
                    + connection["offset"] * line_width * 3,
                    connection["start_y"],
                    connection["start_x"]
                    + (connection["end_x"] - connection["start_x"]) / 2
                    + connection["offset"] * line_width * 3,
                    connection["end_y"],
                    connection["end_x"],
                    connection["end_y"],
                )

                # get the widths of sink and source component
                source_width = component_width[
                    self.blueprint.components[
                        self.blueprint.connections[connection["key"]]["from"]
                    ]["type"]
                ]
                sink_width = component_width[
                    self.blueprint.components[
                        self.blueprint.connections[connection["key"]]["to"]
                    ]["type"]
                ]

                # adjust the points of the two triangles to form nice arrows at the beginning and end of the connection
                self.root.ids[f"pointer_start_{connection['key']}"].points = (
                    connection["start_x"] + source_width / 2 + line_width,
                    connection["start_y"] - line_width * 0.8,
                    connection["start_x"] + source_width / 2 + line_width,
                    connection["start_y"] + line_width * 0.8,
                    connection["start_x"] + source_width / 2 + line_width * 2,
                    connection["start_y"],
                )
                self.root.ids[f"pointer_end_{connection['key']}"].points = (
                    connection["end_x"] - sink_width / 2 - line_width * 2,
                    connection["end_y"] + line_width * 0.8,
                    connection["end_x"] - sink_width / 2 - line_width * 2,
                    connection["end_y"] - line_width * 0.8,
                    connection["end_x"] - sink_width / 2 - line_width,
                    connection["end_y"],
                )
            else:
                self.root.ids[f"line_{connection['key']}"].points = (
                    connection["start_x"],
                    connection["start_y"],
                    connection["start_x"],
                    connection["start_y"]
                    + (connection["end_y"] - connection["start_y"]) / 2
                    + connection["offset"] * line_width * 3,
                    connection["end_x"],
                    connection["start_y"]
                    + (connection["end_y"] - connection["start_y"]) / 2
                    + connection["offset"] * line_width * 3,
                    connection["end_x"],
                    connection["end_y"],
                )

                if connection["start_y"] > connection["end_y"]:
                    # adjust the points of the two triangles to form nice arrows at the beginning and end of the connection
                    self.root.ids[f"pointer_start_{connection['key']}"].points = (
                        connection["start_x"] - line_width * 0.8,
                        connection["start_y"] - component_height / 2 - line_width,
                        connection["start_x"] + line_width * 0.8,
                        connection["start_y"] - component_height / 2 - line_width,
                        connection["start_x"],
                        connection["start_y"] - component_height / 2 - line_width * 2,
                    )
                    self.root.ids[f"pointer_end_{connection['key']}"].points = (
                        connection["end_x"] - line_width * 0.8,
                        connection["end_y"] + component_height / 2 + line_width * 2,
                        connection["end_x"] + line_width * 0.8,
                        connection["end_y"] + component_height / 2 + line_width * 2,
                        connection["end_x"],
                        connection["end_y"] + component_height / 2 + line_width,
                    )
                else:
                    # adjust the points of the two triangles to form nice arrows at the beginning and end of the connection
                    self.root.ids[f"pointer_start_{connection['key']}"].points = (
                        connection["start_x"] - line_width * 0.8,
                        connection["start_y"] + component_height / 2 + line_width,
                        connection["start_x"] + line_width * 0.8,
                        connection["start_y"] + component_height / 2 + line_width,
                        connection["start_x"],
                        connection["start_y"] + component_height / 2 + line_width * 2,
                    )
                    self.root.ids[f"pointer_end_{connection['key']}"].points = (
                        connection["end_x"] - line_width * 0.8,
                        connection["end_y"] - component_height / 2 - line_width * 2,
                        connection["end_x"] + line_width * 0.8,
                        connection["end_y"] - component_height / 2 - line_width * 2,
                        connection["end_x"],
                        connection["end_y"] - component_height / 2 - line_width,
                    )

        # iterate over all components
        for component in self.blueprint.components.values():
            # set the positions for the labels and icons
            self.root.ids[f"text_{component['key']}"].pos = (
                self.root.ids[f"frame_{component['key']}"].pos[0]
                - component_width[component["type"]] * 0.5,
                self.root.ids[f"frame_{component['key']}"].pos[1]
                - component_height * 0.45
                - 30,
            )

            # set the font size of labels
            self.root.ids[f"text_{component['key']}"].font_size = 18 * scaling_factor

            # set the size of the components
            self.root.ids[f"frame_{component['key']}"].size = (
                component_width[component["type"]],
                component_height,
            )
            self.root.ids[f"text_{component['key']}"].size = (
                component_width[component["type"]] * 2,
                100,
            )

            # pools need their circles adjusted
            if component["type"] == "pool":
                # adjust position of circles
                self.root.ids[f"outer_circle_{component['key']}"].pos = self.root.ids[
                    f"frame_{component['key']}"
                ].pos
                self.root.ids[f"inner_circle_{component['key']}"].pos = (
                    self.root.ids[f"frame_{component['key']}"].pos[0] + 2 * line_width,
                    self.root.ids[f"frame_{component['key']}"].pos[1] + 2 * line_width,
                )
                # adjust size of circles
                self.root.ids[f"outer_circle_{component['key']}"].size = (
                    component_height,
                    component_height,
                )
                self.root.ids[f"inner_circle_{component['key']}"].size = (
                    component_height - 4 * line_width,
                    component_height - 4 * line_width,
                )

        # highlight the selected component
        if (
            self.selected_asset == None
            or self.selected_asset == ""
            or self.selected_asset["type"] == "energy"
            or self.selected_asset["type"] == "material"
            or self.selected_asset["type"] == "connection"
        ):
            #  if the user selected a flow, a connection or no component at all: move the highlight image out of sight
            self.root.ids["highlight"].pos = [-1000, -1000]

        else:
            # choose the correct highlight asset:
            self.root.ids["highlight"].source = self.highlight_icons[
                self.selected_asset["type"]
            ]
            # adjust it in size
            self.root.ids["highlight"].size = [
                component_width[self.selected_asset["type"]] * 2,
                component_height * 2,
            ]
            # place it behind the selected component
            self.root.ids["highlight"].pos = [
                self.root.ids[f"frame_{self.selected_asset['key']}"].pos[0]
                - component_width[self.selected_asset["type"]] / 2,
                self.root.ids[f"frame_{self.selected_asset['key']}"].pos[1]
                - component_height / 2,
            ]

        # place "new connection" button
        if (
            self.selected_asset == None
            or self.selected_asset == ""
            or self.selected_asset["type"] == "energy"
            or self.selected_asset["type"] == "material"
            or self.selected_asset["type"] == "connection"
            or self.selected_asset["type"] == "sink"
            or len(self.blueprint.components) < 2
        ):
            self.root.ids["new_connection"].pos = [-1000, -1000]
        else:
            self.root.ids["new_connection"].pos = [
                self.root.ids[f"frame_{self.selected_asset['key']}"].pos[0]
                + component_width[self.selected_asset["type"]],
                self.root.ids[f"frame_{self.selected_asset['key']}"].pos[1]
                + component_height,
            ]

        if self.connection_edit_mode:
            if "mouse_pos" in kwargs:
                self.root.ids[f"line_preview"].points = (
                    self.root.ids[f"frame_{self.selected_asset['key']}"].pos[0]
                    + component_width[self.selected_asset["type"]] / 2,
                    self.root.ids[f"frame_{self.selected_asset['key']}"].pos[1]
                    + component_height / 2,
                    kwargs["mouse_pos"][0],
                    kwargs["mouse_pos"][1] - self.root.ids.canvas_layout.pos[0] / 2,
                )

    # validation of components
    def validate_thermalsystem(self, textfield):
        # check for the required validation type and perform checks accordingly
        if textfield.validation_type in ("thermalsystem_temperature"):
            # if (self.root.ids.checkbox_thermasystem_temperature_min.active):
            if self.root.ids.textfield_thermalsystem_temperature_min.text == "":
                temperature_min = -273
            elif self.root.ids.textfield_thermalsystem_temperature_min.text == "-":
                temperature_min = -273
                print("Temperatur min ist -273")
            else:
                temperature_min = float(
                    self.root.ids.textfield_thermalsystem_temperature_min.text
                )
                print("Temperatur min eingetippt")

            if self.root.ids.textfield_thermalsystem_temperature_max.text == "":
                temperature_max = 1000000000
                print("Temperatur maximal hoch")
            elif self.root.ids.textfield_thermalsystem_temperature_max.text == "-":
                temperature_max = 1000000000
                print("Temperatur max maximal hoch")
            else:
                temperature_max = float(
                    self.root.ids.textfield_thermalsystem_temperature_max.text
                )
                print("Temperatur max eingetippt")

            if self.root.ids.textfield_thermalsystem_temperature_start.text == "":
                temperature_start = temperature_min
                print(
                    "temperature start sollte temperature min entsprechen",
                    temperature_start,
                    temperature_min,
                )
            elif self.root.ids.textfield_thermalsystem_temperature_start.text == "-":
                temperature_start = 0
                print("temperature start ist 0")
            else:
                temperature_start = float(
                    self.root.ids.textfield_thermalsystem_temperature_start.text
                )
                print("temperature start eingetippt")

            # Eigentliche Checks durchführen
            # tmin < tmax
            if not temperature_min <= temperature_max:
                textfield.helper_text = (
                    "temperature min is not allowed to be higher than temperature max"
                )
                print("t_min zu niedrig bzw t_max zu hoch")
                return False
            else:
                print("t_max größer als t_min")

            # tstart <= tmax
            if not temperature_start <= temperature_max:
                textfield.helper_text = (
                    "temperature start is not allowed to be higher temperature max"
                )
                print("t_start darf nicht höher sein als t_max")
                return False
            else:
                print("t_max größer als t_start")

            # tmin <= tstart
            if not temperature_start >= temperature_min:
                textfield.helper_text = (
                    "temperature min is not allowed to be higher than temperature start"
                )
                print("t_start muss größer sein als t_min")
                return False
            else:
                print("t_start ist größer als t_min")

            # tmin >= -273
            if not temperature_min >= -273:
                textfield.helper_text = (
                    "temperature should be higher than or equal to -273°C"
                )
                print("t_min zu klein")
                return False
            else:
                print("t_min Wert ist ok")

            if not temperature_max >= -273:
                textfield.helper_text = (
                    "temperature should be higher than or equal to -273°C"
                )
                print("t_max zu niedrig")
                return False
            else:
                print("t_max Wert ist ok")

            if not temperature_start >= -273:
                textfield.helper_text = (
                    "temperature should be higher than or equal to -273°C"
                )
                print("t_start zu niedrig")
                return False
            else:
                print("t_start Wert ist ok")

        # all checks passed? set value to be valid
        textfield.value_valid = True
        textfield.error = False

    def validate_deadtime(self):
        print("Komponente 'dedatime' aufgerufen")

    def validate_schedule(self):
        print("Kompoente 'schedule' aufgerufen")

    def validate_storage(self):
        print("Komponente 'storage' aufgerufen")

    def validate_converter(self, textfield):
        print("Komponente 'converter' aufgerufen")

        if textfield.validation_type in ("converter"):
            if self.root.ids.textfield_converter_power_max.text == "":
                power_max = 0
                print("max power gleich 0")
            elif self.root.ids.textfield_converter_power_max.text == "-":
                power_max = 0
                print("max power gleich 0")
            else:
                power_max = float(self.root.ids.textfield_converter_power_max.text)
                print("max power eingetippt")

            if self.root.ids.textfield_converter_power_min.text == "":
                power_min = 0
                print("min power gleich 0")
            elif self.root.ids.textfield_converter_power_min.text == "-":
                power_min = 0
                print("min power gleich 0")
            else:
                power_min = float(self.root.ids.textfield_converter_power_min.text)
                print("min power eingetippt")

            if self.root.ids.textfield_converter_power_nominal.text == "":
                power_nominal = 0
                print("nominal power gleich ß")
            elif self.root.ids.textfield_converter_power_nominal.text == "-":
                power_nominal = 0
                print("nominal power gleich 0")
            else:
                power_nominal = float(
                    self.root.ids.textfield_converter_power_nominal.text
                )
                print("nominal power eigetippt")

            if self.root.ids.textfield_converter_eta_max.text == "":
                eta_max = 0
                print("eta max gleich 0")
            elif self.root.ids.textfield_converter_eta_max.text == "-":
                eta_max = 0
                print("eta max gleich 0")
            else:
                eta_max = float(self.root.ids.textfield_converter_eta_max.text)
                print("eta max eingetippt")

            if self.root.ids.textfield_converter_availability.text == "":
                converter_availability = 0
                print("converter availability gleich 0")
            elif self.root.ids.textfield_converter_availability.text == "-":
                converter_availability = 0
                print("converter availabiltiy gleich 0")
            else:
                converter_availability = float(
                    self.root.ids.textfield_converter_availability.text
                )
                print("converter availability eingetippt")

            if not power_max >= power_min:
                print("max power darf nicht kleiner als min power sein")
                textfield.helper_text = "max. operating power should be higher than or equal to min. operating power"
                return False
            else:
                print("max power größer als min power")

            if power_max > power_min and power_min == 0:
                print("A.1.1")
                self.root.ids.textfield_converter_power_min.error = True
                self.root.ids.textfield_converter_power_min.helper_text = (
                    "no min. operating power"
                )
                # textfield.helper_text = "no min. operating power"
                # return
            else:
                print("B")

            if power_nominal != 0 and (
                power_nominal < power_min or power_nominal > power_max
            ):
                print("E.1")
                textfield.helper_text = (
                    "operating point is outside the limits of min. or max. power"
                )
                return False
            else:
                print("E.2")

            if not (eta_max >= 0 and eta_max <= 100):
                print("")
                textfield.helper_text = "expected percentage value between 0-100% !"
                return False
            else:
                print("I.2")

            if not (converter_availability >= 0 and converter_availability <= 100):
                print("converter availaility außerhalb der Grenzen")
                textfield.helper_text = "expected a percentage value between 0-100% !"
                return False
            else:
                print("Wert für converter availability erlaubt")

        # all checks passed? set value to be valid
        textfield.value_valid = True
        textfield.error = False

    def validate_sink(self, textfield):
        print("sink")

        # if textfield.validation_type in ("sink_power_max", "sink_power_min", "sink_demand"):
        if textfield.validation_type in ("sink"):

            if self.root.ids.textfield_sink_power_max.text == "":
                sink_power_max = 0
                # self.root.ids.textfield_sink_power_max.error = False
                print("H.1")
            elif self.root.ids.textfield_sink_power_max.text == "-":
                sink_power_max = 0
                # self.root.ids.textfield_sink_power_max.error = False
                print("Fall H.2")
            else:
                sink_power_max = float(self.root.ids.textfield_sink_power_max.text)
                # self.root.ids.textfield_sink_power_max.error = False
                print("Fall H.3")

            if self.root.ids.textfield_sink_power_min.text == "":
                sink_power_min = 0
                # self.root.ids.textfield_sink_power_min.error = False
                print("H.1")
            elif self.root.ids.textfield_sink_power_min.text == "-":
                sink_power_min = 0
                # self.root.ids.textfield_sink_power_min.error = False
                print("Fall H.2")
            else:
                sink_power_min = float(self.root.ids.textfield_sink_power_min.text)
                # self.root.ids.textfield_sink_power_min.error = False
                print("Fall H.3")

            if self.root.ids.textfield_sink_demand.text == "":
                sink_demand = 0
                # self.root.ids.textfield_sink_demand.error = False
                print("H.1")
            elif self.root.ids.textfield_sink_demand.text == "-":
                sink_demand = 0
                # self.root.ids.textfield_sink_demand.error = False
                print("Fall H.2")
            else:
                sink_demand = float(self.root.ids.textfield_sink_demand.text)
                # self.root.ids.textfield_sink_demand.error = False
                print("Fall H.3")

            if (sink_power_max != 0 or sink_power_min != 0) and sink_demand != 0:
                print("M")
                # textfield.error = True
                textfield.helper_text = (
                    "fixed demand with max/min input power not possible"
                )
                return False
            else:
                print("M.2")
                textfield.helper_text = "numbers are ok"

        # all checks passed? set value to be valid
        textfield.value_valid = True
        textfield.error = False

    def validate_source(self, textfield):

        # if textfield.validation_type in ("source_power_max", "source_power_min", "source_availability", "source_determined_power"):
        if textfield.validation_type in ("source"):

            if self.root.ids.textfield_source_availability.text == "":
                source_availability = 0
                # self.root.ids.textfield_source_availability.error = False
                print("H.1")
            elif self.root.ids.textfield_source_availability.text == "-":
                source_availability = 0
                # self.root.ids.textfield_source_availability.error = False
                print("Fall H.2")
            else:
                source_availability = float(
                    self.root.ids.textfield_source_availability.text
                )
                # self.root.ids.textfield_source_availability.error = False
                print("Fall H.3")

            if self.root.ids.textfield_source_power_max.text == "":
                source_power_max = 0
                # self.root.ids.textfield_sink_demand.error = False
                print("H.1")
            elif self.root.ids.textfield_source_power_max.text == "-":
                source_power_max = 0
                # self.root.ids.textfield_sink_demand.error = False
                print("Fall H.2")
            else:
                source_power_max = float(self.root.ids.textfield_source_power_max.text)
                # self.root.ids.textfield_sink_demand.error = False
                print("Fall H.3")

            if self.root.ids.textfield_source_power_min.text == "":
                source_power_min = 0
                # self.root.ids.textfield_sink_power_min.error = False
                print("H.1")
            elif self.root.ids.textfield_source_power_min.text == "-":
                source_power_min = 0
                # self.root.ids.textfield_sink_power_min.error = False
                print("Fall H.2")
            else:
                source_power_min = float(self.root.ids.textfield_source_power_min.text)
                # self.root.ids.textfield_sink_power_min.error = False
                print("Fall H.3")

            if self.root.ids.textfield_source_determined_power.text == "":
                source_determined_power = 0
                # self.root.ids.textfield_sink_demand.error = False
                print("H.1")
            elif self.root.ids.textfield_source_determined_power.text == "-":
                source_determined_power = 0
                # self.root.ids.textfield_sink_demand.error = False
                print("Fall H.2")
            else:
                source_determined_power = float(
                    self.root.ids.textfield_source_determined_power.text
                )
                # self.root.ids.textfield_sink_demand.error = False
                print("Fall H.3")

            if not (source_availability >= 0 and source_availability <= 100):
                print("K")
                # textfield.error = True
                textfield.helper_text = "expected percentage value between 0-100% !"
                return False
            else:
                print("K.2")
                textfield.helper_text = "numbers are ok"

            # if source_power_max != "" and source_availability == 0:
            #     print("L")
            #     #textfield.error = True
            #     textfield.helper_text = "availablility must be set"
            #     return
            # else:
            #     print("L.2")
            #     textfield.helper_text = "numbers are ok"

            if source_power_max == 0 and source_availability != 0:
                print("L")
                # textfield.error = True
                textfield.helper_text = "maximum output power must be set"
                return False
            else:
                print("L.2")
                textfield.helper_text = "numbers are ok"

            if (
                source_power_max != 0 or source_power_min != 0
            ) and source_determined_power != 0:
                print("N")
                # textfield.error = True
                textfield.helper_text = (
                    "fixed operation level with max/min output power not possible"
                )
                return False
            else:
                print("N.2")
                textfield.helper_text = "numbers are ok"

        # all checks passed? set value to be valid
        textfield.value_valid = True
        textfield.error = False

    def validate_textfield_input(self, textfield):
        """Description...."""

        # Set unsaved changes on asset to True
        self.unsaved_changes_on_asset = True

        # empty inputs do not have to be validated
        if textfield.text.strip() == "":
            textfield.text = ""
            textfield.error = False
            textfield.value_valid = True
            return

        # #assume value as invalid
        textfield.value_valid = False
        textfield.error = True

        # Make sure that the input is a number
        try:
            textfield.text = textfield.text.replace(",", ".").strip()
            input = float(textfield.text)
        except:
            if not textfield.text == "-":
                textfield.text = textfield.text[:-1]
                return

        # negative Zahlen erlauben? Grenze dann bei -273°C?
        # keine negativen Zahlen für alle Textfelder (ausgenommen thermalsystem) ?
        if not textfield.validation_type in ("thermalsystem_temperature"):
            if textfield.text == "-":
                input = 0
            if input < 0:
                textfield.text = textfield.text[1:]
                input = input * -1

        if (
            textfield.validation_type == "thermalsystem_temperature"
            and not self.validate_thermalsystem(textfield)
        ):
            return
        elif textfield.validation_type == "deadtime":
            self.validate_deadtime()
        elif textfield.validation_type == "schedule":
            self.validate_schedule()
        elif textfield.validation_type == "storage":
            self.validate_storage()
        elif textfield.validation_type == "converter" and not self.validate_converter(
            textfield
        ):
            return
        elif textfield.validation_type == "sink" and not self.validate_sink(textfield):
            return
        elif textfield.validation_type == "source" and not self.validate_source(
            textfield
        ):
            return

        # all checks passed? set value to be valid
        textfield.value_valid = True
        textfield.error = False

        # if tmin leer:
        # oder checkbox:
        #     tmin = -273
        # else:
        #     tmin = textfield_tmin
        #
        # if tmax leer:
        # oder checkbox :
        #     tmax = 100000000
        # else:
        #     tmax = textfield_tmax
        #
        # if tstart leer:
        # oder checkbox:
        #     tstart = tmin
        # else:
        #     tstart= textfield_tstart
        #
        #
        # if tmin > tmax:
        #     textfield.helper_text("...")
        #     return

    """
    def on_checkbox_active(self, checkbox, textfield, value):
        # pass
        # Set unsaved changes on asset to True
        self.unsaved_changes_on_asset = True

        # assume value as invalid
        #textfield.value_valid = False
        #textfield.error = True
        #checkbox.active = False

        #textfield.helper_text = "ok"

        self.root.ids.textfield_thermalsystem_temperature_max.helper_text = "ok"
        print(self.root.ids.textfield_thermalsystem_temperature_max.helper_text)
        value = False
        #print(textfield.helper_text)
        #checkbox.active = False


        # check for the required validation type and perform checks accordingly
        if textfield.validation_type in ("thermalsystem_temperature_start", "thermalsystem_temperature_ambient", "thermalsytem_temperature_max", "thermalsystem_temperature_min"):
            if input < -273:
                textfield.helper_text = "Input has to be greater than -273°C"
                return
            elif self.root.ids.textfield_thermalsystem_temperature_max.text < self.root.ids.textfield_thermalsystem_temperature_min.text:
                textfield.helper_text = "temperature max should be higher than temperature min"
                return
            elif self.root.ids.textfield_thermalsystem_temperature_start.text < self.root.ids.textfield_thermalsystem_temperature_min.text or self.root.ids.textfield_thermalsystem_temperature_start.text > self.root.ids.textfield_thermalsystem_temperature_max.text:
                textfield.helper_text = "temperature start should be in between of temperatrure max and min"
                return

        # check for the required validation type and perform checks accordingly
        if checkbox.validation_type in ("thermalsystem_temperature_max"):
             if value:
                self.root.ids.textfield_thermalsystem_temperature_max.helper_text = "Checkbox is active"
             elif value:
                self.root.ids.textfield_thermalsystem_temperature_max.helper_text = "Checkbox is not active"
        else:
           self.root.ids.textfield_thermalsystem_temperature_max.helper_text = "Checkbox is not active"

        # all checks passed? set value to be valid
        self.root.ids.textfield_thermalsystem_temperature_min.value_valid = True
        self.root.ids.textfield_thermalsystem_temperature_min.error = False
        #print(self.root.ids.switch_thermalsystem_temperature_min.active)
    """
