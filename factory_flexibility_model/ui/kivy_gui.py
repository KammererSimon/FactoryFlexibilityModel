# IMPORTS
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.ui.utility.flowtype_determination as fd
from factory_flexibility_model.ui.gui_components.import_gui_components import (
    import_gui_components,
)
from factory_flexibility_model.ui.gui_components.layout_canvas.drag_label.draglabel import (
    DragLabel,
)
from factory_flexibility_model.ui.gui_components.layout_canvas.factory_visualisation import (
    initialize_visualization,
    save_component_positions,
    update_visualization,
)
from factory_flexibility_model.ui.gui_components.layout_component_configuration.dialog_component_definition.dialog_component_definition import (
    show_component_definition_dialog,
)
from factory_flexibility_model.ui.gui_components.layout_component_configuration.layout_component_configuration_tab import (
    update_component_configuration_tab,
)
from factory_flexibility_model.ui.gui_components.layout_component_creation.layout_component_creation import (
    show_component_creation_menu,
)
from factory_flexibility_model.ui.gui_components.main_menu.layout_main_menu import (
    main_menu,
)
from factory_flexibility_model.ui.utility.GUI_logging import log_event
from factory_flexibility_model.ui.utility.io.import_config_files import import_config
from factory_flexibility_model.ui.utility.window_handling import resize_window


