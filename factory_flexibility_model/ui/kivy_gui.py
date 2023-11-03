import os
from collections import defaultdict

from kivy.core.window import Window
from kivy.graphics import Ellipse, Line, Triangle
from kivy.lang import Builder
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IconRightWidget, TwoLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDColorPicker

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.factory.Flowtype as ft
import factory_flexibility_model.ui.utility.color as color
import factory_flexibility_model.ui.utility.flowtype_determination as fd
from factory_flexibility_model.ui.dialogs.dialog_component_definition import (
    show_component_definition_dialog,
)
from factory_flexibility_model.ui.dialogs.dialog_converter_ratios import (
    show_converter_ratio_dialog,
)
from factory_flexibility_model.ui.layouts.main_menu import *

# from factory_flexibility_model.ui.layouts.timeseries_overview import (
#    LayoutTimeseriesOverview,
# )
from factory_flexibility_model.ui.utility.custom_widget_classes import *
from factory_flexibility_model.ui.utility.update_config_tab import update_config_tab

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
    def on_start(self):
        """
        This function is automatically called by the __init_ method of the app class.
        In the context of this app it is used to add custom layouts to some widgets of the Screen.
        Added layouts include:
        - left_main_menu() into the navigation drawer in the main screen
        """
        self.root.ids.main_menu.add_widget(main_menu())

    def abort_new_connection(self, touch):
        self.connection_edit_mode = False
        Window.unbind(mouse_pos=self.update_visualization)
        self.initialize_visualization()

    def add_component(self, instance, touch):
        """
        This function adds a new component to the blueprint.
        It is being called, when the user drags one of the component dummys from the component creation menu to the main canvas
        It is checked, which component type was selected based on the instance of dmmy object handed over.
        Then a component of the correct type is added to the blueprint and all visualisations are being updated.
        The Component definition popup is being opened to give the user the option to directly configure the new component
        :param instance: The component dummy widget that the user dragged to the canvas
        :param touch: a touch event, used to prevent unintended executions
        """
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

        if component_type == "converter":
            self.blueprint.components[component_key]["GUI"]["primary_flow"] = None

        # create a temporary widget on the main canvas to store the position until self.save_component_positions()
        component_framelabel = DragLabel(id=component_key)
        component_framelabel.pos = instance.pos

        self.root.ids.canvas_layout.add_widget(component_framelabel)
        self.root.ids[f"frame_{component_key}"] = component_framelabel

        # add parameter-dict for the new component
        self.session_data["parameters"][component_key] = {}

        # close the component selection menu
        self.root.ids.component_shelf.set_state("closed")

        # catch the position of the new component and update the visualisation to show it in the correct place
        self.save_component_positions()
        self.initialize_visualization()

        # select the new asset
        self.change_selected_asset(component_key)

        # ask the user for a name, description and flowtype
        if self.session_data["show_component_config_dialog_on_creation"]:
            show_component_definition_dialog(self)

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

    def app_show_converter_ratio_dialog(self):
        show_converter_ratio_dialog(self)

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

        # IMPORT additional layouts
        # component_config_tab
        Builder.load_file(
            r"factory_flexibility_model\ui\layouts\component_config_tab.kv"
        )
        # converter ratio dialog
        Builder.load_file(
            r"factory_flexibility_model\ui\dialogs\dialog_converter_ratios.kv"
        )

        # dialog component definition
        Builder.load_file(
            r"factory_flexibility_model\ui\dialogs\dialog_component_definition.kv"
        )
        # dialog parameter config
        Builder.load_file(
            r"factory_flexibility_model\ui\dialogs\dialog_parameter_config.kv"
        )
        # dialog session_config
        Builder.load_file(
            r"factory_flexibility_model\ui\dialogs\dialog_session_config.kv"
        )
        # main menu
        Builder.load_file(r"factory_flexibility_model\ui\layouts\main_menu.kv")

        # safe session as dialog
        Builder.load_file(
            r"factory_flexibility_model\ui\dialogs\dialog_save_session_as.kv"
        )
        # unit definition dialog
        Builder.load_file(
            r"factory_flexibility_model\ui\dialogs\dialog_unit_definition.kv"
        )

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
        self.selected_asset = None  # the asset that the user has currently selected
        self.session_data = {
            "display_scaling_factor": 0.6,
            "show_component_config_dialog_on_creation": False,
            "session_path": None,
            "parameters": {},
            "timeseries": {},
            "simulations": {},
        }

        # Style Config for GUI
        self.main_color = color.color("#1D4276")
        self.dialog = None  # keeps track of currently opened dialog
        self.display_grid_size = [
            45,
            30,
        ]  # number of grid points underlying the visualisation
        self.theme_cls.colors = colors
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # paths to used .png-assets
        def get_files_in_directory(directory_path):
            files_dict = {}
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    filename, extension = os.path.splitext(file)
                    files_dict[filename] = os.path.join(root, file)
            return files_dict

        self.component_icons = get_files_in_directory("assets\\components")
        self.source_icons = get_files_in_directory("assets\\sources")
        self.sink_icons = get_files_in_directory("assets\\sinks")
        self.highlight_icons = get_files_in_directory("assets\\highlights")
        self.default_icons = get_files_in_directory("assets\\defaults")

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

        # delete all parameters saved for the component
        del self.session_data["parameters"][self.selected_asset["key"]]

        # delete the component
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
                component_framelabel.source = "assets\\empty_rectangle.png"
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
                self.session_data["parameters"][key][parameter] = float(textfield.text)

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
            self.session_data["parameters"][key]["delay"] = int(
                self.root.ids.textfield_deadtime_delay.text
            )

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
                self.session_data["parameters"][key][parameter] = float(textfield.text)

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
                self.session_data["parameters"][key][parameter] = float(textfield.text)

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

    def set_display_scaling_factor(self, *args):
        self.session_data["display_scaling_factor"] = (
            self.root.ids.layout_size_slider.value / 100 + 0.4
        )
        self.initialize_visualization()
        self.update_visualization()

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
                "source": "assets\\defaults\\thermalsystem.png",
            },
            "deadtime": {
                "id": "dummy_deadtime",
                "source": "assets\\defaults\\deadtime.png",
            },
            "schedule": {
                "id": "dummy_schedule",
                "source": "assets\\defaults\\schedule.png",
            },
            "storage": {
                "id": "dummy_storage",
                "source": "assets\\defaults\\storage.png",
            },
            "triggerdemand": {
                "id": "triggerdemand",
                "source": "assets\\defaults\\triggerdemand.png",
            },
            "converter": {
                "id": "dummy_converter",
                "source": "assets\\defaults\\converter.png",
            },
            "pool": {
                "id": "dummy_pool",
                "source": "assets\\defaults\\pool.png",
            },
            "sink": {"id": "dummy_sink", "source": "assets\\defaults\\sink.png"},
            "source": {
                "id": "dummy_source",
                "source": "assets\\defaults\\source.png",
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

    def show_flowtype_config_dialog(self):
        """
        This function opens the dialog for configuring flowtypes.
        """

        self.dialog = MDDialog(
            title="Flowtype Definition",
            type="custom",
            content_cls=dialog_flowtype_definition(),
            auto_dismiss=False,
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
            self.popup.dismiss()

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
        self.popup = MDDropdownMenu(
            caller=caller,
            items=dropdown_items,
            position="center",
            width_mult=4,
        )

        # append widget to the UI
        self.popup.bind()
        self.popup.open()

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

    def update_config_tab(self):
        """
        This function is called, when the user clicks on a component. It openes the corresponding configuration-screen in the card on the right and fills in all the values from the selected asset into the textfields and labels.
        """

        if self.selected_asset is None:
            # if no asset is selected: show the standard screen
            self.root.ids.asset_config_screens.current = "welcome_screen"
        else:
            # call update function
            update_config_tab(self)

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
