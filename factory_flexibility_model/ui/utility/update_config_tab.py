from kivy.properties import StringProperty
from kivymd.uix.list import IconLeftWidgetWithoutTouch, TwoLineIconListItem

from factory_flexibility_model.ui.dialogs.dialog_parameter_config import (
    show_parameter_config_dialog,
)
from factory_flexibility_model.ui.layouts.component_config_tab import (
    layout_component_configuration,
    layout_component_definition,
    layout_converter_ratios,
)
from factory_flexibility_model.ui.utility.import_scheduler_demands import (
    import_scheduler_demands,
)
from factory_flexibility_model.ui.dialogs.dialog_converter_ratios import show_converter_ratio_dialog
# define list of attributes to be considered for the different component types
converter_parameters = {
    "ratios": {
        "text": "Inputs/Outputs",
        "description": "",
        "unit_type": ""
    },
    "power_max": {
        "text": "Maximum Operating Point",
        "description": "Maximum Conversion Rate per Timestep",
        "unit_type": "flowrate",
    },
    "power_min": {
        "text": "Minimum Operating Point",
        "description": "Minimum Conversion Rate per Timestep",
        "unit_type": "flowrate",
    },
    "availabiity": {
        "text": "Availability",
        "description": "Availability of Pmax",
        "unit_type": "%",
    },
    "max_pos_ramp_power": {
        "text": "Positive Ramping",
        "description": "Maximum Ramp Up",
        "unit_type": "ramping",
    },
    "max_neg_ramp_power": {
        "text": "Negative Ramping",
        "description": "Maximum Ramp Down",
        "unit_type": "ramping",
    },
    "eta_max": {
        "text": "Best Efficiency",
        "description": "Maximum Efficiency at nominal operating Point",
        "unit_type": "%",
    },
    "power_nominal": {
        "text": "Nominal Operating Point",
        "description": "Operating Point of Max Efficiency",
        "unit_type": "flowrate",
    },
    "delta_eta_high": {
        "text": "Upper Efficiency Drop",
        "description": "Rate of efficiency drop when exceeding nominal operating point",
        "unit_type": "efficiency_drop",
    },
    "delta_eta_low": {
        "text": "Lower Efficiency Drop",
        "description": "Rate of efficiency drop when operating below nominal operating point",
        "unit_type": "efficiency_drop",
    },
}
deadtime_parameters = {
    "delay": {
        "text": "Delay",
        "description": "Delay Number of Timesteps",
        "unit_type": "timesteps",
    }
}
schedule_parameters = {
    "power_max": {
        "text": "Max Throughput",
        "description": "Maximum Total Flowrate",
        "unit_type": "flowrate",
    },
    "demands": {
        "text": "Demands",
        "description": "List of individual Demands",
        "unit_type": "integer",
    },
}
sink_parameters = {
    "power_max": {
        "text": "Maximum Input",
        "description": "Maximum Input Flowrate",
        "unit_type": "flowrate",
    },
    "power_min": {
        "text": "Minimum Input",
        "description": "Minimum Input Flowrate",
        "unit_type": "flowrate",
    },
    "demand": {
        "text": "Demand",
        "description": "Endogenous given Demand",
        "unit_type": "flowrate",
    },
    "cost": {
        "text": "Cost",
        "description": "Cost per Unit of Utilization",
        "unit_type": "currency",
    },
    "revenue": {
        "text": "Revenue",
        "description": "Revenue per Unit of Utilization",
        "unit_type": "currency",
    },
    "co2_emission_per_unit": {
        "text": "Emissions Caused",
        "description": "Caused Emissions",
        "unit_type": "emissions",
    },
    "co2_refund_per_unit": {
        "text": "Emissions Saved",
        "description": "Saved Emissions]",
        "unit_type": "emissions",
    },
}
source_parameters = {
    "power_max": {
        "text": "Maximum Output",
        "description": "Maximum Output Flowrate",
        "unit_type": "flowrate",
    },
    "power_min": {
        "text": "Minimum Output",
        "description": "Minimum Output Flowrate",
        "unit_type": "flowrate",
    },
    "determined_power": {
        "text": "Fixed Output",
        "description": "Endogenous given Input Volume",
        "unit_type": "flowrate",
    },
    "availability": {
        "text": "Availability",
        "description": "Ratio of Maximum Output that is available at any time",
        "unit_type": "%",
    },
    "cost": {
        "text": "Cost",
        "description": "Cost per Unit of Utilization",
        "unit_type": "currency",
    },
    "capacity_charge": {
        "text": "Capacity Charge",
        "description": "Fixed price charged per maximum utilized flowrate",
        "unit_type": "capacity_charge",
    },
    "co2_emission_per_unit": {
        "text": "Emissions Caused",
        "description": "Caused Emissions",
        "unit_type": "emissions",
    },
}
storage_parameters = {
    "efficiency": {
        "text": "Base Efficiency",
        "description": "Efficiency at nominal operation point",
        "unit_type": "%",
    },
    "capacity": {
        "text": "Capacity",
        "description": "Storage Capacity",
        "unit_type": "flow",
    },
    "power_max_charge": {
        "text": "Max Charging Power",
        "description": "Max Charging Power",
        "unit_type": "flowrate",
    },
    "power_max_discharge": {
        "text": "Max Discharging Power",
        "description": "Max Discharging Power",
        "unit_type": "flowrate",
    },
    "soc_start": {
        "text": "SOC Start",
        "description": "Initial state of Charge",
        "unit_type": "%",
    },
    "leakage_time": {
        "text": "Absolute Leakage",
        "description": "Absolute Leakage over Time",
        "unit_type": "leakage_time",
    },
    "leakage_soc": {
        "text": "Relative Leakage",
        "description": "Relative Leakage over Time",
        "unit_type": "leakage_soc",
    },
}
thermalsystem_parameters = {
    "temperature_ambient": {
        "text": "Ambient Temperature",
        "description": "Temperature Outside of the System",
        "unit_type": "temperature",
    },
    "temperature_max": {
        "text": "Maximum Temperature",
        "description": "Upper Boundary for Valid Internal Temperature",
        "unit_type": "temperature",
    },
    "temperature_min": {
        "text": "Minimum Temperature",
        "description": "Lower Boundary for Valid Internal Temperature",
        "unit_type": "temperature",
    },
    "R": {
        "text": "Thermal Resistance",
        "description": "Energy Loss Factor",
        "unit_type": "float",
    },
    "C": {
        "text": "thermal Capacity",
        "description": "Heat Capacity",
        "unit_type": "float",
    },
}