# CLASSES
class factory_GUIApp(MDApp):
    def on_start(self):
        """
        This function is automatically called by the __init_ method of the app class.
        In the context of this app it is used to add custom layouts to some widgets of the Screen.
        Added layouts include:
        - left_main_menu() into the navigation drawer in the main screen

        :return: None
        """
        self.root.ids.main_menu.add_widget(main_menu())
        initialize_visualization(self)

    def abort_new_connection(self, touch):
        self.connection_edit_mode = False
        Window.unbind(mouse_pos=update_visualization(self))
        initialize_visualization(self)

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
            show_component_creation_menu(self)
            return

        # abort if there is no session yet
        if self.session_data["session_path"] is None:
            log_event(
                self,
                "Cannot create components before initializing or importing a session!",
                "ERROR",
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
                "icon": self.config["assets"]["default_icons"][component_type],
            },
            "description": "",
            "type": component_type,
            "flowtype": self.blueprint.flowtypes["unknown"],
        }

        # Exception: Thermalsystems are always initialized with flowtype heat
        if component_type == "thermalsystem":
            self.blueprint.components[component_key][
                "flowtype"
            ] = self.blueprint.flowtypes["heat"]

        # initialize converter primary flows as None
        if component_type == "converter":
            self.blueprint.components[component_key]["GUI"]["primary_flow"] = None

        # create a temporary widget on the main canvas to store the position until save_component_positions()
        component_framelabel = DragLabel(id=component_key)
        component_framelabel.pos = instance.pos

        self.root.ids.canvas_layout.add_widget(component_framelabel)
        self.root.ids[f"frame_{component_key}"] = component_framelabel

        # close the component selection menu
        self.root.ids.component_shelf.set_state("closed")

        # catch the position of the new component and update the visualisation to show it in the correct place
        save_component_positions(self)
        initialize_visualization(self)

        # select the new asset
        self.change_selected_asset(component_key)

        # ask the user for a name, description and flowtype
        if self.session_data["show_component_config_dialog_on_creation"]:
            show_component_definition_dialog(self)

        # set unsaved changes to true
        self.unsaved_changes_on_session = True

        # write log
        log_event(
            self, f"New {component_type} created with key '{component_key}'", "DEBUG"
        )

    def add_connection(self, destination_key):
        """
        This function is being called when the user activated the connection creation mode and then clicked on a destination component
        """

        # disable connection edit mode
        self.connection_edit_mode = False
        Window.unbind(mouse_pos=update_visualization(self))

        # get the origin
        origin_name = self.selected_asset["name"]
        origin_key = self.get_key(origin_name)
        origin_flowtype = self.blueprint.components[origin_key]["flowtype"]
        destination_name = self.blueprint.components[destination_key]["name"]
        destination_flowtype = self.blueprint.components[destination_key]["flowtype"]

        # find existing inputs and outputs for source and destination component
        input_qty = 0
        output_qty = 0
        for connection in self.blueprint.connections.values():
            if connection["from"] == origin_key:
                output_qty += 1
            if connection["to"] == destination_key:
                input_qty += 1

        # check, if origin component can provide another output
        if (
            output_qty
            >= self.config["component_definitions"][
                self.blueprint.components[origin_key]["type"]
            ]["max_outputs"]
        ):
            # in case the origin component already reached its maximum number of outputs:
            log_event(
                self,
                f"{origin_name} already has the maximum number of outputs connected",
                "ERROR",
            )
            initialize_visualization(self)
            return

        if (
            input_qty
            >= self.config["component_definitions"][
                self.blueprint.components[destination_key]["type"]
            ]["max_inputs"]
        ):
            # in case the origin component already reached its maximum number of inputs:
            log_event(
                self,
                f"{destination_name} already has the maximum number of inputs connected",
                "ERROR",
            )
            initialize_visualization(self)
            return

        # make sure that the connection is not already existing:
        for connection in self.blueprint.connections.values():
            # check all connections in the blueprint
            if connection["from"] == origin_key and connection["to"] == destination_key:
                # if current connection is equal to the one to be created: abort and warn the user
                log_event(
                    self,
                    f"Creating connection failed: There is already a connection from {origin_name} to {destination_name}!",
                    "ERROR",
                )
                initialize_visualization(self)
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
                log_event(
                    self,
                    f"Creating connection failed: {origin_name} and {destination_name} have incompatible flowtypes!",
                    "ERROR",
                )
                return

        # create adressing key for new connection
        i = 0
        while f"connection_{i}" in self.blueprint.connections.keys():
            i += 1
        connection_key = f"connection_{i}"

        # create a new connection:
        self.blueprint.connections[connection_key] = {}
        self.blueprint.connections[connection_key]["from"] = origin_key
        self.blueprint.connections[connection_key]["to"] = destination_key
        self.blueprint.connections[connection_key]["flowtype"] = connection_flowtype
        self.blueprint.connections[connection_key]["key"] = connection_key
        self.blueprint.connections[connection_key]["weight_origin"] = 1
        self.blueprint.connections[connection_key]["weight_destination"] = 1
        self.blueprint.connections[connection_key]["to_losses"] = False
        self.blueprint.connections[connection_key]["type"] = "connection"

        # update the configuration card, visualisation and asset list
        initialize_visualization(self)

        # set unsaved changes to true
        self.unsaved_changes_on_session = True

        # write log
        log_event(
            self,
            f"New connection created from {origin_name} to {destination_name} with key '{connection_key}'",
            "DEBUG",
        )

    def build(self):
        """
        .. _build:
        This function is the main function that is called when creating a new instance of the GUI. It creates the Screen
        and initializes all functional variables for the GUI

        :return: None
        """

        # import all the kivy-layout files for the different gui_components
        import_gui_components()

        # create root object for the app
        screen = Builder.load_file(
            r"factory_flexibility_model\ui\gui_components\main_window\FactoryModelGUI.kv"
        )

        # Background variables for GUI
        self.blueprint = bp.Blueprint()  # Stores the current factory layout
        self.config = import_config()
        self.connection_edit_mode = (
            False  # is set to true while the user is building a new connection
        )
        self.dialog = None  # keeps track of currently opened dialog
        self.dropdown = None  # keeps track of currently opened dropdown
        self.popup = None  # keeps track of currently opened popup
        self.unsaved_changes_on_session = False  # indicated if there have been changes to the session since opening or saving
        self.unsaved_changes_on_asset = False  # indicates if there have been changes to the current asset since selecting or saving
        self.selected_asset = None  # the asset that the user has currently selected
        self.session_data = {
            "display_scaling_factor": self.config["display_scaling_factor"],
            "log": [],  # initialize an empty list to collect log messages
            "parameters": {},
            "show_component_config_dialog_on_creation": self.config[
                "show_component_config_dialog_on_creation"
            ],
            "session_path": None,
            "session_active": False,
            "simulations": {},
            "timeseries": {},
        }

        # Style Config for GUI
        self.theme_cls.colors = self.config["color_preset"]
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # set window configuration
        Window.maximize()  # start in fullscreen
        # update the visualization when changing the window size
        Window.bind(on_resize=resize_window)
        Window.bind(on_maximize=resize_window)
        Window.bind(on_restore=resize_window)
        self.title = "Factory Flexibility Model"

        return screen

    def change_selected_asset(self, key):
        """
        This function takes a component key and sets the asset adressed by the key as the currently selected asset.

        :param key:
        :return: None
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
        update_component_configuration_tab(self)

        # update visualisation to highlight selected asset
        update_visualization(self)

    def click_on_component(self, instance, touch):
        """
        This function is triggered everytime when the user clicks on the component (or on the canvas if it is still buggy)
        This function will select the clicked component as the current asset.
        If the user moves the component the new position will be stored using save_component_positions
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
        save_component_positions(self)

    def delete_connection(self, key):
        """
        This function deletes the currently selected connection
        """

        # close the opened dialog
        self.dialog.dismiss

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
        initialize_visualization(self)

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

        # search name in flow dict
        for flowtype in self.blueprint.flowtypes.values():
            if flowtype.name == given_name:
                return flowtype.key

        # search for name in unit dict
        for unit in self.blueprint.units.values():
            if unit.name == given_name:
                return unit.key

        return None

    def initiate_asset_selection(self, key):
        # was the calling asset already selected?-> do nothing
        if not self.selected_asset == None and self.selected_asset["key"] == key:
            return

        # -> no unsaved changes? -> change asset
        elif not self.unsaved_changes_on_asset:
            self.change_selected_asset(key)

    def initiate_new_connection(self, *args):
        print("NEW CONNECTION BUTTON PRESSED")
        self.connection_edit_mode = True
        Window.bind(mouse_pos=lambda _, pos: update_visualization(self, mouse_pos=pos))

        self.root.ids["new_connection"].text = "Cancel"
        self.root.ids["new_connection"].icon = "cancel"
        self.root.ids["new_connection"].unbind(on_release=self.initiate_new_connection)
        self.root.ids["new_connection"].bind(on_release=self.abort_new_connection)

    def set_unsaved_changes_on_asset(self, boolean):
        self.unsaved_changes_on_asset = boolean
