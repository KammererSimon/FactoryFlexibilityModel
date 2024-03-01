# IMPORTS
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.list import (
    IconLeftWidgetWithoutTouch,
    OneLineIconListItem,
    TwoLineIconListItem,
)
from kivymd.uix.selectioncontrol import MDCheckbox

from factory_flexibility_model.ui.gui_components.layout_component_configuration.dialog_converter_ratios.dialog_converter_ratios import (
    show_converter_ratio_dialog,
)
from factory_flexibility_model.ui.gui_components.layout_component_configuration.dialog_parameter_configuration.dialog_parameter_configuration import (
    show_parameter_config_dialog,
)
from factory_flexibility_model.ui.utility.io.import_scheduler_demands import (
    import_scheduler_demands,
)


# CLASSES
class LayoutComponentDefinition(BoxLayout):
    pass


class LayoutComponentConfiguration(BoxLayout):
    pass


class ParameterConfigItem(TwoLineIconListItem):
    parameter = StringProperty()
    value_description = StringProperty()
    unit = StringProperty()
    unit_type = StringProperty()


class ParameterCheckboxItem(OneLineIconListItem):
    parameter = StringProperty()
    value_description = StringProperty()
    unit = StringProperty()


# FUNCTIONS


def set_boolean_parameter(app, status, parameter_key):
    """This function is used to directly set the values of boolean component parameters. The user can directly specify them using the checkbox in the listitem of the parameter and no additional input window is required as for all the other parameters.
    The function simply checks, if the active value of the checkbox clicked is true or false and then writes a 1 or 0 into the parameters-dict

    :param app: Pointer to the main factory_GUIApp-Object
    :param status: [Boolean] State of the activated checkbox
    :param Parameter_key: Key of the component parameter that the current configuration is made for
    """

    if status:
        app.session_data["scenarios"][app.selected_scenario][app.selected_asset["key"]][
            parameter_key
        ] = {
            "type": "boolean",
            "value": True,
        }
    else:
        app.session_data["scenarios"][app.selected_scenario][app.selected_asset["key"]][
            parameter_key
        ] = {
            "type": "boolean",
            "value": False,
        }

    update_component_configuration_tab(app)


