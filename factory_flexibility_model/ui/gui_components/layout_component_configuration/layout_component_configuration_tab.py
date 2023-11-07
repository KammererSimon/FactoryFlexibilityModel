# IMPORTS
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivymd.uix.list import IconLeftWidgetWithoutTouch, TwoLineIconListItem
from factory_flexibility_model.ui.gui_components.layout_component_configuration.dialog_converter_ratios.dialog_converter_ratios import (
    show_converter_ratio_dialog,)
from factory_flexibility_model.ui.gui_components.layout_component_configuration.dialog_parameter_configuration.dialog_parameter_configuration import (
    show_parameter_config_dialog,)
from factory_flexibility_model.ui.utility.io.import_scheduler_demands import (
    import_scheduler_demands,)
from factory_flexibility_model.ui.utility.define_component_parameters import define_component_parameters

# CLASSES
class LayoutComponentDefinition(BoxLayout):
    pass

class LayoutComponentConfiguration(BoxLayout):
    pass

class ParameterConfigItem(TwoLineIconListItem):
    parameter = StringProperty()
    value_description = StringProperty()
    unit = StringProperty()


# FUNCTIONS
def update_component_configuration_tab(app):
    """
    This function updates the config tab to display the values for the asset currently selected within the session.
    It shows the correct screen in the tab and set the configuration of all widgets according to the specifications in the blueprint

    :param app: Pointer to the main factory_GUIApp-Object
    """

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
    parameters = app.session_data["parameters"][asset_key]

    # get component parameter list
    component_parameter_list = define_component_parameters()

    # add required parameters
    for parameter_key, attribute_data in component_parameter_list[asset_type].items():
        # specify the correct unit for the selected parameter
        if attribute_data["unit_type"] == "flowrate":
            unit = app.selected_asset["flowtype"].unit.get_unit_flowrate()
        elif attribute_data["unit_type"] == "flow":
            unit = app.selected_asset["flowtype"].unit.get_unit_flow()
        elif attribute_data["unit_type"] == "%":
            unit = "%"
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
        elif attribute_data["unit_type"] == "capacity_charge":
            unit = f"{app.blueprint.info['currency']}/{app.selected_asset['flowtype'].unit.get_unit_flowrate()}_peak"
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
        else:
            unit = ""

        list_icon = IconLeftWidgetWithoutTouch(id="icon", icon="help")
        list_item = ParameterConfigItem(
            list_icon,
            id=f"attribute_{parameter_key}",
            text=attribute_data["text"],
            secondary_text="Not Specified",
            unit=unit,
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
            list_icon.text_color = app.main_color.rgba
            list_item.text_color = app.main_color.rgba
            list_item.secondary_text_color = app.main_color.rgba
            list_item.font_style = "H6"

            if parameter_key == "demands":
                list_item.secondary_text = f"{len(parameters[parameter_key][0]['value'][0])} individual demands specified"
                list_icon.icon = "ray-start-arrow"

            elif len(parameters[parameter_key]) == 1:
                value = parameters[parameter_key][next(iter(parameters[parameter_key]))]
                if value["type"] == "static":
                    list_item.secondary_text = (
                        f"{round(float(value['value']),2)} {unit}"
                    )
                    list_icon.icon = "ray-start-arrow"
                else:
                    list_item.secondary_text = f"Timeseries: {value['value']}"
                    list_icon.icon = "chart-line"
            elif len(parameters[parameter_key]) > 1:
                list_item.secondary_text = (
                    f"{len(parameters[parameter_key])} Variations Specified"
                )
                list_icon.icon = "multicast"

        if parameter_key == "demands":
            list_item.bind(on_release=lambda x: import_scheduler_demands(app))
        elif parameter_key == "ratios":
            list_item.bind(on_release=lambda x: show_converter_ratio_dialog(app))
            list_icon.icon = "cog"
            list_item.secondary_text = "Show Conversion Ratio Definition"
            list_icon.text_color = app.main_color.rgba
            list_item.text_color = app.main_color.rgba
            list_item.secondary_text_color = app.main_color.rgba
            list_item.font_style = "H6"
        else:
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