component_parameter_list = {
    "converter": converter_parameters,
    "deadtime": deadtime_parameters,
    "schedule": schedule_parameters,
    "sink": sink_parameters,
    "source": source_parameters,
    "storage": storage_parameters,
    "thermalsystem": thermalsystem_parameters,
}

# CLASSES
class ParameterConfigItem(TwoLineIconListItem):
    parameter = StringProperty()
    value_description = StringProperty()
    unit = StringProperty()


# FUNCTIONS
def update_config_tab(app):
    """
    This function updates the config tab to display the values for the asset currently selected within the session.
    It shows the correct screen in the tab and set the configuration of all widgets according to the specifications in the blueprint
    :param app: pointer to the current app instance
    """

    asset_key = app.selected_asset["key"]
    asset_type = app.selected_asset["type"]

    # switch to the correct screen of the component tab
    app.root.ids.asset_config_screens.current = "component_config"
    # clear the tab from all existing widgets
    app.root.ids.screen_component_config_top.clear_widgets()
    app.root.ids.screen_component_config_bottom.clear_widgets()

    # CREATE LAYOUT FOR GENERAL DEFINITION
    layout_definition = layout_component_definition()
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
    layout_config = layout_component_configuration()
    # update parameter list items
    parameters = app.session_data["parameters"][asset_key]

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
        elif attribute_data["unit_type"] == "ramping":
            unit = f"{app.selected_asset['flowtype'].unit.get_unit_flowrate()}/h"
        elif attribute_data["unit_type"] == "currency":
            unit = app.blueprint.info["currency"]
        elif attribute_data["unit_type"] == "leakage_time":
            unit = f"{app.selected_asset['flowtype'].unit.get_unit_flow()}/h"
        elif attribute_data["unit_type"] == "leakage_soc":
            unit = "%/h"
        elif attribute_data["unit_type"] == "emissions":
            unit = f"kgCO2/{app.selected_asset['flowtype'].unit.get_unit_flow()}"
        elif attribute_data["unit_type"] == "capacity_charge":
            unit = f"{app.blueprint.info['currency']}/{app.selected_asset['flowtype'].unit.get_unit_flowrate()}_peak"
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
                    list_item.secondary_text = f"{value['value']} {unit}"
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
