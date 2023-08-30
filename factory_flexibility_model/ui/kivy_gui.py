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
from kivy.properties import StringProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy_garden.graph import LinePlot
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    IconLeftWidget,
    ImageLeftWidgetWithoutTouch,
    IRightBodyTouch,
    OneLineAvatarListItem,
    OneLineListItem,
    TwoLineAvatarListItem,
    TwoLineIconListItem,
    TwoLineListItem,
)
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDColorPicker
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.textfield import MDTextField

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.input_validations as iv
import factory_flexibility_model.io.factory_import as imp
import factory_flexibility_model.simulation.scenario as sc
import factory_flexibility_model.simulation.simulation as fs

# IMPORT 3RD PARTY PACKAGES


main_color = "#1D4276"
version = "alpha 04.23.01"
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


class DragLabel(DragBehavior, Image):
    id = StringProperty("")
    key = StringProperty("")


class ValidatedTextField(MDTextField):
    validation_type = ""  # specifies which validate validation routine is performed when the user changes the text
    value_valid = True  # Is set to false when the user gave an invalid validate


class ValidatedCheckBox(CheckBox):
    validation_type = ""
    value = True


# class MyCheckBox(CheckBox):
#     pass


class dialog_connection_config(BoxLayout):
    pass


class FlowchartConnector(Widget):
    pass


class dialog_image_selection(BoxLayout):
    pass


class dialog_timeseries_selection(BoxLayout):
    pass


class dialog_new_component(BoxLayout):
    pass


class dialog_new_connection(BoxLayout):
    pass


class dialog_new_flow(BoxLayout):
    pass


class dialog_new_scenario(BoxLayout):
    pass


class dialog_new_session(BoxLayout):
    pass


class dialog_update_scenario(BoxLayout):
    pass


class IconListItem(TwoLineAvatarListItem):
    icon = StringProperty()


class ImageDropDownItem(OneLineAvatarListItem):
    source = StringProperty()
    text = StringProperty()


class connection_source_dropdown(DropDown):
    pass


class RightButton(IRightBodyTouch, MDRaisedButton):
    """Custom right container."""


class ScenarioCard(MDCard):
    scenario_key = StringProperty("")


class Tab(BoxLayout, MDTabsBase):
    pass


class CanvasWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            Color("#1D4276")
            Color(0.5, 0.3, 0.8, 1)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


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

        # make sure that there is at least one flowtype in the factory
        if len(self.blueprint.flows) == 0:
            self.add_flow(instance, touch)

        # assign a key to the new Component
        i = 0
        while f"component_{i}" in self.blueprint.components.keys():
            i += 1
        component_key = f"component_{i}"

        # create a blueprint entry for the Component
        self.blueprint.components[component_key] = defaultdict(lambda: "")
        self.blueprint.components[component_key]["position_x"] = 0
        self.blueprint.components[component_key]["position_y"] = 0
        self.blueprint.components[component_key][
            "key"
        ] = component_key  # number of the Component which is dragged into the layout beginning by 0
        self.blueprint.components[component_key]["flowtype"] = self.blueprint.flows[
            "flow_0"
        ][
            "key"
        ]  # number of the flowtype which is added beginning by 0

        # create a temporary widget on the main canvas to store the position until self.save_component_positions()
        component_framelabel = DragLabel(id=component_key)
        component_framelabel.pos = instance.pos

        self.root.ids.canvas_layout.add_widget(component_framelabel)
        self.root.ids[f"frame_{component_key}"] = component_framelabel

        # specify Component type, initial name and initial icon depending on the dragged dummy:

        # give the Component a unique name
        i = 1
        while self.get_key(f"Unspecified {instance.key} {i}"):
            i += 1
        self.blueprint.components[component_key][
            "name"
        ] = f"Unspecified {instance.key} {i}"  # name of Component which is dragged into the layout by numbering exemplary is 'Unspecified thermal system 1'
        self.blueprint.components[component_key][
            "type"
        ] = (
            instance.key
        )  # name of Component which is dragged into the layout exemplary thermalsystem
        self.blueprint.components[component_key]["icon"] = self.default_icons[
            instance.key
        ]

        # close the Component selection menu
        self.root.ids.component_shelf.set_state("closed")

        # catch the position of the new Component and update the visualisation to show it in the correct place
        self.save_component_positions()
        self.initialize_visualization()

        # select the new asset
        self.change_selected_asset(component_key)

        # set unsaved changes to true
        self.unsaved_changes_on_session = True

    def add_connection(self, sink_key):
        """
        This function is being called when the user confirms the creation of a new connection within the new_connection_dialog.
        """

        # disable connection edit mode
        self.connection_edit_mode = False
        Window.unbind(mouse_pos=self.update_visualization)

        # get the source
        source_name = self.selected_asset["name"]
        source_key = self.get_key(source_name)
        sink_name = self.blueprint.components[sink_key]["name"]

        # make sure that the connection is not already existing:
        for connection in self.blueprint.connections.values():
            # check all coinnections in the blueprint
            if connection["from"] == source_key and connection["to"] == sink_key:
                # if current connection is equal to the one to be created: abort and warn the user
                self.show_info_dialog(
                    f"There is already a connection from {source_name} to {sink_name}!"
                )
                return

        # create adressing key for new connection
        i = 0
        while f"connection_{i}" in self.blueprint.connections.keys():
            i += 1
        connection_key = f"connection_{i}"

        # create a new connection:
        self.blueprint.connections[connection_key] = defaultdict(lambda: "")
        self.blueprint.connections[connection_key][
            "name"
        ] = f"{source_name} -> {sink_name}"
        self.blueprint.connections[connection_key]["from"] = source_key
        self.blueprint.connections[connection_key]["to"] = sink_key
        self.blueprint.connections[connection_key]["flowtype"] = self.blueprint.flows[
            list(self.blueprint.flows.keys())[0]
        ]["key"]
        self.blueprint.connections[connection_key]["key"] = connection_key
        self.blueprint.connections[connection_key]["weight_source"] = 1
        self.blueprint.connections[connection_key]["weight_sink"] = 1
        self.blueprint.connections[connection_key]["to_losses"] = False
        self.blueprint.connections[connection_key]["type"] = "connection"

        # select the new connection for editing:
        self.selected_asset = self.blueprint.connections[connection_key]
        self.root.ids.asset_config_screens.current = "connection_config"

        # update the configuration card, visualisation and asset list
        print(self.selected_asset)
        self.update_config_tab()
        self.initialize_visualization()

        # set unsaved changes to true
        self.unsaved_changes_on_session = True

    def add_flow(self, instance, touch):
        """
        This function ads a generic new flowtype to the blueprint and selects it for configuration
        """

        # check, if the function call actually came from an object that has been clicked/moved
        if not instance.collide_point(*touch.pos):
            # abort if not
            return

        # only continue if the dummy has been moved out of the right column
        if instance.pos[0] < self.root.ids.component_shelf.width:
            self.show_component_creation_menu()
            return

        # create key for the new flowtype
        flow_key = f"flow_{len(self.blueprint.flows)}"

        i = 1
        while self.get_key(f"Unspecified Flow {i}"):
            i += 1

        # create a new flowtype:
        self.blueprint.flows[flow_key] = defaultdict(lambda: "")
        self.blueprint.flows[flow_key]["name"] = f"Unspecified Flow {i}"
        self.blueprint.flows[flow_key]["key"] = flow_key
        self.blueprint.flows[flow_key]["type"] = "energy"
        self.blueprint.flows[flow_key]["unit_flow"] = ""
        self.blueprint.flows[flow_key]["unit_flowrate"] = ""
        self.blueprint.flows[flow_key]["color"] = [0.5, 0.5, 0.5, 1]
        self.blueprint.flows[flow_key]["conversion_factor"] = 1

        # reset the Component creation menu
        self.root.ids.component_shelf.set_state("closed")

        # catch the position of the new Component and update the visualisation to show it in the correct place
        self.save_component_positions()
        self.initialize_visualization()

        # select the new flowtype
        self.change_selected_asset(flow_key)

        # set unsaved changes to true
        self.unsaved_changes_on_session = True

    def build(self):
        """
        This function is the main function that is called when creating a new instance of the GUI. It creates the Screen
        and initializes all functional variables for the GUI
        """
        # create root object for the app
        screen = Builder.load_file(
            os.path.join(os.path.dirname(__file__), "FactoryModelGUI.kv")
        )

        # Background variables for GUI
        self.blueprint = bp.blueprint()  # Stores the current factory layout
        self.connection_edit_mode = (
            False  # is set to true while the user is building a new connection
        )
        self.filepath = ""  # stores the filepath that is currently worked on
        self.unsaved_changes_on_session = False  # indicated if there have been changes to the session since opening or saving
        self.unsaved_changes_on_asset = False  # indicates if there have been changes to the current asset since selecting or saving
        self.scenarios = {}  # List of existing scenarios in the current session
        self.selected_asset = None  # the asset that the user has currently selected
        self.selected_asset_class = "Flows"  # class of the selected asset
        self.selected_parameter = (
            ""  # the scenarioparameter that the user has currently selected
        )
        self.selected_scenario = {
            "timesteps": 168,
            "name": "Testscenario",
            "time_factor": 1,
        }
        self.selected_timeseries = np.zeros(168)  # the currently activated timeseries
        self.search_text = ""  # text within the Component search bar
        self.timeseries = []  # List of imported timeseries within the session
        self.write_log = (
            True  # sets, if a log_simulation of function calls is written or not
        )
        self.version = (
            version  # version index to recognize possible conflicts with old saves
        )

        # Style Config for GUI
        self.main_color = "#1D4276"
        self.main_color_rgba = [0.1137, 0.2588, 0.463, 1]
        self.dialog = None  # keeps track of currently opened dialogs
        self.display_grid_size = [
            45,
            30,
        ]  # number of grid points underlying the visualisation
        self.display_scaling_factor = 0.7  # factor that determines the standard size of icons in the visualisation
        self.theme_cls.colors = colors
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        # self.screen.ids.textfield_thermalsystem_temperature_start.bind(on_text=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_thermalsystem_temperature_ambient.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_thermalsystem_temperature_max.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_thermalsystem_temperature_min.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_thermalsystem_sustainable.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_thermalsystem_R.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_thermalsystem_C.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_deadtime_delay.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_schedule_power_max.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_storage_charge_max.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_storage_charge_min.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_storage_discharge_max.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_storage_discharge_min.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_storage_capacity.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_storage_start.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_storage_leakage_time.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_storage_leakage_SoC.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_storage_efficiency_max.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_converter_power_max.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_converter_power_min.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_converter_availability.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_converter_rampup.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_converter_rampdown.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_converter_eta_max.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_converter_power_nominal.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_converter_delta_eta_high.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_converter_delta_eta_low.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_sink_cost.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_sink_refund.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_sink_co2_emission.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_sink_co2_refund.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_sink_power_max.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_sink_power_min.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_sink_demand.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_source_power_max.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_source_power_min.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_source_power_determined.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_source_availability.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_source_capacity_charge.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_source_emissions.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)
        # self.screen.ids.textfield_source_cost.bind(on_text_validate=self.set_error_message, on_focus=self.set_error_message,)

        # paths to used .png-assets
        self.component_icons = {
            "pool": "Assets\\icon_pool.png",
            "converter": "Assets\\icon_converter.png",
            "deadtime": "Assets\\icon_deadtime.png",
            "source": "Assets\\icon_source.png",
            "sink": "Assets\\icon_sink.png",
            "thermalsystem": "Assets\\icon_thermalsystem.png",
            "scheduler": "Assets\\icon_schedule.png",
            "storage": "Assets\\icon_storage.png",
            "Air Conditioning": "Assets\\components\\component_airconditioning.png",
            "Battery": "Assets\\components\\component_battery.png",
            "Battery Empty": "Assets\\components\\component_battery_empty.png",
            "Car": "Assets\\components\\component_car.png",
            "Car Charging": "Assets\\components\\component_car_charging.png",
            "Computer": "Assets\\components\\component_computer.png",
            "Cooling": "Assets\\components\\component_cooling.png",
            "Deadtime": "Assets\\components\\component_deadtime.png",
            "Delivery": "Assets\\components\\component_delivery.png",
            "DRI": "Assets\\components\\component_dri.png",
            "Electric Arc Furnance": "Assets\\components\\component_arc_furnance.png",
            "Electricity": "Assets\\components\\component_electricity.png",
            "Electricity House": "Assets\\components\\component_electricity_house.png",
            "Electrolysis": "Assets\\components\\component_electrolysis.png",
            "Emissions": "Assets\\components\\component_emissions.png",
            "Factory Electricity": "Assets\\components\\component_factory_electricity.png",
            "Fluxcompensator": "Assets\\components\\component_fluxcompensator.png",
            "Process Heating": "Assets\\components\\component_factory_heating.png",
            "Fan": "Assets\\components\\component_fan.png",
            "Flame": "Assets\\components\\component_flame.png",
            "Gauge": "Assets\\components\\component_gauge.png",
            "Gear": "Assets\\components\\component_gear.png",
            "Heating": "Assets\\components\\component_heating.png",
            "Heatpump": "Assets\\components\\component_heatpump.png",
            "Lightbulb": "Assets\\components\\component_lightbulb.png",
            "Nicer Dicer": "Assets\\components\\component_nicerdicer.png",
            "Production": "Assets\\components\\component_production.png",
            "Sales": "Assets\\components\\component_sales.png",
            "Schedule": "Assets\\components\\component_schedule.png",
            "Storage": "Assets\\components\\component_storage.png",
            "Temperature": "Assets\\components\\component_temperature.png",
            "Thermal Storage": "Assets\\components\\component_thermal_storage.png",
            "Transport": "Assets\\components\\component_transport.png",
            "Warning": "Assets\\components\\component_warning.png",
            "Weather": "Assets\\components\\component_weather.png",
        }
        self.icon_list = {
            "Default": "Assets\\icons\\default.png",
            "Battery": "Assets\\icons\\battery.png",
            "Flame": "Assets\\icons\\flame.png",
            "Gear": "Assets\\icons\\gear.png",
            "Airconditioning": "Assets\\icons\\airconditioning.png",
            "BatteryEmpty": "Assets\\icons\\battery_empty.png",
            "Car": "Assets\\icons\\car.png",
            "CarCharging": "Assets\\icons\\car_charging.png",
            "CO2": "Assets\\icons\\co2.png",
            "Computer": "Assets\\icons\\computer.png",
            "Cooling": "Assets\\icons\\cooling.png",
            "Deadtime": "Assets\\icons\\deadtime.png",
            "Delivery": "Assets\\icons\\delivery.png",
            "Electricity": "Assets\\icons\\electricity.png",
            "ElectricityHouse": "Assets\\icons\\electricity_house.png",
            "Electrolysis": "Assets\\icons\\electrolysis.png",
            "Emissions": "Assets\\icons\\emissions.png",
            "Fan": "Assets\\icons\\fan.png",
            "GasGrid": "Assets\\icons\\gas_grid.png",
            "GaugeEmpty": "Assets\\icons\\gauge_empty.png",
            "HeatStorage": "Assets\\icons\\heat_storage.png",
            "Heating": "Assets\\icons\\heating.png",
            "Heatpump": "Assets\\icons\\heatpump.png",
            "Hydrogen": "Assets\\icons\\hydrogen.png",
            "Lightbulb": "Assets\\icons\\lightbulb.png",
            "Losses": "Assets\\icons\\losses.png",
            "Powerpole": "Assets\\icons\\powerpole.png",
            "PressureGauge": "Assets\\icons\\pressure_gauge.png",
            "Production": "Assets\\icons\\production.png",
            "RoomTemperature": "Assets\\icons\\room_temperature.png",
            "Sales": "Assets\\icons\\sales.png",
            "Schedule": "Assets\\icons\\schedule.png",
            "Solar": "Assets\\icons\\solar.png",
            "SolarHeating": "Assets\\icons\\solar_heating.png",
            "Storage": "Assets\\icons\\storage.png",
            "Thermometer": "Assets\\icons\\thermometer.png",
            "Transport": "Assets\\icons\\transport.png",
            "Warning": "Assets\\icons\\warning.png",
            "Weather": "Assets\\icons\\weather.png",
            "Wind": "Assets\\icons\\windmill.png",
        }
        self.source_icons = {
            "Car Charging": "Assets\\sources\\source_car_charging.png",
            "CO2": "Assets\\sources\\source_co2.png",
            "Cooling": "Assets\\sources\\source_cooling.png",
            "Default": "Assets\\sources\\source_default.png",
            "Deliveries": "Assets\\sources\\source_deliveries.png",
            "Electricity": "Assets\\sources\\source_electricity.png",
            "Electrolysis": "Assets\\sources\\source_electrolysis.png",
            "Fan": "Assets\\sources\\source_fan.png",
            "Flame": "Assets\\sources\\source_flame.png",
            "Gas Grid": "Assets\\sources\\source_gas_grid.png",
            "Gauge": "Assets\\sources\\source_gauge.png",
            "Gauge Empty": "Assets\\sources\\source_gauge_empty.png",
            "Heating": "Assets\\sources\\source_heating.png",
            "Hydrogen": "Assets\\sources\\source_hydrogen.png",
            "Limestone": "Assets\\sources\\source_limestone.png",
            "Oxygen": "Assets\\sources\\source_oxygen.png",
            "Powerpole": "Assets\\sources\\source_powerpole.png",
            "Production": "Assets\\sources\\source_production.png",
            "Purchase": "Assets\\sources\\source_purchase.png",
            "Solar": "Assets\\sources\\source_solar.png",
            "Temperature": "Assets\\sources\\source_temperature.png",
            "Transport": "Assets\\sources\\source_transport.png",
            "Warehouse": "Assets\\sources\\source_warehouse.png",
            "Weather": "Assets\\sources\\source_weather.png",
            "Wind": "Assets\\sources\\source_wind.png",
        }
        self.sink_icons = {
            "Airconditioning": "Assets\\sinks\\sink_airconditioning.png",
            "Battery": "Assets\\sinks\\sink_battery.png",
            "Car Charging": "Assets\\sinks\\sink_car_charging.png",
            "CO2": "Assets\\sinks\\sink_co2.png",
            "Cooling": "Assets\\sinks\\sink_cooling.png",
            "Default": "Assets\\sinks\\sink_default.png",
            "Delivery": "Assets\\sinks\\sink_delivery.png",
            "Electricity": "Assets\\sinks\\sink_electricity.png",
            "Electricity House": "Assets\\sinks\\sink_electricity_house.png",
            "Electrolysis": "Assets\\sinks\\sink_electrolysis.png",
            "Emissions": "Assets\\sinks\\sink_emissions.png",
            "Process Heat": "Assets\\sinks\\sink_factory_heating.png",
            "Fan": "Assets\\sinks\\sink_fan.png",
            "Flame": "Assets\\sinks\\sink_Flame.png",
            "Gas Grid": "Assets\\sinks\\sink_gas_grid.png",
            "Gauge": "Assets\\sinks\\sink_gauge.png",
            "Gear": "Assets\\sinks\\sink_gear.png",
            "Hydrogen": "Assets\\sinks\\sink_hydrogen.png",
            "Lightbulb": "Assets\\sinks\\sink_lightbulb.png",
            "Losses": "Assets\\sinks\\sink_losses.png",
            "Powerpole": "Assets\\sinks\\sink_powerpole.png",
            "Production": "Assets\\sinks\\sink_production.png",
            "Sales": "Assets\\sinks\\sink_sales.png",
            "Transport": "Assets\\sinks\\sink_transport.png",
            "Warehouse": "Assets\\sinks\\sink_warehouse.png",
            "Warning": "Assets\\sinks\\sink_warning.png",
        }
        self.highlight_icons = {
            "source": "Assets\\sources\\highlight_source.png",
            "sink": "Assets\\sinks\\highlight_sink.png",
            "pool": "Assets\\components\\highlight_pool.png",
            "converter": "Assets\\components\\highlight_component.png",
            "deadtime": "Assets\\components\\highlight_component.png",
            "thermalsystem": "Assets\\components\\highlight_component.png",
            "triggerdemand": "Assets\\components\\highlight_component.png",
            "schedule": "Assets\\components\\highlight_component.png",
            "storage": "Assets\\components\\highlight_component.png",
        }
        self.scenario_images = {
            "changing_weather": "Assets\\scenarios\\changing_weather.png",
            "cheap_hydrogen": "Assets\\scenarios\\cheap_hydrogen.png",
            "cloudy": "Assets\\scenarios\\cloudy.png",
            "market": "Assets\\scenarios\\market.png",
            "market_2": "Assets\\scenarios\\market_2.png",
            "market_3": "Assets\\scenarios\\market_3.png",
            "rising_prices": "Assets\\scenarios\\rising_prices.png",
            "scenario_default": "Assets\\scenarios\\scenario_default.jpg",
            "sunny": "Assets\\scenarios\\sunny.png",
            "windstill": "Assets\\scenarios\\windstill.png",
            "windy": "Assets\\scenarios\\windy.png",
        }
        self.default_icons = {
            "pool": "Assets\\components\\component_pool.png",
            "source": "Assets\\sources\\source_default.png",
            "sink": "Assets\\sinks\\sink_default.png",
            "converter": "Assets\\components\\component_gear.png",
            "thermalsystem": "Assets\\components\\component_temperature.png",
            "deadtime": "Assets\\components\\component_deadtime.png",
            "storage": "Assets\\components\\component_battery.png",
            "schedule": "Assets\\components\\component_schedule.png",
        }

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
        This function takes a Component key and sets the asset adressed by the key as the currently selected asset.
        """

        if not self.dialog == None:
            self.dialog.dismiss()

        # get the asset adressed by the key and store it in self.selected_asset
        if key in self.blueprint.components:
            if not self.blueprint.components[key] == None:
                self.selected_asset = self.blueprint.components[key]
        if key in self.blueprint.connections:
            if not self.blueprint.connections[key] == None:
                self.selected_asset = self.blueprint.connections[key]
        if key in self.blueprint.flows:
            if not self.blueprint.flows[key] == None:
                self.selected_asset = self.blueprint.flows[key]

        # there can't be any changes on the current asset now
        self.unsaved_changes_on_asset = False

        # update the config_tab to show the selected asset
        self.update_config_tab()

        # update visualisation to highlight selected asset
        self.update_visualization()

    def click_on_component(self, instance, touch):
        """
        This function is triggered everytime when the user clicks on the Component (or on the canvas if it is still buggy)
        This function will select the clicked Component as the current asset.
        If the user moves the Component the new position will be stored using self.save_component_positions
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

        # otherwise just select the Component that has been clicked on
        print(f"selecting Component {instance.id}")
        self.initiate_asset_selection(instance.id)
        self.save_component_positions()

    def close_dialog(self):
        """
        This function closes any dialog that is still opened
        """
        if not self.dialog == None:
            self.dialog.dismiss()

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
        self.display_scaling_factor = self.display_scaling_factor * 0.95
        self.initialize_visualization()

    def delete_component(self, *args):

        self.close_dialog()

        # check, which connections need to be removed along with the Component
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

        # delete the Component out of the blueprint
        del self.blueprint.components[self.selected_asset["key"]]

        # now there is no more selected Component
        self.selected_asset = None
        self.root.ids.asset_config_screens.current = "welcome_screen"

        # redraw the visualisation without the selected Component
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

    def get_key(self, given_name):
        """
        This method takes a Component name and returns the corresponding key that the Component can be adressed with in the blueprint
        """

        # search name in Component dict
        for component in self.blueprint.components.values():
            if component["name"] == given_name:
                return component["key"]

        # search name in connection dict
        for connection in self.blueprint.connections.values():
            if connection["name"] == given_name:
                return connection["key"]

        # search name in flowtype dict
        for flow in self.blueprint.flows.values():
            if flow["name"] == given_name:
                return flow["key"]

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
        self.display_scaling_factor = self.display_scaling_factor * 1.05
        self.initialize_visualization()

    def initialize_visualization(self, *args):
        """
        This script builds the basic energy system visualisation out of the given blueprint on the Canvas within the system layout tab of the GUI
        """

        scaling_factor = (
            self.display_scaling_factor
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
        # TODO: This step is needed to have them at the background under the Component labels
        #  ...change this if there is a better way to get this behaviour
        for connection in self.blueprint.connections.values():
            # get connection color from blueprint
            connection_color = self.blueprint.flows[connection["flowtype"]]["color"]

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
                points=(0, 0, 1000, 1000), width=8 * self.display_scaling_factor
            )  #

            # place it on the canvas
            canvas.add(new_line)

            # inititalize small rectangles to display the directions of the flows
            # make them a little darker than the flowtype itself
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
            points=(-10, -10, -10, -10), width=8 * self.display_scaling_factor
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

            # create draglabel for the icon of the Component
            component_framelabel = DragLabel(
                source=component["icon"],
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
                * component["position_x"]
                / self.display_grid_size[0]
                + 50,
                self.root.ids.canvas_layout.pos[1]
                - component_height / 2
                + (self.root.ids.canvas_layout.height - 100)
                * component["position_y"]
                / self.display_grid_size[1]
                + 50,
            )

            # if the Component is a pool: create a circle in the correct color
            if component["type"] == "pool":
                # exchange the icon with an empty one
                component_framelabel.source = "Assets\\empty_rectangle.png"
                # determine of the color of the pool
                if component["flowtype"] == "":
                    canvas.add(Color(0.1137, 0.2588, 0.463, 1))
                else:
                    pool_color = self.blueprint.flows[component["flowtype"]]["color"]
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
                        component_height - 32 * self.display_scaling_factor,
                        component_height - 32 * self.display_scaling_factor,
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
                    component_framelabel.pos[0] + 16 * self.display_scaling_factor,
                    component_framelabel.pos[1] + 16 * self.display_scaling_factor,
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

        # DRAW A LEGEND OF ALL EXISTING FLOWS

        # get width of canvas
        width = self.root.ids.canvas_layout.size[0]
        height = self.root.ids.canvas_layout.size[1]
        pos_y = self.root.ids.canvas_layout.pos[1]
        delta_y = height / 20

        i_flow = 0
        for flow in self.blueprint.flows.values():
            # set line color
            canvas.add(
                Color(
                    flow["color"][0],
                    flow["color"][1],
                    flow["color"][2],
                    flow["color"][3],
                )
            )

            # create a new line object
            new_line = Line(
                points=(
                    width,
                    height + pos_y - delta_y * i_flow,
                    width * 1.05,
                    height + pos_y - delta_y * i_flow,
                ),
                width=8 * scaling_factor,
            )

            # place it on the canvas
            canvas.add(new_line)

            # create a textlabel for the flowtype
            flow_textlabel = MDLabel(
                text=flow["name"].upper(),
                halign="center",
                pos=(
                    width * 0.95,
                    height
                    + pos_y
                    - 40 * self.display_scaling_factor
                    - delta_y * i_flow,
                ),
                font_size=14 * self.display_scaling_factor,
                size=(width * 0.15, 30 * self.display_scaling_factor),
                on_touch_up=lambda touch, instance: self.click_on_component(
                    touch, instance
                ),
                id=flow["key"],
            )
            self.root.ids.canvas_layout.add_widget(flow_textlabel)

            # increment number of already shown flows
            i_flow += 1

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
        filetype = [("Factory Model Session", "*.factory")]
        filepath_new = filedialog.askopenfilename(
            defaultextension=filetype, filetypes=filetype
        )

        # make sure the user didn't abort the file selection or selected something invalid
        if filepath_new == None or filepath_new == "":
            return

        # a new filepath has been specified -> change it in the app
        self.filepath = filepath_new

        # open yaml-file given by the user
        with open(self.filepath) as file:
            data = yaml.load(file, Loader=yaml.UnsafeLoader)

        # check version compatibility
        if not hasattr(data, "version") or not data["version"] == self.version:
            # warn the user if the versions dont match
            self.show_info_dialog(
                "The imported session was created with an outdated version of the factory and may be incompatible at some points or causes unexpected crashes"
            )

        # create new blueprint based on the loaded data
        self.blueprint = bp.blueprint()

        # recreate components as a defaultdict
        for component in data["components"].values():
            self.blueprint.components[component["key"]] = defaultdict(lambda: "")
            for attribute in component:
                self.blueprint.components[component["key"]][attribute] = component[
                    attribute
                ]

        # recreate connections as a defaultdict
        for connection in data["connections"].values():
            self.blueprint.connections[connection["key"]] = defaultdict(lambda: "")
            for attribute in connection:
                self.blueprint.connections[connection["key"]][attribute] = connection[
                    attribute
                ]

        # recreate flows as a defaultdict
        for flow in data["flows"].values():
            self.blueprint.flows[flow["key"]] = defaultdict(lambda: "")
            for attribute in flow:
                self.blueprint.flows[flow["key"]][attribute] = flow[attribute]

        # recreate info dict
        self.blueprint.info.update(data["info"])

        # recreate scenarios
        self.scenarios = {}
        self.root.ids.grid_scenarios.clear_widgets()
        if "scenarios" in data:
            for scenario in data["scenarios"].values():
                self.new_scenario(data=scenario)

        # There are no more unsaved changes now...
        self.unsaved_changes_on_session = False
        self.unsaved_changes_on_asset = False

        # there is no Component selected initially
        self.selected_asset = None

        # update the GUI to display the data
        self.root.ids.scenario_screens.current = "scenario_selection_screen"
        self.root.ids.asset_config_screens.current = "welcome_screen"
        self.root.ids.label_session_name.text = self.blueprint.info["name"]
        self.initialize_visualization()

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
            self.save_session(True)

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
            # get requested name and description
            session_name = self.dialog.content_cls.ids.textfield_new_session_name.text
            session_description = (
                self.dialog.content_cls.ids.textfield_new_session_description.text
            )

            # close the previous dialog
            self.dialog.dismiss()

            # create an empty blueprint and add the given information
            self.blueprint = bp.blueprint()
            self.blueprint.info["name"] = session_name
            self.blueprint.info["description"] = session_description

            # store current tool version in the blueprint to enable warnings later
            self.blueprint.info["version"] = self.version

            # set the selected asset to none
            self.selected_asset = None

            # initialize the GUI
            self.initialize_visualization()
            self.root.ids.asset_config_screens.current = "welcome_screen"
            self.root.ids.label_session_name.text = session_name

            # New session has not been saved yet
            self.unsaved_changes_on_session = True
            self.unsaved_changes_on_asset = False

            # reset scenarios
            self.scenarios = {}
            self.root.ids.grid_scenarios.clear_widgets()

            # inform the user
            Snackbar(text=f"Starting new Session: {session_name}").open()

    def on_start(self):
        self.root.ids.label_version.text = f"Version: {self.version}"
        self.root.ids.label_session_name.text = "Unspecified Session"

    def run_simulation(self):

        # prepare blueprint for execution of simulation
        simulation_data = bp.blueprint()

        # include components
        for component in self.blueprint.components.values():
            simulation_data.components[component["key"]] = {}
            for value in component:
                if not component[value] == "" and "scenario_" not in value:
                    simulation_data.components[component["key"]][value] = component[
                        value
                    ]
            # replace name with key
            # TODO: include key/name separation in the factorymodel itself!!!
            simulation_data.components[component["key"]]["name"] = component["key"]
            del simulation_data.components[component["key"]]["key"]

        # include connections
        simulation_data.connections = {}
        for connection in self.blueprint.connections.values():
            simulation_data.connections[connection["key"]] = {}
            for value in connection:
                simulation_data.connections[connection["key"]][value] = connection[
                    value
                ]

        # include flows
        simulation_data.flows = {}
        for flow in self.blueprint.flows.values():
            simulation_data.flows[flow["key"]] = {}
            for value in flow:
                if not value == "color":
                    simulation_data.flows[flow["key"]][value] = flow[value]
                else:
                    simulation_data.flows[flow["key"]][value] = [
                        round(flow[value][0], 2),
                        round(flow[value][1], 2),
                        round(flow[value][2], 2),
                        1,
                    ]
                simulation_data.flows[flow["key"]]["name"] = flow["key"]

        # include scenario_data of currently selected scenario
        for parameter in self.selected_scenario["parameters"].values():
            simulation_data.components[parameter["Component"]][
                parameter["attribute"]
            ] = parameter["timeseries"]

        # include general information
        simulation_data.info = self.blueprint.info
        simulation_data.info["max_timesteps"] = self.selected_scenario["timesteps"]

        factory = imp.import_factory_blueprint(simulation_data)

        # create a scenario object with the given simulation parameters:
        Testscenario = sc.scenario(self.selected_scenario["name"])
        Testscenario.number_of_timesteps = self.selected_scenario["timesteps"]
        Testscenario.timefactor = self.selected_scenario["time_factor"]

        # call the factory factory to conduct the simulation
        simulation = fs.simulation(
            factory, Testscenario, enable_simulation_log=True, enable_solver_log=True
        )

        simulation.create_dash("default")

    def save_session(self, use_filepath, *args):
        """
        This function saves the current session to a file for later reopening
        """

        # make sure that there is a factory to save:
        if (
            len(self.blueprint.components) < 2
            or len(self.blueprint.connections) < 1
            or len(self.blueprint.flows) < 1
        ):
            # create dialog
            btn_ok = MDFlatButton(text="OK")
            self.dialog = MDDialog(
                title="Insufficient Components",
                text="There is no factory to safe yet! Add at least one flowtype, two components and a connection before saving.",
                buttons=[btn_ok],
            )
            btn_ok.bind(on_release=self.dialog.dismiss)
            self.dialog.open()
            return

        # create a set of serializable data out of the blueprint
        # initialize a new dict
        data = {}

        # store only the defined values per asset. Data doesnt contain defaultdicts anymore now
        data["components"] = {}
        for component in self.blueprint.components.values():
            data["components"][component["key"]] = {}
            for value in component:
                data["components"][component["key"]][value] = component[value]

        data["connections"] = {}
        for connection in self.blueprint.connections.values():
            data["connections"][connection["key"]] = {}
            for value in connection:
                data["connections"][connection["key"]][value] = connection[value]

        data["flows"] = {}
        for flow in self.blueprint.flows.values():
            data["flows"][flow["key"]] = {}
            for value in flow:
                if not value == "color":
                    data["flows"][flow["key"]][value] = flow[value]
                else:
                    data["flows"][flow["key"]][value] = [
                        round(flow[value][0], 2),
                        round(flow[value][1], 2),
                        round(flow[value][2], 2),
                        1,
                    ]

        data["info"] = self.blueprint.info

        data["scenarios"] = {}
        for scenario in self.scenarios.values():
            data["scenarios"][scenario["key"]] = {}
            for value in scenario:
                if not value == "card_widget":
                    data["scenarios"][scenario["key"]][value] = scenario[value]

        if not use_filepath or self.filepath == "":
            # ask user for filepath
            filetype = [("Factory Model Session", "*.factory")]
            new_filepath = filedialog.asksaveasfile(
                defaultextension=filetype, filetypes=filetype
            )

            # check if the user aborted the selection
            if new_filepath == None:
                return
            else:
                self.filepath = new_filepath.name

        # store the blueprint dictionary as json file
        with open(self.filepath, "w") as file:
            yaml.dump(data, file)

        # There are no more unsaved changes now...
        self.unsaved_changes_on_session = False

        Snackbar(text=f"Session succesfully saved at {self.filepath}").open()

    def save_changes_on_flow(self):
        """
        This function takes the user validate from the flowtype configuration tab and stores it in the blueprint
        """

        # store key of old version
        flow_key = self.get_key(self.selected_asset["name"])
        # store user given new name
        new_name = self.root.ids.textfield_flow_name.text

        # make sure that the given name is not taken yet
        if not new_name == self.blueprint.flows[flow_key]["name"] and self.get_key(
            new_name
        ):
            self.show_info_dialog("The given name is already bound to another asset!")
            return

        # delete the old blueprint entry
        del self.blueprint.flows[flow_key]

        # create a new blueprint entry with given values
        self.blueprint.flows[flow_key] = defaultdict(lambda: "")
        self.blueprint.flows[flow_key].update(
            {
                "name": new_name,
                "key": flow_key,
                "unit_flow": self.root.ids.textfield_flow_unit_energy.text,
                "unit_flowrate": self.root.ids.textfield_flow_unit_power.text,
                "conversion_factor": self.root.ids.textfield_flow_conversion_factor.text,
                "color": self.root.ids.icon_color_flow.icon_color,
            }
        )
        # set the flowtype type
        if self.root.ids.checkbox_flow_energy.active:
            self.blueprint.flows[flow_key]["type"] = "energy"
        elif self.root.ids.checkbox_flow_material.active:
            self.blueprint.flows[flow_key]["type"] = "material"
        else:
            self.blueprint.flows[flow_key]["type"] = "unspecified"

        # reselect the asset to adapt changes
        self.selected_asset = self.blueprint.flows[flow_key]

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the visualization:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"Flow {self.selected_asset['name']} updated!").open()

    def save_changes_on_converter(self):
        """
        This function takes the user validate from the converter configuration tab and stores it in the blueprint
        """

        # store key of old version
        component_key = self.get_key(self.selected_asset["name"])

        # make sure that the given name is not taken yet
        if not self.blueprint.components[component_key][
            "name"
        ] == self.root.ids.textfield_converter_name.text and self.get_key(
            self.root.ids.textfield_converter_name.text
        ):
            self.show_info_dialog("The given name is already bound to another asset!")
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
            self.show_info_dialog(
                "Changes can not be stored due to invalid values remaining"
            )
            return

        # create a new blueprint entry with given values
        converter_new = defaultdict(lambda: "")
        converter_new = {
            "name": self.root.ids.textfield_converter_name.text,
            "key": component_key,
            "type": "converter",
            "description": self.root.ids.textfield_converter_description.text,
            "power_max": self.root.ids.textfield_converter_power_max.text,
            "power_min": self.root.ids.textfield_converter_power_min.text,
            "availability": self.root.ids.textfield_converter_availability.text,
            "max_pos_ramp_power": self.root.ids.textfield_converter_rampup.text,
            "max_neg_ramp_power": self.root.ids.textfield_converter_rampdown.text,
            "eta_max": self.root.ids.textfield_converter_eta_max.text,
            "power_nominal": self.root.ids.textfield_converter_power_nominal.text,
            "delta_eta_high": self.root.ids.textfield_converter_delta_eta_high.text,
            "delta_eta_low": self.root.ids.textfield_converter_delta_eta_low.text,
            "icon": self.root.ids.image_converter_configuration.source,
            "position_x": self.selected_asset["position_x"],
            "position_y": self.selected_asset["position_y"],
        }

        # overwrite old entry
        self.blueprint.components[component_key] = converter_new

        # set selected asset to the updated converter
        self.selected_asset = converter_new

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
        # This function takes the user validate from the storage configuration tab and stores it in the blueprint
        """

        # store key of old version
        component_key = self.get_key(self.selected_asset["name"])

        # create a new blueprint entry with given values
        storage_new = defaultdict(lambda: "")
        storage_new = {"name": self.root.ids.textfield_storage_name.text,
                       "key": component_key,
                       "type": "storage",
                       "description": self.root.ids.textfield_storage_description.text,
                       #"flowtype": self.get_key(self.root.ids.textfield_storage_flow.text),
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
                       "position_x": self.selected_asset["position_x"],
                       "position_y": self.selected_asset["position_y"]}

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
        This function takes the user validate from the deadtime configuration tab and stores it in the blueprint
        """

        # store key of old version
        component_key = self.get_key(self.selected_asset["name"])

        if not (self.root.ids.textfield_deadtime_delay.value_valid):
            self.show_info_dialog(
                "Changes can not be stored due to invalid values remaining"
            )
            return

        # create a new blueprint entry with given values
        deadtime_new = defaultdict(lambda: "")
        deadtime_new = {
            "name": self.root.ids.textfield_deadtime_name.text,
            "key": component_key,
            "type": "deadtime",
            "description": self.root.ids.textfield_deadtime_description.text,
            # "flowtype": self.get_key(self.root.ids.textfield_deadtime_flow.text),
            "Delay": self.root.ids.textfield_deadtime_delay.text,
            "icon": self.root.ids.image_deadtime_configuration.source,
            "position_x": self.selected_asset["position_x"],
            "position_y": self.selected_asset["position_y"],
        }

        # overwrite old entry
        self.blueprint.components[component_key] = deadtime_new

        # set selected asset to the updated deadtime
        self.selected_asset = deadtime_new

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the visualisation:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_schedule(self):
        """
        This function takes the user validate from the schedule configuration tab and stores it in the blueprint
        """

        # store key of old version
        component_key = self.get_key(self.selected_asset["name"])

        if not (self.root.ids.textfield_schedule_power_max.value_valid):
            self.show_info_dialog(
                "Changes can not be stored due to invalid values remaining"
            )
            return

        # create a new blueprint entry with given values
        schedule_new = defaultdict(lambda: "")
        schedule_new = {
            "name": self.root.ids.textfield_schedule_name.text,
            "key": component_key,
            "type": "schedule",
            "description": self.root.ids.textfield_schedule_description.text,
            # "flowtype": self.get_key(self.root.ids.textfield_schedule_flow.text),
            "Maximum power flowtype": self.root.ids.textfield_schedule_power_max.text,
            "icon": self.root.ids.image_schedule_configuration.source,
            "position_x": self.selected_asset["position_x"],
            "position_y": self.selected_asset["position_y"],
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

    def save_changes_on_connection(self):
        """
        This function takes the user validate from the connection configuration tab and stores it in the blueprint
        """
        # saving changes to a flowtype means that there are unsaved changes in the session
        self.unsaved_changes_on_session = True

        # store the connection key for reuse
        connection_key = self.selected_asset["key"]

        # delete the old blueprint entry
        del self.blueprint.connections[self.selected_asset["key"]]

        # create new empty dict for connection
        self.blueprint.connections[connection_key] = defaultdict(lambda: "")

        # create new name:
        new_name = f"{self.root.ids.textfield_connection_source.text} -> {self.root.ids.textfield_connection_sink.text}"

        # create a new blueprint entry with given values
        self.blueprint.connections[connection_key].update(
            {
                "name": new_name,
                "key": connection_key,
                "from": self.get_key(self.root.ids.textfield_connection_source.text),
                "to": self.get_key(self.root.ids.textfield_connection_sink.text),
                "weight_source": self.root.ids.textfield_connection_weight_source.text,
                "weight_sink": self.root.ids.textfield_connection_weight_sink.text,
                "flowtype": self.get_key(self.root.ids.textfield_connection_flow.text),
                "to_losses": self.root.ids.checkbox_connection_losses.active,
                "type": "connection",
            }
        )

        # reselect the asset to adapt changes
        self.selected_asset = self.blueprint.connections[connection_key]

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the preview:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_pool(self):
        """
        This function takes the user validate from the pool configuration tab and stores it in the blueprint
        """

        # make sure that the given name is not taken yet
        if not self.blueprint.components[self.selected_asset["key"]][
            "name"
        ] == self.root.ids.textfield_pool_name.text and self.get_key(
            self.root.ids.textfield_pool_name.text
        ):
            self.show_info_dialog("The given name is already bound to another asset!")
            return

        # create new blueprint entry
        pool_new = defaultdict(lambda: "")
        pool_new.update(
            {
                "name": self.root.ids.textfield_pool_name.text,
                "key": self.selected_asset["key"],
                "type": "pool",
                "description": self.root.ids.textfield_pool_description.text,
                "flowtype": self.get_key(self.root.ids.textfield_pool_flow.text),
                "position_x": self.blueprint.components[self.selected_asset["key"]][
                    "position_x"
                ],
                "position_y": self.blueprint.components[self.selected_asset["key"]][
                    "position_y"
                ],
                "icon": "Assets\\components\\component_pool.png",
            }
        )

        # overwrite old entry
        self.blueprint.components[self.selected_asset["key"]] = pool_new

        # update connection names to adapt changes if the name of the pool has changed
        self.update_connection_names()

        # reselect the pool to adapt changes
        self.selected_asset = pool_new

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the preview:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_sink(self):
        """
        This function takes the user validate from the sink configuration tab and stores it in the blueprint
        """

        # make sure that the given name is not taken yet
        if not self.blueprint.components[self.selected_asset["key"]][
            "name"
        ] == self.root.ids.textfield_sink_name.text and self.get_key(
            self.root.ids.textfield_sink_name.text
        ):
            self.show_info_dialog("The given name is already bound to another asset!")
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
                self.show_info_dialog(
                    "Changes can not be stored due to invalid values remaining"
                )
                return

        # create new blueprint entry
        sink_new = defaultdict(lambda: "")
        sink_new.update(
            {
                "name": self.root.ids.textfield_sink_name.text,
                "key": self.selected_asset["key"],
                "type": "sink",
                "description": self.root.ids.textfield_sink_description.text,
                "flowtype": self.get_key(self.root.ids.textfield_sink_flow.text),
                "cost": self.root.ids.textfield_sink_cost.text,
                "power_max": self.root.ids.textfield_sink_power_max.text,
                "power_min": self.root.ids.textfield_sink_power_min.text,
                "demand": self.root.ids.textfield_sink_demand.text,
                "revenue": self.root.ids.textfield_sink_refund.text,
                "co2_emission_per_unit": self.root.ids.textfield_sink_co2_emission.text,
                "co2_refund_per_unit": self.root.ids.textfield_sink_co2_refund.text,
                "position_x": self.blueprint.components[self.selected_asset["key"]][
                    "position_x"
                ],
                "position_y": self.blueprint.components[self.selected_asset["key"]][
                    "position_y"
                ],
                "icon": self.root.ids.image_sink_configuration.source,
                "scenario_determined": self.root.ids.switch_sink_determined.active,
                "scenario_co2_refund_per_unit": self.root.ids.switch_sink_co2_refund.active,
                "scenario_co2_emission_per_unit": self.root.ids.switch_sink_co2_emission.active,
                "scenario_revenue": self.root.ids.switch_sink_refund.active,
                "scenario_cost": self.root.ids.switch_sink_cost.active,
            }
        )

        # overwrite old entry
        self.blueprint.components[self.selected_asset["key"]] = sink_new

        # reselect asset to adapt the changes:
        self.selected_asset = sink_new

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # update connection names to adapt changes if the name of the sink has changed
        self.update_connection_names()

        # redraw the preview:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_source(self):
        """
        This function takes the user validate from the source configuration tab and stores it in the blueprint
        """

        # make sure that the given name is not taken yet
        if not self.blueprint.components[self.selected_asset["key"]][
            "name"
        ] == self.root.ids.textfield_source_name.text and self.get_key(
            self.root.ids.textfield_source_name.text
        ):
            self.show_info_dialog("The given name is already bound to another asset!")
            return

            # Check, that all user inputs are valid
            if (
                not (self.root.ids.textfield_source_power_max.value_valid)
                and (self.root.ids.textfield_source_power_min.value_valid)
                and (self.root.ids.textfield_source_power_determined.value_valid)
                and (self.root.ids.textfield_source_availability.value_valid)
                and (self.root.ids.textfield_source_capacity_charge.value_valid)
                and (self.root.ids.textfield_source_emissions.value_valid)
                and (self.root.ids.textfield_source_cost.value_valid)
            ):
                self.show_info_dialog(
                    "Changes can not be stored due to invalid values remaining"
                )
                return

        # create new blueprint entry
        source_new = defaultdict(lambda: "")
        source_new.update(
            {
                "availability": iv.validate(
                    self.root.ids.textfield_source_availability.text, "float"
                ),
                "capacity_charge": iv.validate(
                    self.root.ids.textfield_source_capacity_charge.text, "float"
                ),
                "cost": iv.validate(self.root.ids.textfield_source_cost.text, "float"),
                "description": self.root.ids.textfield_source_description.text,
                "emissions": iv.validate(
                    self.root.ids.textfield_source_emissions.text, "float"
                ),
                "flowtype": self.get_key(self.root.ids.textfield_source_flow.text),
                "icon": self.root.ids.image_source_configuration.source,
                "key": self.selected_asset["key"],
                "name": self.root.ids.textfield_source_name.text,
                "position_x": self.blueprint.components[self.selected_asset["key"]][
                    "position_x"
                ],
                "position_y": self.blueprint.components[self.selected_asset["key"]][
                    "position_y"
                ],
                "power_max": iv.validate(
                    self.root.ids.textfield_source_power_max.text, "float"
                ),
                "power_min": iv.validate(
                    self.root.ids.textfield_source_power_min.text, "float"
                ),
                "power_determined": iv.validate(
                    self.root.ids.textfield_source_power_determined.text, "float"
                ),
                "scenario_availability": self.root.ids.switch_source_availability.active,
                "scenario_cost": self.root.ids.switch_source_cost.active,
                "scenario_determined": self.root.ids.switch_source_determined.active,
                "scenario_emissions": self.root.ids.switch_source_emissions.active,
                "type": "source",
            }
        )

        # overwrite old entry
        self.blueprint.components[self.selected_asset["key"]] = source_new

        # change the selected Component:
        self.selected_asset = source_new

        # update connection names to adapt changes if the name of the source has changed
        self.update_connection_names()

        # set unsaved changes parameters
        self.unsaved_changes_on_asset = False
        self.unsaved_changes_on_session = True

        # redraw the preview:
        self.initialize_visualization()

        # inform the user
        Snackbar(text=f"{self.selected_asset['name']} updated!").open()

    def save_changes_on_storage(self):
        """
        This function takes the user validate from the storage configuration tab and stores it in the blueprint
        """

        # make sure that the given name is not taken yet
        if not self.blueprint.components[self.selected_asset["key"]][
            "name"
        ] == self.root.ids.textfield_storage_name.text and self.get_key(
            self.root.ids.textfield_storage_name.text
        ):
            self.show_info_dialog("The given name is already bound to another asset!")
            return

            # Check, that all user inputs are valid
            if (
                not (self.root.ids.textfield_storage_capacity_valid)
                and (self.root.ids.textfield_storage_power_max.value_valid)
                and (self.root.ids.textfield_storage_power_min.value_valid)
                and (self.root.ids.textfield_storage_soc_start.value_valid)
                and (self.root.ids.textfield_storage_efficiency.value_valid)
                and (self.root.ids.textfield_storage_leakage_time.value_valid)
                and (self.root.ids.textfield_storage_leakage_soc.value_valid)
            ):
                self.show_info_dialog(
                    "Changes can not be stored due to invalid values remaining"
                )
                return

        # create new blueprint entry
        storage_new = defaultdict(lambda: "")
        storage_new.update(
            {
                "capacity": self.root.ids.textfield_storage_capacity.text,
                "description": self.root.ids.textfield_storage_description.text,
                "efficiency": self.root.ids.textfield_storage_efficiency.text,
                "flowtype": self.get_key(self.root.ids.textfield_storage_flow.text),
                "icon": self.root.ids.image_storage_configuration.source,
                "key": self.selected_asset["key"],
                "leakage_soc": self.root.ids.textfield_storage_leakage_soc.text,
                "leakage_time": self.root.ids.textfield_storage_leakage_time.text,
                "name": self.root.ids.textfield_storage_name.text,
                "position_x": self.blueprint.components[self.selected_asset["key"]][
                    "position_x"
                ],
                "position_y": self.blueprint.components[self.selected_asset["key"]][
                    "position_y"
                ],
                "power_max_charge": self.root.ids.textfield_storage_power_max.text,
                "power_max_discharge": self.root.ids.textfield_storage_power_min.text,
                "soc_start": self.root.ids.textfield_storage_soc_start.text,
                "type": "storage",
            }
        )

        # overwrite old entry
        self.blueprint.components[self.selected_asset["key"]] = storage_new

        # change the selected Component:
        self.selected_asset = storage_new

        # update connection names to adapt changes if the name of the source has changed
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
        This function takes the user validate from the thermal system configuration tab and stores it in the blueprint
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
            self.show_info_dialog(
                "Changes can not be stored due to invalid values remaining"
            )
            return

        # store key of old version
        component_key = self.get_key(self.selected_asset["name"])

        # create a new blueprint entry with given values
        thermalsystem_new = defaultdict(lambda: "")
        thermalsystem_new = {
            "name": self.root.ids.textfield_thermalsystem_name.text,
            "key": component_key,
            "type": "thermalsystem",
            "description": self.root.ids.textfield_thermalsystem_description.text,
            # "flowtype": self.get_key(self.root.ids.textfield_thermalsystem_flow.text),
            "Start temperature": self.root.ids.textfield_thermalsystem_temperature_start.text,
            "ambient temperature": self.root.ids.textfield_thermalsystem_temperature_ambient.text,
            "maximum temperature": self.root.ids.textfield_thermalsystem_temperature_max.text,
            "minimum temperature": self.root.ids.textfield_thermalsystem_temperature_min.text,
            "sustainable": self.root.ids.textfield_thermalsystem_sustainable.text,
            "R": self.root.ids.textfield_thermalsystem_R.text,
            "C": self.root.ids.textfield_thermalsystem_C.text,
            "icon": self.root.ids.image_thermalsystem_configuration.source,
            "position_x": self.selected_asset["position_x"],
            "position_y": self.selected_asset["position_y"],
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
        This function is called everytime when a Component has been moven by the user within the layout visualisation.
        It checks the current positions of all components for deviations from their last known location.
        If a position deviates more than the expected rounding error the new position is stored in the blueprint
        """

        # create a factor that determines the size of displayed components depending on the canvas size and the number
        # of elements to be displayed. The concrete function is try and error and my be changed during development
        scaling_factor = (
            self.display_scaling_factor
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
            # calculate the current relative position on the canvas for the Component
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

            # make sure that the new position is within the grid. If not: move tho Component to the closest border
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

                # Check, if the Component has been dragged on top of the recycle bin to delete it..
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
                    # if x coordinate of the Component has changed more than expected rounding error:
                    if not current_pos_x - component["position_x"] == 0:
                        component["position_x"] = current_pos_x
                        changes_done = True

                    # if y coordinate of the Component has changed more than expected rounding error: store it
                    if not current_pos_y - component["position_y"] == 0:
                        component["position_y"] = current_pos_y
                        changes_done = True

        # mark session as changed if changes have been done:
        if changes_done:
            self.unsaved_changes_on_session = True
            self.initialize_visualization()

    def set_display_scaling_factor(self, *args):
        self.display_scaling_factor = self.root.ids.layout_size_slider.value / 100 + 0.4
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
                "Component": self.selected_parameter["Component"],
                "attribute": self.selected_parameter["attribute"],
            }
        if value_type == "Custom Timeseries":
            # write the currently given parameter specification into the scenario
            self.selected_scenario["parameters"][self.selected_parameter["key"]] = {
                "type": "custom_timeseries",
                "timeseries": self.selected_timeseries,
                "unit": self.root.ids.textfield_custom_timeseries_unit.text,
                "Component": self.selected_parameter["Component"],
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
        # abort if the event has not been triggered by the touched Component
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

    def show_asset_list(self):
        """
        This function creates a list of all existing assets and presents them to the user in the right info card
        """

        # clear existing list
        self.root.ids.list_assets.clear_widgets()

        # recreate lost based on the flows in current blueprint
        for flow in self.blueprint.flows.values():
            if not flow == None:  # necessary because flows is a defaultdict
                if (
                    self.search_text == ""
                    or (self.search_text.upper() in flow["name"].upper())
                    or (self.search_text.upper() in "FLOW")
                ):
                    # define image and item
                    icon = IconLeftWidget(
                        icon="waves",
                        icon_size=30,
                        theme_icon_color="Custom",
                        icon_color=flow["color"],
                    )
                    item = TwoLineAvatarListItem(
                        text=flow["name"],
                        secondary_text="flowtype",
                        on_release=self.select_asset_list_item,
                    )
                    # place components correctly in the layout
                    item.add_widget(icon)
                    self.root.ids.list_assets.add_widget(item)

        # recreate list based on the connections in current blueprint
        for connection in self.blueprint.connections.values():

            if (
                self.search_text == ""
                or (self.search_text.upper() in connection["name"].upper())
                or (self.search_text.upper() in "CONNECTION")
            ):

                # define icon and item
                icon = IconLeftWidget(
                    icon="fast-forward",
                    icon_size=30,
                    theme_icon_color="Custom",
                    icon_color=self.blueprint.flows[connection["flowtype"]]["color"],
                )
                item = TwoLineIconListItem(
                    text=connection["name"],
                    secondary_text="connection",
                    on_release=self.select_asset_list_item,
                )

                # place components correctly in the layout
                item.add_widget(icon)
                self.root.ids.list_assets.add_widget(item)

        # iterate over all Component types
        for component in self.blueprint.components.values():
            if (
                self.search_text == ""
                or (self.search_text.upper() in component["type"].upper())
                or (self.search_text.upper() in component["name"].upper())
            ):
                # search the correct image
                image = ImageLeftWidgetWithoutTouch(source=component["icon"])

                # create list item
                item = TwoLineAvatarListItem(
                    text=component["name"],
                    id=f"listitem_{component['name']}",
                    secondary_text=component["type"],
                    on_release=self.select_asset_list_item,
                )

                # place components correctly
                item.add_widget(image)
                self.root.ids.list_assets.add_widget(item)

        # show the asset browser
        self.root.ids.asset_config_screens.current = "asset_browser"

    def show_color_picker(self):
        self.dialog = MDColorPicker(size_hint=(0.3, 0.5), background_color=[1, 1, 1, 1])
        self.dialog.open()
        self.dialog.bind(
            on_release=self.update_flow_color,
        )

    def show_component_creation_menu(self):

        # COMPONENTS

        # define the Component dummys to be created
        component_dummys = {
            "source": {
                "id": "dummy_source",
                "source": "Assets\\sources\\source_default.png",
            },
            "sink": {"id": "dummy_sink", "source": "Assets\\sinks\\sink_default.png"},
            "pool": {
                "id": "dummy_pool",
                "source": "Assets\\components\\component_pool.png",
            },
            "converter": {
                "id": "dummy_converter",
                "source": "Assets\\components\\component_gear.png",
            },
            "storage": {
                "id": "dummy_storage",
                "source": "Assets\\components\\component_battery.png",
            },
            "schedule": {
                "id": "dummy_schedule",
                "source": "Assets\\components\\component_schedule.png",
            },
            "deadtime": {
                "id": "dummy_deadtime",
                "source": "Assets\\components\\component_deadtime.png",
            },
            "thermalsystem": {
                "id": "dummy_thermalsystem",
                "source": "Assets\\components\\component_temperature.png",
            },
        }

        # get available height of the Component canvas
        canvas_height = self.root.ids.canvas_shelf.size[1]
        canvas_width = self.root.ids.canvas_shelf.size[0]

        # calculate height for components
        component_height = canvas_height / (len(component_dummys) + 1)
        component_pos_x = (canvas_width - component_height * 1.5) / 2

        # clear Component dummy canvas
        self.root.ids.canvas_shelf.canvas.clear()

        # iterate over all specified dummys and create them
        i = 0
        for type in component_dummys:
            # create draglabel for the icon of the Component
            component_dummy = DragLabel(
                source=component_dummys[type]["source"],
                id=component_dummys[type]["id"],
                key=type,
                on_touch_up=lambda touch, instance: self.add_component(touch, instance),
            )
            component_dummy.pos = (
                component_pos_x + component_height * 0.25,
                canvas_height / len(component_dummys) * i,
            )
            component_dummy.size = (component_height * 1.5, component_height)
            self.root.ids.canvas_shelf.add_widget(component_dummy)
            i += 1

        # FLOW

        # clear flowtype dummy canvas
        self.root.ids.canvas_flow.canvas.clear()

        # create and position a flowtype dummy icon
        flow_dummy = DragLabel(
            source="Assets\\icon_flow.png",
            id="dummy_flow",
            key="flowtype",
            on_touch_up=lambda touch, instance: self.add_flow(touch, instance),
            pos=(
                self.root.ids.canvas_flow.size[0] * 0.15,
                self.root.ids.canvas_flow.pos[1],
            ),
            size=(
                self.root.ids.canvas_flow.size[0] * 0.7,
                self.root.ids.canvas_flow.size[1],
            ),
        )
        self.root.ids.canvas_flow.add_widget(flow_dummy)

        # show the Component shelf
        self.root.ids.component_shelf.set_state("open")

    def show_component_deletion_dialog(self):

        # abort if there is no asset or a flowtype or connection selected
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
            text="Do you really want to delete the Component with all its adherent connections?",
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
                        "source": component["icon"],
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

    def show_flow_creation_dialog(self):
        # create dialog
        btn_false = MDFlatButton(text="CANCEL")
        btn_true = MDRaisedButton(text="CREATE NEW FLOW")
        self.dialog = MDDialog(
            title="New Flow",
            buttons=[btn_false, btn_true],
            type="custom",
            content_cls=dialog_new_flow(),
        )
        btn_false.bind(on_release=self.dialog.dismiss)
        btn_true.bind(on_release=self.add_flow)
        self.dialog.open()

    def show_flow_selection_dropdown(self, caller):
        """
        This function creates a dropdown menu giving the user the option to select one of the flows in the blueprint.
        The name of the selected flowtype is being set as text to the Component that this function is being called from.
        """

        def set_text(caller, text):
            # this function returns the user selection to the object that the dialog has been called from
            caller.text = text
            self.menu.dismiss()

        # initialize empty list
        dropdown_items = []
        # iterate over all components in the blueprint
        for flow in self.blueprint.flows.values():
            # append a dropdown item to the list
            dropdown_items.append(
                {
                    "viewclass": "IconListItem",
                    "icon": "waves-arrow-right",
                    "text": flow["name"],
                    "on_release": lambda x=flow["name"]: set_text(caller, x),
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
        The filepath of the selected icon is being set as text to the Component that this function is being called from.
        """

        def set_image(caller, path):
            # change icon in the selected asset
            # self.selected_asset["icon"] = path

            # return the selected icon to the iconlabel in the config-tab
            caller.source = path
            self.selected_asset["icon"] = path
            self.initialize_visualization()

            # close icon selection dialog
            self.menu.dismiss()

        # initialize empty list
        dropdown_items = []

        # determine which selection of icons is displayed
        if self.selected_asset["type"] == "source":
            icon_list = self.source_icons
        elif self.selected_asset["type"] == "sink":
            icon_list = self.sink_icons
        else:
            icon_list = self.component_icons

        # iterate over all icons in the list
        for icon_name in icon_list:
            # append a dropdown item to the list with the current icon
            dropdown_items.append(
                {
                    "viewclass": "ImageDropDownItem",
                    "source": icon_list[icon_name],
                    "text": icon_name,
                    "on_release": lambda x=icon_list[icon_name]: set_image(caller, x),
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

    def show_info_dialog(self, text):
        """
        This function creates an overlay dialog that displays the user a handed over text message.
        The user can only confirm by clicking OK
        """
        # create dialog
        btn_ok = MDRaisedButton(text="OK")
        self.dialog = MDDialog(title="Warning", buttons=[btn_ok], text=text)
        btn_ok.bind(on_release=self.dialog.dismiss)
        self.dialog.open()

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

    def show_scenario_deletion_dialog(self, instance):
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

    def show_parameter_unit_selection_dialog(self):
        def set_text(text):
            # this function returns the user selection to the object that the dialog has been called from
            self.root.ids.textfield_custom_timeseries_unit.text = text
            self.menu.dismiss()

        # initialize empty list
        dropdown_items = []

        # append a dropdown item to the list
        dropdown_items.append(
            {
                "viewclass": "OneLineListItem",
                "text": "kW",
                "on_release": lambda x="kW": set_text(x),
            }
        )
        dropdown_items.append(
            {
                "viewclass": "OneLineListItem",
                "text": "€",
                "on_release": lambda x="€": set_text(x),
            }
        )
        dropdown_items.append(
            {
                "viewclass": "OneLineListItem",
                "text": "kWh",
                "on_release": lambda x="kWh": set_text(x),
            }
        )
        dropdown_items.append(
            {
                "viewclass": "OneLineListItem",
                "text": "°C",
                "on_release": lambda x="°C": set_text(x),
            }
        )
        dropdown_items.append(
            {
                "viewclass": "OneLineListItem",
                "text": "kg",
                "on_release": lambda x="kg": set_text(x),
            }
        )

        # create list widget
        self.menu = MDDropdownMenu(
            caller=self.root.ids.textfield_custom_timeseries_unit,
            items=dropdown_items,
            position="center",
            width_mult=4,
        )
        # append widget to the UI
        self.menu.bind()
        self.menu.open()

    def switch_search_text(self, text=""):
        # set the search text to the value selected in the search widget
        self.search_text = text

        # update the displayed list
        self.show_asset_list()

    def select_asset_list_item(self, list_item):
        """
        This function is called everytime when the user selects a Component in the Component browser.
        It searches for the corresponding key to the selected listitem and calls the change_selected_asset - method
        """

        # make sure that there is something selected:
        if not list_item == ():
            # call the asset selection method with the key corresponding to the selected list item
            self.initiate_asset_selection(self.get_key(list_item.text))

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
            "Component": self.get_key(list_item.text),
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
            This subfunction creates a list entry representing a single Component parameter that has to be specified
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
                    append_item(component["icon"], component["name"], "availability")
                if component["scenario_cost"]:
                    append_item(component["icon"], component["name"], "cost")
                if component["scenario_determined"]:
                    append_item(
                        component["icon"], component["name"], "determined_power"
                    )
                if component["scenario_emissions"]:
                    append_item(component["icon"], component["name"], "emissions")
            elif component["type"] == "sink":
                if component["scenario_revenue"]:
                    append_item(component["icon"], component["name"], "revenue")
                if component["scenario_cost"]:
                    append_item(component["icon"], component["name"], "cost")
                if component["scenario_determined"]:
                    append_item(component["icon"], component["name"], "demand")
                if component["scenario_co2_emission_per_unit"]:
                    append_item(
                        component["icon"], component["name"], "Emissions Created"
                    )
                if component["scenario_co2_refund_per_unit"]:
                    append_item(
                        component["icon"], component["name"], "Emissions Avoided"
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

        if self.selected_asset["type"] == "connection":
            self.root.ids.asset_config_screens.current = "connection_config"
            # get data from blueprint and add it to the screen
            self.root.ids.textfield_connection_weight_source.text = str(
                self.selected_asset["weight_source"]
            )
            self.root.ids.textfield_connection_weight_sink.text = str(
                self.selected_asset["weight_sink"]
            )
            self.root.ids.checkbox_connection_losses.active = self.selected_asset[
                "to_losses"
            ]
            self.root.ids.textfield_connection_flow.text = self.blueprint.flows[
                self.selected_asset["flowtype"]
            ]["name"]

            if self.selected_asset["from"] == "":
                self.root.ids.textfield_connection_source.text = ""
            else:
                self.root.ids.textfield_connection_source.text = (
                    self.blueprint.components[self.selected_asset["from"]]["name"]
                )

            if self.selected_asset["to"] == "":
                self.root.ids.textfield_connection_sink.text = ""
            else:
                self.root.ids.textfield_connection_sink.text = (
                    self.blueprint.components[self.selected_asset["to"]]["name"]
                )

        elif (
            self.selected_asset["type"] == "energy"
            or self.selected_asset["type"] == "material"
        ):
            # open the correct screen within the configuration tab:
            self.root.ids.asset_config_screens.current = "flow_config"
            # get data from blueprint and add it to the screen
            self.root.ids.textfield_flow_name.text = self.selected_asset["name"]
            self.root.ids.textfield_flow_unit_power.text = self.selected_asset[
                "unit_flowrate"
            ]
            self.root.ids.textfield_flow_unit_energy.text = self.selected_asset[
                "unit_flow"
            ]
            self.root.ids.textfield_flow_conversion_factor.text = str(
                self.selected_asset["conversion_factor"]
            )
            self.root.ids.icon_color_flow.icon_color = self.selected_asset["color"]
            self.unsaved_changes_on_asset = False

        elif self.selected_asset["type"] == "source":
            self.root.ids.asset_config_screens.current = "source_config"
            # get data from blueprint and add it to the screen
            self.root.ids.label_source_name.text = self.selected_asset["name"]
            self.root.ids.textfield_source_name.text = self.selected_asset["name"]
            self.root.ids.textfield_source_description.text = self.selected_asset[
                "description"
            ]
            self.root.ids.textfield_source_flow.text = self.blueprint.flows[
                self.selected_asset["flowtype"]
            ]["name"]
            self.root.ids.textfield_source_cost.text = str(self.selected_asset["cost"])
            self.root.ids.textfield_source_capacity_charge.text = str(
                self.selected_asset["capacity_charge"]
            )
            self.root.ids.textfield_source_emissions.text = str(
                self.selected_asset["emissions"]
            )
            self.root.ids.textfield_source_power_max.text = str(
                self.selected_asset["power_max"]
            )
            self.root.ids.textfield_source_power_min.text = str(
                self.selected_asset["power_min"]
            )
            self.root.ids.textfield_source_power_determined.text = self.selected_asset[
                "power_determined"
            ]
            self.root.ids.textfield_source_availability.text = str(
                self.selected_asset["availability"]
            )
            self.validate_textfield_input(self.root.ids.textfield_source_availability)
            self.root.ids.image_source_configuration.source = self.selected_asset[
                "icon"
            ]
            self.root.ids.switch_source_availability.active = self.selected_asset[
                "scenario_availability"
            ]
            self.root.ids.switch_source_cost.active = self.selected_asset[
                "scenario_cost"
            ]
            self.root.ids.switch_source_determined.active = self.selected_asset[
                "scenario_determined"
            ]
            self.root.ids.switch_source_emissions.active = self.selected_asset[
                "scenario_emissions"
            ]

        elif self.selected_asset["type"] == "pool":
            # show the pool configuration screeen in the box on the bottom of the screen
            self.root.ids.asset_config_screens.current = "pool_config"
            self.root.ids.label_pool_name.text = self.selected_asset["name"]
            self.root.ids.textfield_pool_flow.text = self.blueprint.flows[
                self.selected_asset["flowtype"]
            ]["name"]
            self.root.ids.textfield_pool_name.text = self.selected_asset["name"]
            self.root.ids.textfield_pool_description.text = self.selected_asset[
                "description"
            ]

        elif self.selected_asset["type"] == "converter":
            # show the converter configuration screeen in the box on the bottom of the screen
            self.root.ids.asset_config_screens.current = "converter_config"
            # read values from the blueprint and initialize the validate fields
            self.root.ids.label_converter_name.text = self.selected_asset["name"]
            self.root.ids.textfield_converter_name.text = self.selected_asset["name"]
            self.root.ids.textfield_converter_description.text = self.selected_asset[
                "description"
            ]
            self.root.ids.textfield_converter_power_max.text = str(
                self.selected_asset["power_max"]
            )
            self.root.ids.textfield_converter_power_min.text = str(
                self.selected_asset["power_min"]
            )
            self.root.ids.textfield_converter_availability.text = str(
                self.selected_asset["availability"]
            )
            self.root.ids.textfield_converter_rampup.text = str(
                self.selected_asset["max_pos_ramp_power"]
            )
            self.root.ids.textfield_converter_rampdown.text = str(
                self.selected_asset["max_neg_ramp_power"]
            )
            self.root.ids.textfield_converter_eta_max.text = str(
                self.selected_asset["eta_max"]
            )
            self.root.ids.textfield_converter_power_nominal.text = str(
                self.selected_asset["power_nominal"]
            )
            self.root.ids.textfield_converter_delta_eta_high.text = str(
                self.selected_asset["delta_eta_high"]
            )
            self.root.ids.textfield_converter_delta_eta_low.text = str(
                self.selected_asset["delta_eta_low"]
            )
            self.validate_textfield_input(self.root.ids.textfield_converter_power_min)
            self.validate_textfield_input(self.root.ids.textfield_converter_power_max)
            self.validate_textfield_input(self.root.ids.textfield_converter_rampup)
            self.validate_textfield_input(self.root.ids.textfield_converter_rampdown)
            self.validate_textfield_input(self.root.ids.textfield_converter_eta_max)
            self.validate_textfield_input(
                self.root.ids.textfield_converter_power_nominal
            )
            self.validate_textfield_input(
                self.root.ids.textfield_converter_availability
            )

            # display the correct icon
            self.root.ids.image_converter_configuration.source = self.selected_asset[
                "icon"
            ]

        elif self.selected_asset["type"] == "sink":
            self.root.ids.asset_config_screens.current = "sink_config"
            # get data from blueprint and add it to the screen
            self.root.ids.label_sink_name.text = self.selected_asset["name"]
            self.root.ids.textfield_sink_name.text = self.selected_asset["name"]
            self.root.ids.textfield_sink_description.text = self.selected_asset[
                "description"
            ]
            self.root.ids.textfield_sink_cost.text = str(self.selected_asset["cost"])
            self.root.ids.textfield_sink_refund.text = str(
                self.selected_asset["revenue"]
            )
            self.root.ids.textfield_sink_co2_emission.text = str(
                self.selected_asset["co2_emission_per_unit"]
            )
            self.root.ids.textfield_sink_co2_refund.text = str(
                self.selected_asset["co2_refund_per_unit"]
            )
            self.root.ids.textfield_sink_flow.text = self.blueprint.flows[
                self.selected_asset["flowtype"]
            ]["name"]
            self.root.ids.textfield_sink_power_max.text = str(
                self.selected_asset["power_max"]
            )
            self.root.ids.textfield_sink_power_min.text = str(
                self.selected_asset["power_min"]
            )
            self.root.ids.textfield_sink_demand.text = str(
                self.selected_asset["demand"]
            )
            self.root.ids.image_sink_configuration.source = self.selected_asset["icon"]
            self.root.ids.switch_sink_determined.active = self.selected_asset[
                "scenario_determined"
            ]
            self.root.ids.switch_sink_co2_refund.active = self.selected_asset[
                "scenario_co2_refund_per_unit"
            ]
            self.root.ids.switch_sink_co2_emission.active = self.selected_asset[
                "scenario_co2_emission_per_unit"
            ]
            self.root.ids.switch_sink_refund.active = self.selected_asset[
                "scenario_revenue"
            ]
            self.root.ids.switch_sink_cost.active = self.selected_asset["scenario_cost"]

        elif self.selected_asset["type"] == "storage":
            self.root.ids.asset_config_screens.current = "storage_config"
            # read values from the blueprint and initialize the validate fields
            self.root.ids.label_storage_name.text = self.selected_asset["name"]
            self.root.ids.textfield_storage_name.text = self.selected_asset["name"]
            self.root.ids.textfield_storage_description.text = self.selected_asset[
                "description"
            ]
            # self.root.ids.textfield_schedule_flow.text = self.blueprint.flows[self.selected_asset["flowtype"]]["name"]
            self.root.ids.textfield_storage_power_max.text = self.selected_asset[
                "power_max_charge"
            ]
            self.root.ids.textfield_storage_power_min.text = self.selected_asset[
                "power_max_discharge"
            ]
            # self.root.ids.textfield_storage_discharge_max.text = self.selected_asset["Maximum discharging power"]
            # self.root.ids.textfield_storage_discharge_min.text = self.selected_asset["Minimum discharging power"]
            self.root.ids.textfield_storage_capacity.text = self.selected_asset[
                "capacity"
            ]
            self.root.ids.textfield_storage_soc_start.text = self.selected_asset[
                "soc_start"
            ]
            self.root.ids.textfield_storage_leakage_time.text = self.selected_asset[
                "leakage_time"
            ]
            self.root.ids.textfield_storage_leakage_soc.text = self.selected_asset[
                "leakage SoC"
            ]
            self.root.ids.textfield_storage_efficiency.text = self.selected_asset[
                "efficiency"
            ]

            # display the correct icon
            # self.root.ids.image_storage_configuration.source = self.selected_asset["icon"]

        elif self.selected_asset["type"] == "thermalsystem":
            # show the thermal system configuration screeen in the box on the bottom of the screen
            self.root.ids.asset_config_screens.current = "thermalsystem_config"
            # read values from the blueprint and initialize the validate fields
            self.root.ids.label_thermalsystem_name.text = self.selected_asset["name"]
            self.root.ids.textfield_thermalsystem_name.text = self.selected_asset[
                "name"
            ]
            self.root.ids.textfield_thermalsystem_description.text = (
                self.selected_asset["description"]
            )
            # self.root.ids.textfield_thermalsystem_flow.text = self.blueprint.flows[self.selected_asset["flowtype"]]["name"]
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
                self.selected_asset["icon"]
            )

        elif self.selected_asset["type"] == "schedule":
            # show the schedule configuration screeen in the box on the bottom of the screen
            self.root.ids.asset_config_screens.current = "schedule_config"
            # read values from the blueprint and initialize the validate fields
            self.root.ids.label_schedule_name.text = self.selected_asset["name"]
            self.root.ids.textfield_schedule_name.text = self.selected_asset["name"]
            self.root.ids.textfield_schedule_description.text = self.selected_asset[
                "description"
            ]
            # self.root.ids.textfield_schedule_flow.text = self.blueprint.flows[self.selected_asset["flowtype"]]["name"]
            self.root.ids.textfield_schedule_power_max.text = self.selected_asset[
                "Maximum power flowtype"
            ]
            # display the correct icon
            self.root.ids.image_schedule_configuration.source = self.selected_asset[
                "icon"
            ]

        elif self.selected_asset["type"] == "triggerdemand":
            pass

        elif self.selected_asset["type"] == "deadtime":
            # show the deadtime configuration screeen in the box on the bottom of the screen
            self.root.ids.asset_config_screens.current = "deadtime_config"
            # read values from the blueprint and initialize the validate fields
            self.root.ids.label_deadtime_name.text = self.selected_asset["name"]
            self.root.ids.textfield_deadtime_name.text = self.selected_asset["name"]
            self.root.ids.textfield_deadtime_description.text = self.selected_asset[
                "description"
            ]
            # self.root.ids.textfield_deadtime_flow.text = self.blueprint.flows[self.selected_asset["flowtype"]]["name"]
            self.root.ids.textfield_deadtime_delay.text = self.selected_asset["Delay"]
            self.validate_textfield_input(self.root.ids.textfield_deadtime_delay)
            # display the correct icon
            self.root.ids.image_deadtime_configuration.source = self.selected_asset[
                "icon"
            ]

        # since the asset just got updated there are no unsaved changes anymore
        self.unsaved_changes_on_asset = False

    def update_connection_names(self):
        for connection in self.blueprint.connections.values():
            connection[
                "name"
            ] = f'{self.blueprint.components[connection["from"]]["name"]} -> {self.blueprint.components[connection["to"]]["name"]} '

    def update_flow_color(
        self, instance_color_picker: MDColorPicker, type_color: str, selected_color
    ):
        """
        This function updates the color of the component_color_button in the flowtype-tab
        by giving the user a colorpicker-interface
        """
        self.root.ids.icon_color_flow.icon_color = selected_color[:-1] + [1]
        self.dialog.dismiss()
        self.set_unsaved_changes_on_asset(True)

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
            print(f"updating graph to static value: {value}")

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
            print(f"updating graph to timeseries with peak: {max_value}")
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
        It is being called on startup once and everytime a Component gets moved by the user
        """

        # Specify a scaling factor depending on the size of the canvas and the number of components to be displayed
        # scaling factor = width_of_canvas / sqrt(number_of_components+1) / adjustment_factor
        scaling_factor = (
            self.display_scaling_factor
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

        # create dataset with the incoming and outgoing connections per Component, sorted by the direction
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
                    # set the id of the current connection at the Component
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

                    # get the Component that the connection has to start/end from
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

                # get the widths of sink and source Component
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

        # highlight the selected Component
        if (
            self.selected_asset == None
            or self.selected_asset == ""
            or self.selected_asset["type"] == "energy"
            or self.selected_asset["type"] == "material"
            or self.selected_asset["type"] == "connection"
        ):
            #  if the user selected a flowtype, a connection or no Component at all: move the highlight image out of sight
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
            # place it behind the selected Component
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

    # def on_active(self,instance, value):
    #     if value:
    #         print("Checkbox ist aktiviert")
    #     else:
    #         print("Checkbox wurde nicht aktiviert")

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

        # assume value as invalid
        textfield.value_valid = False
        textfield.error = True  # hier auf False setzen

        # Make sure that the validate is a number
        try:
            textfield.text = textfield.text.replace(",", ".").strip()
            input = float(textfield.text)
        except:
            textfield.text = textfield.text[:-1]
            return

        if not textfield.validation_type in ("thermalsystem_temperature"):
            if input < 0:
                textfield.text = textfield.text[1:]
                input = input * -1

        # check for the required validation type and perform checks accordingly
        if textfield.validation_type in ("thermalsystem_temperature"):

            # if (self.root.ids.checkbox_thermasystem_temperature_min.active):
            # self.root.ids_thermalsystem_temperature_min.text = "-274"

            # Werte für Vergleiche bestimmen
            if self.root.ids.textfield_thermalsystem_temperature_min.text == "":
                temperature_min = -273
                self.root.ids.textfield_thermalsystem_temperature_min.text = "-273"
                self.root.ids.textfield_thermalsystem_temperature_min.error = False
                print("Fall 1")
            else:
                temperature_min = float(
                    self.root.ids.textfield_thermalsystem_temperature_min.text
                )
                print("Fall 2")

            if self.root.ids.textfield_thermalsystem_temperature_max.text == "":
                # temperature_max = float(self.root.ids.textfield_thermalsystem_temperature_max.text)
                self.root.ids.textfield_thermalsystem_temperature_max.text = (
                    "1000000000"
                )
                temperature_max = 1000000000
                self.root.ids.textfield_thermalsystem_temperature_max.error = False
                print("Fall 3")
            else:
                temperature_max = float(
                    self.root.ids.textfield_thermalsystem_temperature_max.text
                )
                print("Fall 4")

            if self.root.ids.textfield_thermalsystem_temperature_start.text == "":
                # self.root.ids.textfield_thermalsystem_temperature_max.text = self.root.ids.textfield_thermalsystem_temperature_start.text
                temperature_start = temperature_max
                self.root.ids.textfield_thermalsystem_temperature_start.error = False
                print("Fall 5")
            else:
                temperature_start = float(
                    self.root.ids.textfield_thermalsystem_temperature_start.text
                )
                print("Fall 6")

            # Eigentliche Checks durchführen
            # tmin < tmax
            if not temperature_min <= temperature_max:
                textfield.helper_text = (
                    "temperature min is not allowed to be higher than temperature max"
                )
                print("Fall 7")
                return
            else:
                textfield.helper_text = "Werte ok"
                print("Fall 8")
                self.root.ids.textfield_thermalsystem_temperature_min.error = False

            # tmin <= tstart
            # tstart <= tmax
            # tmin >= -273

            if not temperature_min <= temperature_start:
                textfield.helper_text = (
                    "temperature min is not allowed to be higher than temperature start"
                )
                print("Fall 9")
                return
            else:
                textfield.helper_text = "Werte ok"
                print("Fall 10")
                self.root.ids.textfield_thermalsystem_temperature_min.error = False

            if not temperature_start <= temperature_max:
                textfield.helper_text = (
                    "temperature start is not allowed to be higher temperature max"
                )
                print("Fall 11")
                return
            else:
                textfield.helper_text = "Werte ok"
                print("Fall 12")
                self.root.ids.textfield_thermalsystem_temperature_min.error = False

            if not temperature_min >= -273:
                textfield.helper_text = (
                    "temperature min should be higher than or equal to -273°C"
                )
                print("Fall 13")
                return
            else:
                textfield.helper_text = "Werte ok"
                print("Fall 14")
                self.root.ids.textfield_thermalsystem_temperature_min.error = False

            if (
                self.root.ids.textfield_thermalsystem_temperature_min.text == "-273"
                or self.root.ids.textfield_thermalsystem_temperature_max.text
                == "1000000000"
            ):
                print("Fall 15")
                self.root.ids.textfield_thermalsystem_temperature_start.error = False
                self.root.ids.textfield_thermalsystem_temperature_start.text = (
                    self.root.ids.textfield_thermalsystem_temperature_min.text
                )
            # else:
            #     temperature_min = float(self.root.ids.textfield_thermalsystem_temperature_min.text)
            #     print("Fall 2")

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

        # if textfield.validation_type in ("thermalsystem_R", "thermalsystem_C", "deadtime_delay", "converter_rampup", "converter_rampdown", "converter_power_nominal"):
        #      if validate < 0:
        #          textfield.helper_text = "Input has to be greater than 0"
        #
        # # check for the required validation type and perform checks accordingly
        # if textfield.validation_type in ("converter_power_max", "converter_power_min"):
        #      if validate < 0:
        #          textfield.helper_text = "Input has to be greater than 0"
        #      elif self.root.ids.textfield_converter_power_max.text < self.root.ids.textfield_converter_power_min.text:
        #           textfield.helper_text = "power max should be higher than power min"
        #      #elif self.root.ids.textfield_converter_power_max.text > self.root.ids.textfield_converter_power_min.text:
        #      #     textfield.helper_text = "numbers are ok"
        #      # else:
        #      #    textfield.error = False
        #
        # # check for the required validation type and perform checks accordingly
        # if textfield.validation_type in ("converter_eta_max", "converter_availability", "source_availability"):
        #      if validate < 0 or validate > 100:
        #         textfield.helper_text = "0-100% required"
        #
        # # check for the required validation type and perform checks accordingly
        # if textfield.validation_type in ("converter_power_nominal"):
        #      if textfield.text > self.root.ids.textfield_converter_power_max.text or textfield.text < self.root.ids.textfield_converter_power_min.text:
        #         textfield.helper_text = "Operating point must be between min. and max. power"

        # if textfield.validation_type in (....):
        #    if validate < 0:
        #        textfield.helper_text = "Input has to be at least 0"
        #        return

        # elif textfield.validation_type == "%":
        #     if validate >= 0 and validate <= 1:
        # return

        # all checks passed? set value to be valid
        textfield.value_valid = True
        textfield.error = False

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
            if validate < -273:
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
