# TESTFACTORIES
# This Script is a temporary solution for the definition of factory layouts.
# By now factories can only be specified by executing the method-prompts for factory_model as a skript.
# This Skript contains multiple layouts, nested in an if-statement. Better validate routines are in the pipeline...

import numpy as np

# IMPORT 3RD PARTY PACKAGES
import pandas as pd

# IMPORT ENDOGENOUS COMPONENTS
from factory_flexibility_model.factory import factory as fm
from factory_flexibility_model.simulation import scenario as sc


# CODE START
def create_testfactory(size, data_path, **kwargs):
    # test scenario
    Testscenario = sc.scenario("Testscenario DRI")
    Testscenario.number_of_timesteps = 72
    Testscenario.timefactor = 1
    inputs = {
        "config": f"{data_path}Config.xlsx",
        "car_data": f"{data_path}Charging_data.xlsx",
        "timeseries": f"{data_path}Timeseries_collection_hour.xlsx",
        "timeseries_15min": f"{data_path}Timeseries_collection_15min.xlsx",
    }
    config = pd.read_excel(inputs["config"], sheet_name="Tabelle1")
    timeseries = pd.read_excel(inputs["timeseries"], sheet_name="Timeseries")
    timeseries_15min = pd.read_excel(inputs["timeseries_15min"], sheet_name="Tabelle1")
    car_data = pd.read_excel(inputs["car_data"], sheet_name="Tabelle1")
    Testscenario.availability = timeseries["availability"]
    Testscenario.solar_radiation = timeseries["radiation"]
    Testscenario.cost_gas = timeseries["cost_gas"]
    Testscenario.cost_electricity = timeseries["cost_electricity"]
    Testscenario.revenue_electricity = timeseries["revenue_electricity"]
    Testscenario.temperature_max = timeseries["temperature_max"]
    Testscenario.temperature_min = timeseries["temperature_min"]
    Testscenario.temperature_outside = timeseries["temperature_outside"]
    Testscenario.cost_h2 = timeseries["cost_h2"]
    Testscenario.revenue_h2 = timeseries["revenue_h2"]
    Testscenario.price_test = timeseries["price_test"]
    Testscenario.BEV_demand = np.array(
        [
            [1, 10, 100, 30],
            [3, 15, 200, 100],
            [7, 20, 100, 40],
            [11, 13, 50, 40],
            [18, 30, 300, 80],
            [40, 50, 200, 50],
            [45, 70, 350, 40],
            [50, 55, 200, 50],
            [52, 57, 100, 100],
            [55, 58, 50, 50],
        ]
    )
    Testscenario.Product_demand = np.array(
        [
            [1, 10, 1, 30],
            [3, 15, 1, 30],
            [7, 20, 1, 40],
            [11, 13, 2, 40],
            [18, 30, 1, 80],
            [40, 50, 1, 50],
            [45, 70, 3, 40],
            [50, 55, 1, 50],
            [52, 57, 2, 100],
            [55, 58, 1, 50],
        ]
    )
    Testscenario.Production_demand = np.array(
        [
            [1, 24, 200, 50],
            [25, 48, 200, 50],
            [49, 72, 200, 50],
        ]
    )
    Testscenario.ProductionDemandFixed = timeseries["production_demand"]
    Testscenario.power_max_electricity_grid = 1000

    if "enable_log" in kwargs:
        log = kwargs["enable_log"]
    else:
        log = False

    if "enable_slacks" in kwargs:
        enable_slacks = kwargs["enable_slacks"]
    else:
        enable_slacks = False

    if size == "large":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.name = "Testlayout_Large"
        Testfactory.max_timesteps = 700
        Testfactory.create_essentials()
        Testfactory.add_component("EDemand", "sink")
        Testfactory.add_component("H2Grid", "source")
        Testfactory.add_component("H2Pool", "pool", flow="hydrogen")
        Testfactory.add_component("H2Demand", "sink")
        Testfactory.add_component("Fuelcell", "converter")
        Testfactory.add_component("ESolar", "source")
        Testfactory.add_component("GGrid", "source", flow="natural_gas")
        Testfactory.add_component("GPool", "pool")
        Testfactory.add_component("HEnvironment", "source", flow="heat")
        Testfactory.add_component("HPool", "pool")
        Testfactory.add_component("Heatpump", "converter")
        Testfactory.add_component("EHeating", "converter")
        Testfactory.add_component("CHP", "converter")
        Testfactory.add_component("ESales", "sink")
        Testfactory.add_component("Electrolysis", "converter")
        Testfactory.add_component("HDemand", "thermalsystem")
        Testfactory.add_component("HSolar", "source")
        Testfactory.add_component("H2Sales", "sink")
        Testfactory.add_component("EStorage", "storage", flow="electricity")
        Testfactory.add_component("H2Storage", "storage", flow="hydrogen")
        Testfactory.add_component("BEVDemand", "schedule")
        Testfactory.add_component("MobilityDemand", "sink", flow="energy")
        Testfactory.add_component("VehicleCharging", "converter")
        Testfactory.add_component("Material1Supply", "source", flow="material")
        Testfactory.add_component("Material2Supply", "source", flow="material")
        Testfactory.add_component("ProductionStep1", "converter")
        Testfactory.add_component("ProductionStep2", "converter")
        Testfactory.add_component(
            "IntermediateProductStorage", "storage", flow="material"
        )
        Testfactory.add_component("RoomHeating", "sink", flow="heat")
        Testfactory.add_component("OrderBook", "schedule")
        Testfactory.add_component("Deliveries", "sink")

        Testfactory.add_connection(
            "ProductionStep2", "OrderBook", weight=0.7, flow="material"
        )
        Testfactory.add_connection("OrderBook", "Deliveries", flow="material")
        Testfactory.add_connection("HDemand", "RoomHeating", to_losses=True)
        Testfactory.add_connection("GPool", "CHP", weight=1, flow="natural_gas")
        Testfactory.add_connection("CHP", "EPool", weight=0.4, flow="electricity")
        Testfactory.add_connection("CHP", "HPool", weight=0.5, flow="heat")
        Testfactory.add_connection("HPool", "HDemand")
        Testfactory.add_connection("HEnvironment", "Heatpump", weight=0.7)
        Testfactory.add_connection("Heatpump", "HPool", weight=0.95, flow="heat")
        Testfactory.add_connection("Fuelcell", "HPool", weight=0.05)
        Testfactory.add_connection("EPool", "Heatpump", weight=0.3)
        Testfactory.add_connection("H2Pool", "H2Demand")
        Testfactory.add_connection("EPool", "ESales")
        Testfactory.add_connection("ESolar", "EPool")
        Testfactory.add_connection("EPool", "EDemand")
        Testfactory.add_connection("GGrid", "GPool")
        Testfactory.add_connection("H2Grid", "H2Pool")
        Testfactory.add_connection("EPool", "EHeating", weight=1)
        Testfactory.add_connection("EHeating", "HPool", weight=0.9)
        Testfactory.add_connection("H2Pool", "Fuelcell", weight=1)
        Testfactory.add_connection("Fuelcell", "EPool", weight=0.90)
        Testfactory.add_connection("EPool", "Electrolysis", weight=1)
        Testfactory.add_connection("Electrolysis", "H2Pool", weight=0.9)
        Testfactory.add_connection("HSolar", "HPool")
        Testfactory.add_connection("H2Pool", "H2Sales")
        Testfactory.add_connection("EPool", "EStorage", weigth=1)
        Testfactory.add_connection("EStorage", "EPool")
        Testfactory.add_connection("H2Storage", "H2Pool")
        Testfactory.add_connection("H2Pool", "H2Storage")
        Testfactory.add_connection("EPool", "BEVDemand")
        Testfactory.add_connection("BEVDemand", "VehicleCharging", weight=1)
        Testfactory.add_connection("VehicleCharging", "MobilityDemand", weight=0.9)
        Testfactory.add_connection("Material1Supply", "ProductionStep1", weight=1)
        Testfactory.add_connection("EPool", "ProductionStep1", weight=0.4)
        Testfactory.add_connection("Material2Supply", "ProductionStep2", weight=0.5)
        Testfactory.add_connection("EPool", "ProductionStep2", weight=0.3)
        Testfactory.add_connection("ProductionStep1", "IntermediateProductStorage")
        Testfactory.add_connection(
            "IntermediateProductStorage", "ProductionStep2", weight=0.2
        )

        if log:
            print("CONFIGURING TESTFACTORY")
        Testfactory.set_configuration("GGrid", scenario_data={"cost": "cost_gas"})
        Testfactory.set_configuration(
            "EGrid",
            scenario_data={
                "cost": "cost_electricity",
                "power_max": "power_max_electricity_grid",
            },
        )
        Testfactory.set_configuration(
            "H2Grid", power_max=1500, scenario_data={"cost": "cost_h2"}
        )
        Testfactory.set_configuration("HEnvironment", is_onsite=True, power_max=300)
        Testfactory.set_configuration(
            "HSolar",
            is_onsite=True,
            power_max=100,
            scenario_data={"availability": "solar_radiation"},
        )
        Testfactory.set_configuration(
            "ESolar",
            is_onsite=True,
            power_max=float(config["installable_pv"]),
            scenario_data={"availability": "solar_radiation"},
        )
        Testfactory.set_configuration(
            "Fuelcell",
            power_max=100,
            power_nominal=90,
            eta_max=0.97,
            delta_eta=0.01,
            visualize=True,
        )
        Testfactory.set_configuration("CHP", power_max=300)
        Testfactory.set_configuration(
            "H2Sales",
            is_onsite=False,
            power_max=20,
            scenario_data={"revenue": "revenue_h2"},
        )
        Testfactory.set_configuration("EDemand", demand=timeseries["base_demand"])
        Testfactory.set_configuration(
            "ESales",
            is_onsite=False,
            scenario_data={"revenue": "revenue_electricity"},
            power_max=75,
        )
        Testfactory.set_configuration(
            "EStorage",
            efficiency=0.9,
            capacity=300,
            power_max_charge=350,
            power_max_discharge=350,
            leakage_time=0.0012,
            leakage_SOC=0.001,
            soc_start=0.5,
        )
        Testfactory.set_configuration(
            "IntermediateProductStorage",
            efficiency=1,
            capacity=300,
            power_max_charge=300,
            power_max_discharge=300,
            soc_start=0,
        )
        Testfactory.set_configuration(
            "BEVDemand", power_max=44, scenario_data={"demands": "BEV_demand"}
        )
        Testfactory.set_configuration(
            "HDemand",
            R=0.2,
            C=20,
            temperature_start=22,
            visualize=True,
            scenario_data={
                "temperature_max": "temperature_max",
                "temperature_min": "temperature_min",
                "temperature_ambient": "temperature_outside",
            },
        )
        Testfactory.set_configuration(
            "RoomHeating", flow_description="Thermal energy losses"
        )
        Testfactory.set_configuration("H2Pool", visualize=True)
        Testfactory.set_configuration("HPool", visualize=True)
        Testfactory.set_configuration("EStorage", visualize=True)
        Testfactory.set_configuration("EPool", visualize=True)
        Testfactory.set_configuration("H2Storage", visualize=True, soc_start=0.5)
        Testfactory.set_configuration(
            "OrderBook", scenario_data={"demands": "Production_demand"}
        )
        Testfactory.set_configuration(
            "MobilityDemand", flow_description="Energy charged "
        )
        Testfactory.set_configuration(
            "Electrolysis",
            visualize=True,
            switchable=True,
            power_min=20,
            power_max=250,
            power_nominal=200,
        )

    elif size == "BEV charging":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.max_timesteps = 72
        Testfactory.create_essentials()
        Testfactory.add_component("BEVDemand", "schedule")
        Testfactory.add_component("MobilityDemand", "sink")
        Testfactory.add_component("VehicleCharging", "converter")
        Testfactory.add_connection("EPool", "BEVDemand", weight=1)
        Testfactory.add_connection("BEVDemand", "VehicleCharging", weight=1)
        Testfactory.add_connection(
            "VehicleCharging", "MobilityDemand", weight=0.95, flow="electricity"
        )

        if log:
            print("CONFIGURING TESTFACTORY")
        Testfactory.set_configuration(
            "EGrid",
            scenario_data={
                "cost": "cost_electricity",
                "power_max": "power_max_electricity_grid",
            },
        )
        Testfactory.set_configuration(
            "BEVDemand", visualize=True, scenario_data={"demands": "BEV_demand"}
        )

    elif size == "production test":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.name = "Demo Karplus"
        Testfactory.max_timesteps = 72
        Testfactory.create_essentials()

        Testfactory.add_flow(
            "Material1",
            flow_type="material",
            unit_energy="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9999AA",
            is_energy=True,
        )
        Testfactory.add_flow(
            "Material2",
            flow_type="material",
            unit_energy="kg",
            conversion_factor=1,
            component_color="#99AA99",
            connection_color="#99AA99",
            is_energy=True,
        )
        Testfactory.add_flow(
            "Product",
            flow_type="material",
            unit_energy="kg",
            conversion_factor=1,
            component_color="#99AAAA",
            connection_color="#99AAAA",
            is_energy=True,
        )
        Testfactory.add_flow(
            "IntermediateProduct",
            flow_type="material",
            unit_energy="kg",
            conversion_factor=1,
            component_color="#6666AA",
            connection_color="#6666AA",
            is_energy=True,
        )

        Testfactory.add_component("EDemand", "sink")
        Testfactory.add_component("ProductionOutput", "sink")
        Testfactory.add_component("OrderBooks", "schedule")
        Testfactory.add_component("GGrid", "source", flow="natural_gas")
        Testfactory.add_component("HPool", "pool")
        Testfactory.add_component("EHeating", "converter")
        Testfactory.add_component("GasHeating", "converter")
        Testfactory.add_component("Material1Supply", "source")
        Testfactory.add_component("Material2Supply", "source")
        Testfactory.add_component("ProductionStep1", "converter")
        Testfactory.add_component("ProductionStep2", "converter")
        Testfactory.add_component(
            "IntermediateProductStorage", "storage", flow="IntermediateProduct"
        )
        Testfactory.add_component("ProductionEnergyDemand", "sink")
        Testfactory.add_component("RoomHeating", "thermalsystem")
        Testfactory.add_component("RoomHeatDemand", "sink")
        # Testfactory.add_component("BatteryStorage", "storage", flowtype="electricity")

        # Testfactory.add_connection("BatteryStorage", "EPool")
        # Testfactory.set_configuration("BatteryStorage", capacity=100, efficiency=0.95)
        # Testfactory.add_connection("EPool", "BatteryStorage")
        Testfactory.add_connection("EPool", "ProductionStep1", weight=0.2)
        Testfactory.add_connection("HPool", "ProductionStep1", weight=0.2, flow="heat")
        Testfactory.add_connection(
            "ProductionStep1", "ProductionEnergyDemand", to_losses=True, flow="energy"
        )
        Testfactory.add_connection(
            "ProductionStep2", "ProductionEnergyDemand", to_losses=True, flow="energy"
        )
        Testfactory.add_connection(
            "Material1Supply", "ProductionStep1", weight=1, flow="Material1"
        )
        Testfactory.add_connection(
            "ProductionStep1", "IntermediateProductStorage", flow="IntermediateProduct"
        )
        Testfactory.add_connection("GasHeating", "HPool", flow="heat")
        Testfactory.add_connection("EPool", "ProductionStep2", weight=0.3)
        Testfactory.add_connection(
            "Material2Supply", "ProductionStep2", weight=0.5, flow="Material2"
        )
        Testfactory.add_connection(
            "IntermediateProductStorage",
            "ProductionStep2",
            weight=0.5,
            flow="IntermediateProduct",
        )
        Testfactory.add_connection("ProductionStep2", "OrderBooks", flow="Product")
        Testfactory.add_connection("OrderBooks", "ProductionOutput")
        Testfactory.add_connection("GGrid", "GasHeating", weight=1)
        Testfactory.add_connection("EPool", "EDemand")
        Testfactory.add_connection("EPool", "EHeating", weight=1)
        Testfactory.add_connection("EHeating", "HPool", weight=0.9)
        Testfactory.add_connection("HPool", "RoomHeating")
        Testfactory.add_connection("RoomHeating", "RoomHeatDemand", to_losses=True)

        if log:
            print("CONFIGURING TESTFACTORY")
        # Testfactory.set_configuration("ESolar", power_max=float(config["installable_pv"]), scenario_data={"availability": "solar_radiation"})
        Testfactory.set_configuration(
            "OrderBooks", scenario_data={"demands": "BEV_demand"}
        )
        Testfactory.set_configuration("GGrid", scenario_data={"cost": "cost_gas"})
        Testfactory.set_configuration(
            "EGrid",
            scenario_data={
                "cost": "cost_electricity",
                "power_max": "power_max_electricity_grid",
            },
        )
        Testfactory.set_configuration(
            "IntermediateProductStorage",
            capacity=500,
            soc_start=0,
            visualize=True,
            efficiency=1,
            leakage_SOC=0,
        )
        Testfactory.set_configuration("EDemand", demand=timeseries["base_demand"] * 0.3)
        Testfactory.set_configuration("HPool", flow_description="Heat transfer")
        Testfactory.set_configuration("EPool", flow_description="Electricity transfer")
        Testfactory.set_configuration(
            "RoomHeating",
            R=0.2,
            C=20,
            temperature_start=20,
            visualize=True,
            scenario_data={
                "temperature_max": "temperature_max",
                "temperature_min": "temperature_min",
                "temperature_ambient": "temperature_outside",
            },
        )

    elif size == "storage test":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.name = "Storage Test"
        Testfactory.max_timesteps = 72
        Testfactory.create_essentials()
        Testfactory.add_component("ESales", "sink")
        Testfactory.add_component("EStorage", "storage", flow="electricity")
        Testfactory.add_connection("EPool", "ESales")
        Testfactory.add_connection("EPool", "EStorage", weigth=1)
        Testfactory.add_connection("EStorage", "EPool")

        if log:
            print("CONFIGURING TESTFACTORY")
        Testfactory.set_configuration(
            "EGrid",
            capacity_charge=0.5,
            scenario_data={
                "cost": "cost_electricity",
                "power_max": "power_max_electricity_grid",
                "availability": "availability",
            },
        )
        Testfactory.set_configuration(
            "ESales", scenario_data={"revenue": "revenue_electricity"}
        )
        Testfactory.set_configuration(
            "EStorage",
            capacity=505,
            efficiency=0.95,
            power_max_charge=100,
            power_max_discharge=100,
            leakage_time=0.0001,
            leakage_SOC=0.00,
            soc_start=0.5,
            soc_start_determined=False,
        )

    elif size == "iteration test":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.name = "Investment Analysis Test"
        Testfactory.max_timesteps = 72
        Testfactory.create_essentials()
        Testfactory.add_component("ESales", "sink")
        Testfactory.add_component("EStorage", "storage", flow="electricity")
        Testfactory.add_component("ESolar", "source")
        Testfactory.add_component("EDemand", "sink")
        Testfactory.add_connection("EPool", "ESales")
        Testfactory.add_connection("EPool", "EStorage", weigth=1)
        Testfactory.add_connection("EStorage", "EPool")
        Testfactory.add_connection("ESolar", "EPool")
        Testfactory.add_connection("EPool", "EDemand")

        if log:
            print("CONFIGURING TESTFACTORY")
        Testfactory.set_configuration(
            "EGrid",
            scenario_data={"cost": "cost_electricity", "availability": "availability"},
            visualize=True,
        )
        Testfactory.set_configuration(
            "ESales",
            is_onsite=False,
            power_max=300,
            scenario_data={"revenue": "revenue_electricity"},
        )
        Testfactory.set_configuration(
            "EStorage",
            capacity=500,
            efficiency=0.95,
            power_max_charge=150,
            power_max_discharge=155,
            leakage_time=0.00,
            leakage_SOC=0.00,
            soc_start=0.5,
        )
        Testfactory.set_configuration(
            "ESolar", is_onsite=True, scenario_data={"availability": "solar_radiation"}
        )
        Testfactory.set_configuration("EDemand", demand=timeseries["base_demand"])

    elif size == "deadtime test":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.max_timesteps = 72
        Testfactory.create_essentials()
        Testfactory.add_component("ESales", "sink")
        Testfactory.add_component("EPool2", "pool")
        Testfactory.add_component("Deadtime", "deadtime")
        Testfactory.add_connection("EPool", "Deadtime")
        Testfactory.add_connection("Deadtime", "EPool2")
        Testfactory.add_connection("EPool2", "ESales")

        if log:
            print("CONFIGURING TESTFACTORY")
        Testfactory.set_configuration("Deadtime", delay=5)
        Testfactory.set_configuration(
            "EGrid",
            scenario_data={
                "cost": "cost_electricity",
                "power_max": "power_max_electricity_grid",
            },
        )
        Testfactory.set_configuration("ESales", scenario_data={"revenue": "price_test"})
        Testfactory.set_configuration("EPool", visualize=True)
        Testfactory.set_configuration("EPool2", visualize=True)

    elif size == "converter test":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.max_timesteps = 72
        Testfactory.create_essentials()
        Testfactory.add_component("RoomHeating", "thermalsystem")
        Testfactory.add_component("Heatpump", "converter")
        Testfactory.add_component("AmbientHeat", "source", flow="heat")
        Testfactory.add_component("GGrid", "source", flow="natural_gas")
        Testfactory.add_component("GasHeating", "converter")
        Testfactory.add_component("HeatDemand", "sink")
        Testfactory.add_connection("GGrid", "GasHeating", weight=1)
        Testfactory.add_connection("GasHeating", "RoomHeating", flow="heat")
        Testfactory.add_connection("EPool", "Heatpump", weight=0.4)
        Testfactory.add_connection("AmbientHeat", "Heatpump", weight=0.7)
        Testfactory.add_connection(
            "Heatpump", "RoomHeating", weight=1.1, flow="heat", lossy=1
        )
        Testfactory.add_connection("RoomHeating", "HeatDemand", to_losses=True)

        if log:
            print("CONFIGURING TESTFACTORY")
        Testfactory.set_configuration(
            "EGrid",
            scenario_data={
                "cost": "cost_electricity",
                "power_max": "power_max_electricity_grid",
            },
        )
        Testfactory.set_configuration(
            "RoomHeating",
            C=20,
            R=0.5,
            sustainable=True,
            temperature_max=26,
            temperature_min=20,
            temperature_start=23,
        )
        Testfactory.set_configuration(
            "Heatpump",
            power_max=100,
            power_min=0,
            power_nominal=75,
            max_pos_ramp_power=10,
            max_neg_ramp_power=10,
            delta_eta_low=0.005,
            delta_eta_high=0.01,
            eta_max=0.95,
            visualize=True,
        )
        Testfactory.set_configuration("GGrid", scenario_data={"cost": "cost_gas"})
        Testfactory.set_configuration(
            "GasHeating", max_pos_ramp_power=5, max_neg_ramp_power=5, visualize=True
        )

    elif size == "thermaldemand test":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.max_timesteps = 72
        Testfactory.create_essentials()
        Testfactory.add_component("ThermalSimulation", "thermalsystem")
        Testfactory.add_component("ElectricHeating", "converter")
        Testfactory.add_component("HeatDemand", "sink")
        Testfactory.add_connection("EPool", "ElectricHeating", weight=1, visualize=True)
        Testfactory.add_connection("ElectricHeating", "ThermalSimulation", weight=0.97)
        Testfactory.add_connection("ThermalSimulation", "HeatDemand", to_losses=True)
        Testfactory.set_configuration(
            "ThermalSimulation",
            R=0.2,
            C=20,
            temperature_max=130,
            temperature_min=20,
            temperature_start=22,
            temperature_ambient=15,
            visualize=True,
        )
        Testfactory.set_configuration(
            "EGrid",
            scenario_data={
                "cost": "cost_electricity",
                "power_max": "power_max_electricity_grid",
            },
        )

    elif size == "demo architecture":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.max_timesteps = 72
        Testfactory.add_flow(
            "Material",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9999AA",
        )
        Testfactory.add_flow(
            "Product",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#6666AA",
            connection_color="#6666AA",
        )

        # COMPONENTS
        Testfactory.create_essentials()
        Testfactory.add_component("MaterialSupply", "source", flow="Material")
        Testfactory.add_component("AmbientHeat", "source", flow="heat")
        Testfactory.add_component("VehicleCharging", "sink", flow="electricity")
        Testfactory.add_component("EDemand", "sink")
        Testfactory.add_component("Deliveries", "sink")
        Testfactory.add_component("RoomHeating", "thermalsystem")
        Testfactory.add_component("Heatpump", "converter")
        Testfactory.add_component("Production", "converter")
        Testfactory.add_component("ProductStorage", "storage", flow="Product")
        Testfactory.add_component("Battery", "storage", flow="electricity")
        Testfactory.add_component("ParkingTimes", "schedule")

        # CONNECTIONS
        Testfactory.add_connection("EPool", "Production", weight=0.5)
        Testfactory.add_connection("EPool", "EDemand")
        Testfactory.add_connection("Production", "ProductStorage", flow="Product")
        Testfactory.add_connection("EPool", "Battery")
        Testfactory.add_connection("EPool", "ParkingTimes")
        Testfactory.add_connection("ParkingTimes", "VehicleCharging")
        Testfactory.add_connection("Battery", "EPool")
        Testfactory.add_connection("MaterialSupply", "Production", weight=1)
        Testfactory.add_connection("ProductStorage", "Deliveries", flow="Product")
        Testfactory.add_connection("Heatpump", "RoomHeating")
        Testfactory.add_connection("EPool", "Heatpump", weight=0.3)
        Testfactory.add_connection("AmbientHeat", "Heatpump", weight=0.7)

        # CONFIGURATION
        Testfactory.set_configuration(
            "EGrid",
            scenario_data={
                "cost": "cost_electricity",
                "power_max": "power_max_electricity_grid",
            },
        )
        Testfactory.set_configuration(
            "ProductStorage", capacity=50, soc_start=0, visualize=True, efficiency=1
        )
        Testfactory.set_configuration(
            "Battery", capacity=100, visualize=True, efficiency=0.9, soc_start=0.3
        )
        Testfactory.set_configuration("EDemand", demand=timeseries["base_demand"] * 0)
        Testfactory.set_configuration("EPool", visualize=True)
        Testfactory.set_configuration(
            "Deliveries", demand=timeseries["production_demand"]
        )
        Testfactory.set_configuration("Production", visualize=True)
        Testfactory.set_configuration(
            "ParkingTimes", power_max=44, scenario_data={"demands": "BEV_demand"}
        )
        Testfactory.set_configuration(
            "RoomHeating",
            R=0.8,
            C=20,
            temperature_max=28,
            temperature_min=20,
            temperature_start=22,
            temperature_ambient=15,
            visualize=True,
        )

    elif size == "demo":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.max_timesteps = 72
        Testfactory.create_essentials()

    elif size == "triggerdemand test":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.name = "Triggerdemand Test"
        Testfactory.max_timesteps = 72
        Testfactory.create_essentials()
        Testfactory.add_flow(
            "Parts",
            flow_type="material",
            unit="Pieces",
            component_color="#654321",
            connection_color="#654321",
            is_energy=False,
        )
        Testfactory.add_flow(
            "Filament",
            flow_type="material",
            unit="Pieces",
            conversion_factor=1,
            component_color="#654321",
            connection_color="#654321",
        )
        Testfactory.add_component("Triggerdemand", "triggerdemand", flow="electricity")
        Testfactory.add_component("3DPrinter", "converter")
        Testfactory.add_component("FilamentFeed", "source")
        Testfactory.add_component("PartStorage", "storage", flow="Parts")
        Testfactory.add_component("PartDelivery", "sink")
        Testfactory.add_connection("3DPrinter", "PartStorage", flow="Parts")
        Testfactory.add_connection("PartStorage", "PartDelivery")
        Testfactory.add_connection("EPool", "Triggerdemand")
        Testfactory.add_connection("Triggerdemand", "3DPrinter", weight=43.5)
        Testfactory.add_connection(
            "FilamentFeed", "3DPrinter", flow="Filament", weight=1
        )

        if log:
            print("CONFIGURING TESTFACTORY")
        Testfactory.set_configuration(
            "EGrid",
            power_max=60,
            scenario_data={"cost": "cost_electricity"},
            visualize=True,
        )
        Testfactory.set_configuration("PartStorage", capacity=10, soc_start=0.2)
        Testfactory.set_configuration(
            "Triggerdemand",
            Tstart=1,
            Tend=72,
            executions=0,
            max_parallel=2,
            load_profile=[2, 2.5, 2, 10, 10.5, 10, 2, 2.5, 2],
        )
        demand = np.zeros(72)
        demand[70] = 5
        demand[24] = 2
        Testfactory.set_configuration("PartDelivery", demand=demand)

    elif size == "DRI":
        if log:
            print("BUILDING TESTFACTORY")
        Testfactory = fm.factory(enable_slacks=enable_slacks, enable_log=log)
        Testfactory.name = "H-DRI + EAF"
        Testfactory.max_timesteps = 72

        # ADD FLOWS
        Testfactory.add_flow(
            "Carbon",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9999AA",
        )
        Testfactory.add_flow(
            "CO2",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#E57373",
        )
        Testfactory.add_flow(
            "Crude Steel",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#791FA3",
        )
        Testfactory.add_flow(
            "Direct Reduced Iron",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#BA69C7",
        )
        Testfactory.add_flow(
            "Electricity",
            "energy",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#0D47A1",
        )
        Testfactory.add_flow(
            "HBI",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9C26B0",
        )
        Testfactory.add_flow(
            "Hydrogen",
            "energy",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#82C785",
        )
        Testfactory.add_flow(
            "Iron Ore",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#E0BFE8",
        )
        Testfactory.add_flow(
            "Lime",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#A18780",
        )
        Testfactory.add_flow(
            "Natural Gas",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9999AA",
        )
        Testfactory.add_flow(
            "Oxygen",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#4CD1E0",
        )
        Testfactory.add_flow(
            "Scrap",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#555555",
        )
        Testfactory.add_flow(
            "Water",
            "material",
            unit="kg",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#82D4FA",
        )

        # ADD SOURCES
        Testfactory.add_component("Source Iron Ore", "source", flow="Iron Ore")
        Testfactory.add_component("Source Hydrogen", "source", flow="Hydrogen")
        Testfactory.add_component("Source Water", "source", flow="Water")
        Testfactory.add_component("ambient_gains", "source", flow="heat")
        Testfactory.add_component("Source Electricity", "source", flow="Electricity")
        Testfactory.add_component("Source Scrap", "source", flow="Scrap")
        Testfactory.add_component("Source Lime", "source", flow="Lime")
        Testfactory.add_component("Source Carbon", "source", flow="Carbon")

        # ADD SINKS
        Testfactory.add_component("Sink Crude Steel", "sink", flow="Crude Steel")
        Testfactory.add_component("losses_energy", "sink", flow="energy_losses")
        Testfactory.add_component("losses_material", "sink", flow="material_losses")
        Testfactory.add_component("CO2 Emissions", "sink", flow="CO2")
        Testfactory.add_component("Crude Steel Output", "sink", flow="Crude Steel")
        Testfactory.add_component("Oxygen Sales", "sink", flow="Oxygen")

        # ADD STORAGES
        Testfactory.add_component("Crude Steel Storage", "storage", flow="Crude Steel")
        Testfactory.add_component("Hydrogen Storage", "storage", flow="Hydrogen")
        Testfactory.add_component("HBI Storage", "storage", flow="HBI")

        # ADD POOLS
        Testfactory.add_component("Pool Hydrogen", "pool", flow="Hydrogen")
        Testfactory.add_component("Pool DRI", "pool", flow="Direct Reduced Iron")
        Testfactory.add_component("Pool Electricity", "pool", flow="Electricity")
        Testfactory.add_component("Pool Oxygen", "pool", flow="Oxygen")

        # ADD CONVERTERS
        Testfactory.add_component("DRI", "converter")
        Testfactory.add_component("PEM", "converter")
        Testfactory.add_component("EAF", "converter")
        Testfactory.add_component("DRI Compactor", "converter")
        Testfactory.add_component("HBI Preheater", "converter")

        # ADD DEADTIMES
        Testfactory.add_component("HBI Storage Deadtime", "deadtime", delay=3)

        # ADD CONNECTIONS
        Testfactory.add_connection("Crude Steel Storage", "Crude Steel Output")
        Testfactory.add_connection("Source Electricity", "Pool Electricity")
        # DRI
        Testfactory.add_connection("DRI", "Pool DRI", weight=1)
        Testfactory.add_connection("Source Iron Ore", "DRI", weight=1)
        Testfactory.add_connection("Pool Electricity", "DRI", weight=1)
        Testfactory.add_connection("Pool Hydrogen", "DRI", weight=1)

        # DRI Storage path
        Testfactory.add_connection("Pool DRI", "DRI Compactor", weight=1)
        Testfactory.add_connection("Pool Electricity", "DRI Compactor", weight=1)
        Testfactory.add_connection("Pool Electricity", "HBI Preheater", weight=1)
        Testfactory.add_connection(
            "DRI Compactor", "HBI Storage Deadtime", weight=1, flow="HBI"
        )
        Testfactory.add_connection("HBI Storage Deadtime", "HBI Storage", weight=1)
        Testfactory.add_connection("HBI Storage", "HBI Preheater", weight=1)
        Testfactory.add_connection("HBI Preheater", "Pool DRI", weight=1)

        # EAF
        Testfactory.add_connection("Pool DRI", "EAF", weight=1)
        Testfactory.add_connection("Pool Electricity", "EAF", weight=1)
        Testfactory.add_connection("Source Lime", "EAF", weight=1)
        Testfactory.add_connection("Source Scrap", "EAF", weight=1)
        Testfactory.add_connection("Source Carbon", "EAF", weight=1)
        Testfactory.add_connection("EAF", "Crude Steel Storage", weight=1)
        Testfactory.add_connection("EAF", "CO2 Emissions", weight=1)

        # PEM / Hydrogen
        Testfactory.add_connection("Source Water", "PEM", weight=1)
        Testfactory.add_connection("Pool Electricity", "PEM", weight=1)
        Testfactory.add_connection("PEM", "Pool Hydrogen", weight=1)
        Testfactory.add_connection("Pool Hydrogen", "Hydrogen Storage")
        Testfactory.add_connection("Hydrogen Storage", "Pool Hydrogen")
        Testfactory.add_connection("Source Hydrogen", "Pool Hydrogen")

        # oxygen
        Testfactory.add_connection("PEM", "Pool Oxygen", weight=1)
        Testfactory.add_connection("Pool Oxygen", "Oxygen Sales")
        Testfactory.add_connection("Pool Oxygen", "EAF", weight=1)

        Testfactory.set_configuration("HBI Storage Deadtime", delay=3)
        Testfactory.set_configuration(
            "DRI",
            power_min=200,
            power_max=285.4,
            max_pos_ramp_power=50,
            max_neg_ramp_power=50,
        )
        Testfactory.set_configuration(
            "Crude Steel Output",
        )

    else:
        raise Exception(f"ERROR: {size} is an invalid key for the testfactory-script")

    return Testfactory, Testscenario
