# This function generates a demo object of the blueprint-class containing a simple factory layout for testing

# IMPORTS
from collections import defaultdict

from factory_flexibility_model.factory import Blueprint as bp


def create_test_blueprint():
    """
    This function generates a demo object of the blueprint-class containing a simple factory layout for testing
    :return: factory.blueprint-object
    """
    blueprint = bp.Blueprint()
    blueprint.flowtypes["electricity"] = defaultdict(lambda: "")
    blueprint.flowtypes["electricity"].update(
        {
            "name": "Electricity",
            "key": "electricity",
            "unit": "kW",
            "color": "#FF0000",
        }
    )

    blueprint.flowtypes["darkenergy"] = defaultdict(lambda: "")
    blueprint.flowtypes["darkenergy"].update(
        {
            "name": "Dark Energy",
            "key": "darkenergy",
            "unit": "kW",
            "color": "#000000",
        }
    )

    blueprint.components["grid_electricity"] = defaultdict(lambda: "")
    blueprint.components["grid_electricity"].update(
        {
            "name": "Grid Electricity",
            "key": "grid_electricity",
            "type": "source",
            "flowtype": "electricity",
            "cost": "5",
            "icon": "assets\\sources\\source_powerpole.png",
            "position_x": 0.1,
            "position_y": 0.2,
        }
    )

    blueprint.components["e_solar"] = defaultdict(lambda: "")
    blueprint.components["e_solar"].update(
        {
            "name": "Solar Panel",
            "key": "e_solar",
            "type": "source",
            "description": "Onsite generation of installed solar panels",
            "flowtype": "electricity",
            "cost": "0",
            "icon": "assets\\sources\\source_solar.png",
            "position_x": 0.1,
            "position_y": 0.6,
        }
    )

    blueprint.components["battery_storage"] = defaultdict(lambda: "")
    blueprint.components["battery_storage"].update(
        {
            "name": "Battery Storage",
            "key": "battery_storage",
            "type": "storage",
            "description": "A 200kWh stationary lithium ion battery storage",
            "flowtype": "electricity",
            "icon": "assets\\components\\component_battery.png",
            "position_x": 0.5,
            "position_y": 0.2,
        }
    )

    blueprint.components["electricity_sales"] = defaultdict(lambda: "")
    blueprint.components["electricity_sales"].update(
        {
            "name": "Electricity Sales",
            "key": "electricity_sales",
            "type": "sink",
            "description": "Option to sell electricity to the grid",
            "flowtype": "electricity",
            "revenue": "5",
            "icon": "assets\\sinks\\sink_sales.png",
            "position_x": 0.9,
            "position_y": 0.6,
        }
    )

    blueprint.components["electricity_demand"] = defaultdict(lambda: "")
    blueprint.components["electricity_demand"].update(
        {
            "name": "Demand Electricity",
            "key": "electricity_demand",
            "type": "sink",
            "description": "Fixed electricity demand timeseries",
            "flowtype": "electricity",
            "icon": "assets\\sinks\\sink_lightbulb.png",
            "position_x": 0.9,
            "position_y": 0.3,
        }
    )

    blueprint.components["pool_electricity"] = defaultdict(lambda: "")
    blueprint.components["pool_electricity"].update(
        {
            "name": "Pool Electricity",
            "key": "pool_electricity",
            "icon": "assets\\components\\pool_frame.png",
            "type": "pool",
            "description": "electrical power equilibrium within the factory",
            "flowtype": "electricity",
            "position_x": 0.5,
            "position_y": 0.6,
        }
    )

    blueprint.connections["connection_1"] = defaultdict(lambda: "")
    blueprint.connections["connection_1"].update(
        {
            "name": "Grid Electricity -> Pool Electricity",
            "key": "connection_1",
            "from": "grid_electricity",
            "to": "pool_electricity",
            "flowtype": "electricity",
            "weight_origin": 1,
            "weight_destination": 1,
            "to_losses": False,
        }
    )

    blueprint.connections["connection_2"] = defaultdict(lambda: "")
    blueprint.connections["connection_2"].update(
        {
            "name": "Solar Panel -> Pool Electricity",
            "key": "connection_2",
            "from": "e_solar",
            "to": "pool_electricity",
            "flowtype": "electricity",
            "weight_origin": 1,
            "weight_destination": 1,
            "to_losses": False,
        }
    )

    blueprint.connections["connection_3"] = defaultdict(lambda: "")
    blueprint.connections["connection_3"].update(
        {
            "name": "Pool Electricity -> Electricity Sales",
            "key": "connection_3",
            "from": "pool_electricity",
            "to": "electricity_sales",
            "flowtype": "electricity",
            "weight_origin": 1,
            "weight_destination": 1,
            "to_losses": False,
        }
    )

    blueprint.connections["connection_4"] = defaultdict(lambda: "")
    blueprint.connections["connection_4"].update(
        {
            "name": "Pool Electricity -> Battery Storage",
            "key": "connection_4",
            "from": "pool_electricity",
            "to": "battery_storage",
            "flowtype": "electricity",
            "weight_origin": 1,
            "weight_destination": 1,
            "to_losses": False,
        }
    )

    blueprint.connections["connection_0"] = defaultdict(lambda: "")
    blueprint.connections["connection_0"].update(
        {
            "name": "Battery Storage -> Pool Electricity",
            "key": "connection_0",
            "from": "battery_storage",
            "to": "pool_electricity",
            "flowtype": "electricity",
            "weight_origin": 1,
            "weight_destination": 1,
            "to_losses": False,
        }
    )

    return blueprint
