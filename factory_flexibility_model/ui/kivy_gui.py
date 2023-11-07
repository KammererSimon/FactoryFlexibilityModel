# IMPORTS

from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.factory.Flowtype as ft
import factory_flexibility_model.ui.utility.flowtype_determination as fd
from factory_flexibility_model.ui.gui_components.dialog_delete_component.dialog_delete_component import (
    show_component_deletion_dialog,
)
from factory_flexibility_model.ui.gui_components.import_gui_components import (
    import_gui_components,
)
from factory_flexibility_model.ui.gui_components.info_popup.info_popup import (
    show_info_popup,
)
from factory_flexibility_model.ui.gui_components.layout_canvas.drag_label.draglabel import (
    DragLabel,
)
from factory_flexibility_model.ui.gui_components.layout_canvas.factory_visualisation import (
    initialize_visualization,
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
from factory_flexibility_model.ui.utility.custom_widget_classes import *
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
            show_info_popup(
                self,
                "Cannot create components before initializing or importing a session!",
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
        initialize_visualization(self)

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
        Window.unbind(mouse_pos=update_visualization(self))

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
                show_info_popup(
                    self,
                    f"There is already a connection from {origin_name} to {destination_name}!",
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
                show_info_popup(
                    self,
                    f"Cannot create this connection, because {origin_name} and {destination_name} already have different flowtypes assigned!",
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
        initialize_visualization(self)

        # set unsaved changes to true
        self.unsaved_changes_on_session = True

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
            "show_component_config_dialog_on_creation": self.config[
                "show_component_config_dialog_on_creation"
            ],
            "session_path": None,
            "parameters": {},
            "timeseries": {},
            "simulations": {},
        }

        # Style Config for GUI
        self.theme_cls.colors = self.config["color_preset"]
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # set window configuration
        Window.maximize()  # start in fullscreen
        # update the visualization when changing the window size
        Window.bind(on_resize=lambda x: resize_window(self))
        Window.bind(on_maximize=lambda x: resize_window(self))
        Window.bind(on_restore=lambda x: resize_window(self))

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

        print(self.selected_asset)

        # update the config_tab to show the selected asset
        self.update_config_tab()

        # update visualisation to highlight selected asset
        update_visualization(self)

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
        Window.bind(mouse_pos=lambda _, pos: update_visualization(self, mouse_pos=pos))

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
            show_info_popup(
                self, "The given name is already assigned within the factory!"
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
            show_info_popup(
                self, "Changes can not be stored due to invalid values remaining"
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
        initialize_visualization(self)

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
        initialize_visualization(self)

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
            show_info_popup(
                self, "The given name is already assigned within the factory!"
            )
            return

        if not (self.root.ids.textfield_deadtime_delay.value_valid):
            show_info_popup(
                self, "Changes can not be stored due to invalid values remaining"
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
        initialize_visualization(self)

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
            show_info_popup(
                self, "The given name is already assigned within the factory!"
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
        initialize_visualization(self)

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
            show_info_popup(
                self, "The given name is already assigned within the factory!"
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
            show_info_popup(
                self, "Changes can not be stored due to invalid values remaining"
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
        initialize_visualization(self)

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
            show_info_popup(
                self, "The given name is already assigned within the factory!"
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
            show_info_popup(
                self, "Changes can not be stored due to invalid values remaining"
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
        initialize_visualization(self)

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
            show_info_popup(
                self, "Changes can not be stored due to invalid values remaining"
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
        initialize_visualization(self)

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
                * self.config["display_grid_size"][0],
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
                * self.config["display_grid_size"][1],
                0,
            )

            # make sure that the new position is within the grid. If not: move tho component to the closest border
            if current_pos_x < 0:
                current_pos_x = 0
            if current_pos_x > self.config["display_grid_size"][0]:
                current_pos_x = self.config["display_grid_size"][0]
            if current_pos_y < 0:
                current_pos_y = 0
            if current_pos_y > self.config["display_grid_size"][1]:
                current_pos_y = self.config["display_grid_size"][1]

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
                    show_component_deletion_dialog(self)

                    update_visualization(self)

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
            initialize_visualization(self)

    def set_unsaved_changes_on_asset(self, boolean):
        self.unsaved_changes_on_asset = boolean

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
            self.root.ids.asset_config_screens.current = "flowtype_list"
        else:
            # call update function
            update_component_configuration_tab(self)

    def update_connection_names(self):
        for connection in self.blueprint.connections.values():
            connection[
                "name"
            ] = f'{self.blueprint.components[connection["from"]]["name"]} -> {self.blueprint.components[connection["to"]]["name"]} '