def update_component_configuration_tab(app):
    """
    This function updates the config tab to display the values for the asset currently selected within the session.
    It shows the correct screen in the tab and set the configuration of all widgets according to the specifications in the blueprint

    :param app: Pointer to the main factory_GUIApp-Object
    """

    # if no asset is selected: show the standard screen and stop
    if app.selected_asset is None:
        app.root.ids.asset_config_screens.current = "flowtype_list"
        return

    # otherwise get the information on the current component and show it...
    asset_key = app.selected_asset["key"]
    asset_type = app.selected_asset["type"]

    # switch to the correct screen of the component tab
    app.root.ids.asset_config_screens.current = "component_config"
    # clear the tab from all existing widgets
    app.root.ids.screen_component_config_top.clear_widgets()
    app.root.ids.screen_component_config_bottom.clear_widgets()

    # CREATE LAYOUT FOR GENERAL DEFINITION
    layout_definition = LayoutComponentDefinition()
    # Update name label
    layout_definition.ids.label_component_name.text = app.selected_asset["name"]
    # update component icon
    layout_definition.ids.image_component_icon.source = app.selected_asset["GUI"][
        "icon"
    ]
    # update info label
    layout_definition.ids.label_info.text = (
        f"{app.selected_asset['flowtype'].name} {app.selected_asset['type']}"
    )
    # update description textfield
    layout_definition.ids.textfield_description.text = app.selected_asset["description"]
    # add layout to the tab
    app.root.ids.screen_component_config_top.add_widget(layout_definition)

    # stop here if the component is a pool
    if asset_type == "pool":
        return

    # CREATE LAYOUT FOR CONFIGURATION
    layout_config = LayoutComponentConfiguration()
    # update parameter list items
    try:
        parameters = app.session_data["scenarios"][app.selected_scenario][asset_key]
    except:
        app.session_data["scenarios"][app.selected_scenario][asset_key] = {}
        parameters = {}

    # get component parameter list
    component_parameter_list = app.config["component_definitions"][asset_type][
        "parameters"
    ]

    # add required parameters
    for parameter_key, attribute_data in component_parameter_list.items():
        # specify the correct unit for the selected parameter
        if attribute_data["unit_type"] == "flowrate":
            unit = app.selected_asset["flowtype"].unit.get_unit_flowrate()
        elif attribute_data["unit_type"] == "flow":
            unit = app.selected_asset["flowtype"].unit.get_unit_flow()
        elif attribute_data["unit_type"] == "%":
            unit = "Ratio (0..1)"
        elif attribute_data["unit_type"] in ["float", "integer"]:
            unit = "Units"
        elif attribute_data["unit_type"] == "efficiency_drop":
            unit = "%/Unit"
        elif attribute_data["unit_type"] == "timesteps":
            unit = "hours"
        elif attribute_data["unit_type"] == "currency":
            unit = f"{app.blueprint.info['currency']}/{app.selected_asset['flowtype'].unit.get_unit_flow()}"
        elif attribute_data["unit_type"] == "leakage_time":
            unit = f"{app.selected_asset['flowtype'].unit.get_unit_flow()}/h"
        elif attribute_data["unit_type"] == "leakage_soc":
            unit = "%/h"
        elif attribute_data["unit_type"] == "emissions":
            unit = f"kgCO2/{app.selected_asset['flowtype'].unit.get_unit_flow()}"
        elif attribute_data["unit_type"] == "capacity_charge_primary_flow":
            if (
                "primary_flow" in app.selected_asset["GUI"].keys()
                and app.selected_asset["GUI"]["primary_flow"] is not None
            ):
                flowtype = app.blueprint.components[
                    app.selected_asset["GUI"]["primary_flow"]
                ]["flowtype"]
                unit = f"{app.blueprint.info['currency']} per {flowtype.unit.get_unit_flowrate()} conversion capacity"
            else:
                unit = f"{app.blueprint.info['currency']}/?/a"
        elif attribute_data["unit_type"] == "capacity_charge_flowrate":
            unit = f"{app.blueprint.info['currency']} per {app.selected_asset['flowtype'].unit.get_unit_flowrate()} peak"
        elif attribute_data["unit_type"] == "capacity_charge_flow":
            unit = f"{app.blueprint.info['currency']} per {app.selected_asset['flowtype'].unit.get_unit_flow()} capacity"
        elif attribute_data["unit_type"] == "flowrate_primary":
            if (
                "primary_flow" in app.selected_asset["GUI"].keys()
                and app.selected_asset["GUI"]["primary_flow"] is not None
            ):
                flowtype = app.blueprint.components[
                    app.selected_asset["GUI"]["primary_flow"]
                ]["flowtype"]
                unit = f"{flowtype.unit.get_unit_flowrate()} {flowtype.name}"
            else:
                unit = ""
        elif attribute_data["unit_type"] == "ramping":
            if (
                "primary_flow" in app.selected_asset["GUI"].keys()
                and app.selected_asset["GUI"]["primary_flow"] is not None
            ):
                flowtype = app.blueprint.components[
                    app.selected_asset["GUI"]["primary_flow"]
                ]["flowtype"]
                unit = f"{flowtype.unit.get_unit_flowrate()} {flowtype.name} /h"
            else:
                unit = ""
        elif attribute_data["unit_type"] == "ramping_cost":
            if (
                "primary_flow" in app.selected_asset["GUI"].keys()
                and app.selected_asset["GUI"]["primary_flow"] is not None
            ):
                flowtype = app.blueprint.components[
                    app.selected_asset["GUI"]["primary_flow"]
                ]["flowtype"]
                unit = f"{app.blueprint.info['currency']}/{flowtype.unit.get_unit_flowrate()}"
            else:
                unit = ""
        elif attribute_data["unit_type"] == "thermal_capacity":
            unit = "kWh/K"
        elif attribute_data["unit_type"] == "thermal_resistance":
            unit = "K/kW"
        else:
            unit = ""

        list_icon = IconLeftWidgetWithoutTouch(id="icon", icon="help")
        list_item = ParameterConfigItem(
            list_icon,
            id=f"attribute_{parameter_key}",
            text=attribute_data["text"],
            secondary_text="Not Specified",
            unit=unit,
            unit_type=attribute_data["unit_type"],
        )
        list_item.parameter = parameter_key
        list_item.value_description = attribute_data["description"]

        # initialize visuals
        list_item.secondary_text = "Not Specified"
        list_icon.icon = "help"
        list_icon.theme_text_color = "Custom"
        list_icon.text_color = [0.7, 0.7, 0.7, 1]
        list_item.theme_text_color = "Custom"
        list_item.text_color = [0.6, 0.6, 0.6, 1]
        list_item.font_style = "Subtitle1"
        list_item.secondary_theme_text_color = "Custom"
        list_item.secondary_text_color = [0.8, 0.8, 0.8, 1]

        # highlight list item if the parameter is specified
        if parameter_key in parameters.keys() and len(parameters[parameter_key]) > 0:
            list_icon.text_color = app.config["main_color"].rgba
            list_item.text_color = app.config["main_color"].rgba
            list_item.secondary_text_color = app.config["main_color"].rgba
            list_item.font_style = "H6"

            # handle special cases of demands
            if parameter_key == "demands":
                # write the length of the current demand list into the info section of the parameter list element
                list_item.secondary_text = f"List of {len(parameters[parameter_key]['value'][0])} individual demands"
                list_icon.icon = "ray-start-arrow"

            # handle special cases of boolean attributes
            elif parameter_key in ["direct_throughput"]:
                pass
            # handle attributes with static values or timeseries:
            else:
                value = parameters[parameter_key]
                # handle static values
                if value["type"] == "static":
                    list_item.secondary_text = (
                        f"{round(float(value['value']),2)} {unit}"
                    )
                    list_icon.icon = "ray-start-arrow"
                # handle timeseries
                else:
                    list_item.secondary_text = f"Timeseries: {value['key']}"
                    list_icon.icon = "chart-line"

        # handle special cases where different functions than the standard data input form have to be used
        if parameter_key == "demands":
            # link excel-import script for scheduler demands
            list_item.bind(on_release=lambda x: import_scheduler_demands(app))
        elif parameter_key == "ratios":
            # link converter_ratio_window for converter ratios
            list_item.bind(on_release=lambda x: show_converter_ratio_dialog(app))
            list_icon.icon = "cog"
            list_item.secondary_text = "Show Conversion Ratio Definition"
            list_icon.text_color = app.config["main_color"].rgba
            list_item.text_color = app.config["main_color"].rgba
            list_item.secondary_text_color = app.config["main_color"].rgba
            list_item.font_style = "H6"
        elif parameter_key in ["direct_throughput"]:
            # exception for the direct throughput parameter of storages.
            # give the list the active colors
            list_icon.icon = "fast-forward"
            list_icon.text_color = app.config["main_color"].rgba
            list_item.text_color = app.config["main_color"].rgba
            list_item.secondary_text_color = app.config["main_color"].rgba
            list_item.font_style = "H6"
            # create a checkbox
            checkbox = MDCheckbox()
            checkbox.pos_hint = {"center_x": 0.8}

            try:
                # set the checkbox as checked or empty as defined in the parameters dict
                if app.session_data["scenarios"][app.selected_scenario][
                    app.selected_asset["key"]
                ][parameter_key]["value"]:
                    list_item.secondary_text = "Allowed"
                    checkbox.active = True
                else:
                    list_item.secondary_text = "Blocked"
                    checkbox.active = False
            except:
                # if the component has not been edited before: initialize the boolean value as false
                app.session_data["scenarios"][app.selected_scenario][asset_key][
                    parameter_key
                ] = {"type": "boolean", "value": False}

                list_item.secondary_text = "Blocked"
                checkbox.active = False

            checkbox.bind(
                active=lambda x, status=checkbox, parameter_key=parameter_key: set_boolean_parameter(
                    app, status, parameter_key
                )
            )
            list_item.add_widget(checkbox)

        else:
            # if none of the exceptions applies: bind the standard parameter definition window
            list_item.bind(
                on_release=lambda x, item=list_item: show_parameter_config_dialog(
                    app, item
                )
            )
        layout_config.ids.list_attributes.add_widget(list_item)

    # add parameter definitions to the layout
    app.root.ids.screen_component_config_bottom.add_widget(layout_config)

    # since the asset just got updated there are no unsaved changes anymore
    app.unsaved_changes_on_asset = False
