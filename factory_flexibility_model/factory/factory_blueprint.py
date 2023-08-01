# FACTORY-BLUEPRINT
# This file describes a class, which can be used to store all the information needed to create a factory-object.
# The class is used as an intermediate step for factory definition and imports

# IMPORT 3RD PARTY PACKAGES
from collections import defaultdict


class factory_blueprint:
    def __init__(self):
        self.version = 20221201  # script version
        self.timefactor = 1  # timefactor of the factory. See documentation for details
        self.GUI_config = {
            "display_scaling_factor": 1
        }  # sets the size of displayed icons within the preview of the factory in the gui
        self.components = {}  # dict with all components of the factory
        self.connections = defaultdict(lambda: None)  # dict of connections
        self.flows = defaultdict(lambda: None)  # list of flows
        self.info = {
            "name": "Undefined",  # Standard Information, equivalent to factory-object initialization
            "description": "Undefined",
            "max_timesteps": 8760,
            "enable_slacks": False,
            "enable_log": False,
        }

    def create_test_blueprint(self):
        self.info["enable_log"] = True
        self.flows["electricity"] = defaultdict(lambda: "")
        self.flows["electricity"].update(
            {
                "name": "Electricity",
                "key": "electricity",
                "type": "energy",
                "unit_energy": "kWh",
                "unit_power": "kW",
                "conversion_factor": 1,
                "color": [0.44, 0.676, 0.277, 1],
            }
        )

        self.flows["darkenergy"] = defaultdict(lambda: "")
        self.flows["darkenergy"].update(
            {
                "name": "Dark Energy",
                "key": "darkenergy",
                "type": "energy",
                "unit_energy": "kWh",
                "unit_power": "kW",
                "conversion_factor": 1,
                "color": [0, 0, 0, 1],
            }
        )

        self.components["grid_electricity"] = defaultdict(lambda: "")
        self.components["grid_electricity"].update(
            {
                "name": "Grid Electricity",
                "key": "grid_electricity",
                "type": "source",
                "flow": "electricity",
                "cost": "5",
                "icon": "Assets\\sources\\source_powerpole.png",
                "position_x": 0.1,
                "position_y": 0.2,
            }
        )

        self.components["e_solar"] = defaultdict(lambda: "")
        self.components["e_solar"].update(
            {
                "name": "Solar Panel",
                "key": "e_solar",
                "type": "source",
                "description": "Onsite generation of installed solar panels",
                "flow": "electricity",
                "cost": "0",
                "icon": "Assets\\sources\\source_solar.png",
                "position_x": 0.1,
                "position_y": 0.6,
            }
        )

        self.components["battery_storage"] = defaultdict(lambda: "")
        self.components["battery_storage"].update(
            {
                "name": "Battery Storage",
                "key": "battery_storage",
                "type": "storage",
                "description": "A 200kWh stationary lithium ion battery storage",
                "flow": "electricity",
                "icon": "Assets\\components\\component_battery.png",
                "position_x": 0.5,
                "position_y": 0.2,
            }
        )

        self.components["electricity_sales"] = defaultdict(lambda: "")
        self.components["electricity_sales"].update(
            {
                "name": "Electricity Sales",
                "key": "electricity_sales",
                "type": "sink",
                "description": "Option to sell electricity to the grid",
                "flow": "electricity",
                "revenue": "5",
                "icon": "Assets\\sinks\\sink_sales.png",
                "position_x": 0.9,
                "position_y": 0.6,
            }
        )

        self.components["electricity_demand"] = defaultdict(lambda: "")
        self.components["electricity_demand"].update(
            {
                "name": "Demand Electricity",
                "key": "electricity_demand",
                "type": "sink",
                "description": "Fixed electricity demand timeseries",
                "flow": "electricity",
                "icon": "Assets\\sinks\\sink_lightbulb.png",
                "position_x": 0.9,
                "position_y": 0.3,
            }
        )

        self.components["pool_electricity"] = defaultdict(lambda: "")
        self.components["pool_electricity"].update(
            {
                "name": "Pool Electricity",
                "key": "pool_electricity",
                "icon": "Assets\\components\\pool_frame.png",
                "type": "pool",
                "description": "electrical power equilibrium within the factory",
                "flow": "electricity",
                "position_x": 0.5,
                "position_y": 0.6,
            }
        )

        self.connections["connection_1"] = defaultdict(lambda: "")
        self.connections["connection_1"].update(
            {
                "name": "Grid Electricity -> Pool Electricity",
                "key": "connection_1",
                "from": "grid_electricity",
                "to": "pool_electricity",
                "flow": "electricity",
                "weight_source": 1,
                "weight_sink": 1,
                "to_losses": False,
            }
        )

        self.connections["connection_2"] = defaultdict(lambda: "")
        self.connections["connection_2"].update(
            {
                "name": "Solar Panel -> Pool Electricity",
                "key": "connection_2",
                "from": "e_solar",
                "to": "pool_electricity",
                "flow": "electricity",
                "weight_source": 1,
                "weight_sink": 1,
                "to_losses": False,
            }
        )

        self.connections["connection_3"] = defaultdict(lambda: "")
        self.connections["connection_3"].update(
            {
                "name": "Pool Electricity -> Electricity Sales",
                "key": "connection_3",
                "from": "pool_electricity",
                "to": "electricity_sales",
                "flow": "electricity",
                "weight_source": 1,
                "weight_sink": 1,
                "to_losses": False,
            }
        )

        self.connections["connection_4"] = defaultdict(lambda: "")
        self.connections["connection_4"].update(
            {
                "name": "Pool Electricity -> Battery Storage",
                "key": "connection_4",
                "from": "pool_electricity",
                "to": "battery_storage",
                "flow": "electricity",
                "weight_source": 1,
                "weight_sink": 1,
                "to_losses": False,
            }
        )

        self.connections["connection_0"] = defaultdict(lambda: "")
        self.connections["connection_0"].update(
            {
                "name": "Battery Storage -> Pool Electricity",
                "key": "connection_0",
                "from": "battery_storage",
                "to": "pool_electricity",
                "flow": "electricity",
                "weight_source": 1,
                "weight_sink": 1,
                "to_losses": False,
            }
        )
