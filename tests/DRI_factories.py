# IMPORT 3RD PARTY PACKAGES
import numpy as np
import openpyxl
import pandas as pd

# IMPORT ENDOGENOUS COMPONENTS
from factory_flexibility_model.factory import Factory as fm
from factory_flexibility_model.simulation import scenario as sc


def create_steel_plant(data_path, plant_type, *, enable_log=None, enable_slacks=None):

    ### SIMULATION CONFIG ###
    filepath = f"{data_path}\\DRI Parameters.xlsx"
    simulation_length_timesteps = 672
    timestep_length_hours = 1

    # READ IN EXCEL FILE
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb["1 Model Inputs"]
    config = {}

    for row in ws.iter_rows(min_row=3, values_only=True):
        key = row[1]
        value = row[2]
        if key:
            config[key] = value

    timeseries = pd.read_excel(filepath, sheet_name="Timeseries")

    # CREATE SCENARIO OBJECT
    Testscenario = sc.scenario(f"Base Case")
    Testscenario.number_of_timesteps = simulation_length_timesteps
    Testscenario.timefactor = timestep_length_hours
    Testscenario.crude_steel_demand = timeseries["crude_steel_demand"][
        0:simulation_length_timesteps
    ]
    Testscenario.cost_electricity = timeseries["cost_electricity"][0:8760]

    # CREATE PLANT - FACTORY MODEL OBJECT
    Plant = fm.factory(
        enable_slacks=enable_slacks,
        timefactor=timestep_length_hours,
    )
    Plant.name = f"{plant_type}-DRI + EAF"
    Plant.max_timesteps = simulation_length_timesteps

    if plant_type == "CCS":
        # CREATE 100% NATURAL GAS + CCS LAYOUT

        # ADD FLOWTYPES
        Plant.add_flowtype(
            "CO2",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#E57373",
        )
        Plant.add_flowtype(
            "Crude Steel",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#791FA3",
        )
        Plant.add_flowtype(
            "Direct Reduced Iron",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#BA69C7",
        )
        Plant.add_flowtype(
            "Electricity",
            "energy",
            unit="MWh",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#0D47A1",
        )
        Plant.add_flowtype(
            "HBI",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9C26B0",
        )
        Plant.add_flowtype(
            "Iron Ore",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#E0BFE8",
        )
        Plant.add_flowtype(
            "Lime",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#A18780",
        )
        Plant.add_flowtype(
            "Natural Gas",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#999911",
            connection_color="#999911",
        )
        Plant.add_flowtype(
            "Oxygen",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#4CD1E0",
        )
        Plant.add_flowtype(
            "Scrap",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#555555",
        )

        # ADD SOURCES
        Plant.add_component("Source Iron Ore", "source", flowtype="Iron Ore")
        Plant.add_component("ambient_gains", "source", flowtype="heat")
        Plant.add_component("Source Electricity", "source", flowtype="Electricity")
        Plant.add_component("Source Scrap", "source", flowtype="Scrap")
        Plant.add_component("Source Lime", "source", flowtype="Lime")
        Plant.add_component("Source Oxygen", "source", flowtype="Oxygen")
        Plant.add_component("Source Natural Gas", "source", flowtype="Natural Gas")

        # ADD SINKS
        Plant.add_component("losses_energy", "sink", flowtype="energy_losses")
        Plant.add_component("losses_material", "sink", flowtype="material_losses")
        Plant.add_component("CO2 Emissions", "sink", flowtype="CO2")
        Plant.add_component("CO2 Sink", "sink", flowtype="CO2")
        Plant.add_component("Crude Steel Output", "sink", flowtype="Crude Steel")
        Plant.add_component("DRI Slack", "sink", flowtype="Direct Reduced Iron")

        # ADD STORAGES
        Plant.add_component("Crude Steel Storage", "storage", flowtype="Crude Steel")
        Plant.add_component("HBI Storage", "storage", flowtype="HBI")

        # ADD POOLS
        Plant.add_component("Pool DRI", "pool", flowtype="Direct Reduced Iron")
        Plant.add_component("Pool Electricity", "pool", flowtype="Electricity")
        Plant.add_component("Pool CO2", "pool", flowtype="CO2")

        # ADD CONVERTERS
        Plant.add_component("DRI", "converter")
        Plant.add_component("CCS", "converter")
        Plant.add_component("EAF", "converter")
        Plant.add_component("DRI Compactor", "converter")
        Plant.add_component("HBI Preheater", "converter")

        # ADD TRIGGERDEMANDS
        Plant.add_component("EAF Trigger", "triggerdemand")

        # ADD DEADTIMES
        Plant.add_component("HBI Storage Deadtime", "deadtime")
        Plant.add_component("EAF Process Time", "deadtime")

        # ADD CONNECTIONS
        Plant.add_connection("Crude Steel Storage", "Crude Steel Output")
        Plant.add_connection("Source Electricity", "Pool Electricity")

        # DRI
        Plant.add_connection("DRI", "Pool DRI", weight=1)
        Plant.add_connection(
            "Source Iron Ore", "DRI", weight=config["iron_ore_pellets_t_per_tdri"]
        )
        Plant.add_connection(
            "Pool Electricity", "DRI", weight=config["electricity_mwh_per_tdri"]
        )
        Plant.add_connection(
            "Source Natural Gas", "DRI", weight=config["natural_gas_t_per_tdri"]
        )
        Plant.add_connection("Pool DRI", "DRI Slack")
        Plant.add_connection("DRI", "Pool CO2", to_losses=True)

        # DRI Storage path
        Plant.add_connection("Pool DRI", "DRI Compactor", weight=1)
        Plant.add_connection(
            "Pool Electricity",
            "DRI Compactor",
            weight=config["hbi_compact_electricity_mwh_per_tDRI"],
        )
        Plant.add_connection(
            "Pool Electricity",
            "HBI Preheater",
            weight=config["hbi_reheat_electricity_mwh_per_tDRI"],
        )
        Plant.add_connection("DRI Compactor", "HBI Storage", weight=1, flowtype="HBI")
        Plant.add_connection("HBI Storage", "HBI Storage Deadtime", weight=1)
        Plant.add_connection("HBI Storage Deadtime", "HBI Preheater", weight=1)
        Plant.add_connection("HBI Preheater", "Pool DRI", weight=1)

        # EAF
        Plant.add_connection(
            "Pool DRI",
            "EAF",
            weight=config["dri_t_per_tls"] * (1 - config["scrap_share_per_tls"]),
        )
        Plant.add_connection("Source Lime", "EAF", weight=config["lime_t_per_tls"])
        Plant.add_connection(
            "Source Scrap",
            "EAF",
            weight=config["dri_t_per_tls"] * config["scrap_share_per_tls"],
        )
        Plant.add_connection("EAF", "EAF Trigger", weight=1, flowtype="Crude Steel")
        Plant.add_connection("EAF Process Time", "Crude Steel Storage", weight=1)
        Plant.add_connection("EAF Trigger", "EAF Process Time", weight=1)
        Plant.add_connection(
            "EAF",
            "CO2 Emissions",
            weight=config["co2_out_t_per_tls"] * (1 - config["scrap_share_per_tls"]),
        )
        Plant.add_connection("Pool Electricity", "EAF Trigger", weight=1)
        Plant.add_connection("EAF Trigger", "losses_energy")
        Plant.add_connection("Source Oxygen", "EAF", weight=config["oxygen_t_per_tls"])

        # CCS
        Plant.add_connection("Pool CO2", "CO2 Emissions")
        Plant.add_connection("Pool CO2", "CCS", weight=1)
        Plant.add_connection(
            "CCS", "CO2 Emissions", weight=1 - config["ccs_efficiency"]
        )
        Plant.add_connection("CCS", "CO2 Sink", weight=config["ccs_efficiency"])
        Plant.add_connection(
            "Pool Electricity",
            "CCS",
            weight=config["electricity_mwh_per_t_sequestered"]
            / config["ccs_efficiency"],
        )

        # SET COMPONENT OPERATING CONSTRAINTS
        Plant.set_configuration(
            "HBI Storage Deadtime", delay=config["hbi_min_storage_time"]
        )
        Plant.set_configuration(
            "DRI",
            power_min=config["dri_power_min"],
            power_max=config["dri_power_max"],
            max_pos_ramp_power=config["dri_ramp_up"],
            max_neg_ramp_power=config["dri_ramp_down"],
        )
        Plant.set_configuration("DRI Compactor", power_max=config["dri_power_max"])
        Plant.set_configuration(
            "Crude Steel Output", scenario_data={"demand": "crude_steel_demand"}
        )
        Plant.set_configuration(
            "HBI Storage",
            capacity=config["hbi_storage_size"],
            soc_start=config["hbi_storage_soc_start"],
        )
        Plant.set_configuration(
            "Crude Steel Storage",
            capacity=config["crude_storage_size"],
            soc_start=config["crude_storage_soc_start"],
        )
        eaf_load_profile_dri = np.zeros(
            int(round(config["batch_time"] * (1 / timestep_length_hours)))
        )
        eaf_load_profile_dri[0] = config["eaf_batch_size_tls"]
        eaf_load_profile_electricity = (
            np.ones(int(round(config["batch_time"] * (1 / timestep_length_hours))))
            * config["eaf_batch_size_tls"]
            * config["electricity_mwh_per_tls"]
            / config["batch_time"]
        )
        Plant.set_configuration(
            "EAF Trigger",
            max_parallel=config["eaf_entities"],
            load_profile_material=eaf_load_profile_dri,
            load_profile_energy=eaf_load_profile_electricity,
        )

        # SET COSTS
        Plant.set_configuration(
            "Source Electricity", scenario_data={"cost": "cost_electricity"}
        )
        Plant.set_configuration("Source Oxygen", cost=config["cost_oxygen_€_per_to2"])
        Plant.set_configuration(
            "Source Natural Gas", cost=config["cost_natural_gas_€_per_tng"]
        )
        Plant.set_configuration(
            "CO2 Emissions", cost=config["cost_emissions_€_per_tco2"]
        )
        Plant.set_configuration("Source Lime", cost=config["cost_lime_€_per_t"])
        Plant.set_configuration("Source Scrap", cost=config["cost_scrap_€_per_t"])
        Plant.set_configuration("Source Iron Ore", cost=config["cost_iron_ore_€_per_t"])

    elif plant_type == "Partial":
        # CREATE Partial replacement NG/H2 Layout

        # ADD FLOWTYPES
        Plant.add_flowtype(
            "Carbon",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "CO2",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Crude Steel",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Direct Reduced Iron",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            description="Mass flowtype of direct reduced iron",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Electricity",
            "energy",
            unit_flow="MWh",
            unit_flowrate="MW",
            description="Electrical energy proviced/consumed",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "HBI",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Hydrogen",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            description="Hydrogen provided / consumed",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Iron Ore",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Lime",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Natural Gas",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            description="Flow of natural gas",
            conversion_factor=1,
            color="#999911",
        )
        Plant.add_flowtype(
            "Oxygen",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            description="Mass flowtype of oxygen",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Scrap",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Water",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )

        # ADD SOURCES
        Plant.add_component("Source Iron Ore", "source", flowtype="Iron Ore")
        Plant.add_component("Source Hydrogen", "source", flowtype="Hydrogen")
        Plant.add_component("Source Water", "source", flowtype="Water")
        Plant.add_component("ambient_gains", "source", flowtype="heat")
        Plant.add_component("Source Electricity", "source", flowtype="Electricity")
        Plant.add_component("Source Scrap", "source", flowtype="Scrap")
        Plant.add_component("Source Lime", "source", flowtype="Lime")
        Plant.add_component("Source Carbon", "source", flowtype="Carbon")
        Plant.add_component("Source Natural Gas", "source", flowtype="Natural Gas")
        Plant.add_component("Source Oxygen", "source", flowtype="Oxygen")

        # ADD SINKS
        Plant.add_component("losses_energy", "sink", flowtype="energy_losses")
        Plant.add_component("losses_material", "sink", flowtype="material_losses")
        Plant.add_component("CO2 Emissions", "sink", flowtype="CO2")
        Plant.add_component("Crude Steel Output", "sink", flowtype="Crude Steel")
        Plant.add_component("Oxygen Sales", "sink", flowtype="Oxygen")
        Plant.add_component("DRI Slack", "sink", flowtype="Direct Reduced Iron")
        Plant.add_component("Water Sink", "sink", flowtype="Water")

        # ADD STORAGES
        Plant.add_component("Crude Steel Storage", "storage", flowtype="Crude Steel")
        Plant.add_component("Hydrogen Storage", "storage", flowtype="Hydrogen")
        Plant.add_component("HBI Storage", "storage", flowtype="HBI")

        # ADD POOLS
        Plant.add_component("Pool Hydrogen", "pool", flowtype="Hydrogen")
        Plant.add_component("Pool DRI", "pool", flowtype="Direct Reduced Iron")
        Plant.add_component("Pool Electricity", "pool", flowtype="Electricity")
        Plant.add_component("Pool Oxygen", "pool", flowtype="Oxygen")
        Plant.add_component("DRI Composition", "pool", flowtype="Direct Reduced Iron")

        # ADD CONVERTERS
        Plant.add_component("H2 DRI", "converter")
        Plant.add_component("Natural Gas DRI", "converter")
        Plant.add_component("DRI Constraint", "converter")
        Plant.add_component("PEM", "converter")
        Plant.add_component("EAF", "converter")
        Plant.add_component("DRI Compactor", "converter")
        Plant.add_component("HBI Preheater", "converter")

        # ADD TRIGGERDEMANDS
        Plant.add_component("EAF Trigger", "triggerdemand")

        # ADD DEADTIMES
        Plant.add_component("HBI Storage Deadtime", "deadtime")
        Plant.add_component("EAF Process Time", "deadtime")

        # ADD CONNECTIONS
        Plant.add_connection("Crude Steel Storage", "Crude Steel Output")
        Plant.add_connection("Source Electricity", "Pool Electricity")

        # H2 DRI
        Plant.add_connection(
            "Source Iron Ore", "H2 DRI", weight=config["iron_ore_pellets_t_per_tdri"]
        )
        Plant.add_connection(
            "Pool Electricity", "H2 DRI", weight=config["electricity_mwh_per_tdri"]
        )
        Plant.add_connection(
            "Source Carbon", "H2 DRI", weight=config["carbon_h2_t_per_tdri"]
        )
        Plant.add_connection(
            "Pool Hydrogen", "H2 DRI", weight=config["h2_gas_preheat_t_per_tdri"]
        )
        Plant.add_connection("H2 DRI", "Water Sink", to_losses=True)

        # Natural Gas DRI
        Plant.add_connection(
            "Source Iron Ore",
            "Natural Gas DRI",
            weight=config["iron_ore_pellets_t_per_tdri"],
        )
        Plant.add_connection(
            "Pool Electricity",
            "Natural Gas DRI",
            weight=config["electricity_mwh_per_tdri"],
        )
        Plant.add_connection(
            "Source Natural Gas",
            "Natural Gas DRI",
            weight=config["natural_gas_t_per_tdri"],
        )
        Plant.add_connection(
            "Natural Gas DRI", "CO2 Emissions", to_losses=True
        )  # remove if possible

        # DRI Constraints
        # Plant.add_connection("Pool Electricity", "DRI Constraint", weight=0.05)
        Plant.add_connection(
            "H2 DRI", "DRI Composition", flowtype="Direct Reduced Iron", weight=1
        )
        Plant.add_connection(
            "Natural Gas DRI",
            "DRI Composition",
            flowtype="Direct Reduced Iron",
            weight=1,
        )
        Plant.add_connection(
            "DRI Composition",
            "DRI Constraint",
            flowtype="Direct Reduced Iron",
            weight=1,
        )
        Plant.add_connection("DRI Constraint", "Pool DRI", weight=1)
        Plant.add_connection("Pool DRI", "DRI Slack")  # remove if possible

        # DRI Storage path
        Plant.add_connection("Pool DRI", "DRI Compactor", weight=1)
        Plant.add_connection(
            "Pool Electricity",
            "DRI Compactor",
            weight=config["hbi_compact_electricity_mwh_per_tDRI"],
        )
        Plant.add_connection(
            "Pool Electricity",
            "HBI Preheater",
            weight=config["hbi_reheat_electricity_mwh_per_tDRI"],
        )
        Plant.add_connection("DRI Compactor", "HBI Storage", weight=1, flowtype="HBI")
        Plant.add_connection("HBI Storage", "HBI Storage Deadtime", weight=1)
        Plant.add_connection("HBI Storage Deadtime", "HBI Preheater", weight=1)
        Plant.add_connection("HBI Preheater", "Pool DRI", weight=1)

        # EAF
        Plant.add_connection(
            "Pool DRI",
            "EAF",
            weight=config["dri_t_per_tls"] * (1 - config["scrap_share_per_tls"]),
        )
        Plant.add_connection("Source Lime", "EAF", weight=config["lime_t_per_tls"])
        Plant.add_connection(
            "Source Scrap",
            "EAF",
            weight=config["dri_t_per_tls"] * config["scrap_share_per_tls"],
        )
        Plant.add_connection("EAF", "EAF Trigger", weight=1, flowtype="Crude Steel")
        Plant.add_connection("EAF Process Time", "Crude Steel Storage", weight=1)
        Plant.add_connection("EAF Trigger", "EAF Process Time", weight=1)
        Plant.add_connection(
            "EAF",
            "CO2 Emissions",
            weight=config["co2_out_t_per_tls"] * (1 - config["scrap_share_per_tls"]),
        )
        Plant.add_connection("Pool Electricity", "EAF Trigger", weight=1)
        Plant.add_connection("EAF Trigger", "losses_energy")

        # PEM / Hydrogen
        Plant.add_connection("Source Water", "PEM", weight=config["water_t_per_th2"])
        Plant.add_connection(
            "Pool Electricity", "PEM", weight=config["electricity_mwh_per_th2"]
        )
        Plant.add_connection("PEM", "Pool Hydrogen", weight=1)
        Plant.add_connection("Pool Hydrogen", "Hydrogen Storage")
        Plant.add_connection("Hydrogen Storage", "Pool Hydrogen")
        Plant.add_connection("Source Hydrogen", "Pool Hydrogen")

        # oxygen
        Plant.add_connection(
            "PEM", "Pool Oxygen", weight=config["oxygen_out_t_per_th2"]
        )
        Plant.add_connection("Pool Oxygen", "Oxygen Sales")
        Plant.add_connection("Pool Oxygen", "EAF", weight=config["oxygen_t_per_tls"])
        Plant.add_connection("Source Oxygen", "Pool Oxygen")

        # SET COMPONENT OPERATING CONSTRAINTS
        Plant.set_configuration(
            "HBI Storage Deadtime", parameters={"delay": config["hbi_min_storage_time"]}
        )
        Plant.set_configuration(
            "DRI Constraint",
            parameters={
                "power_min": config["dri_power_min"],
                "power_max": config["dri_power_max"],
                "max_pos_ramp_power": config["dri_ramp_up"],
                "max_neg_ramp_power": config["dri_ramp_down"],
            },
        )
        Plant.set_configuration(
            "Crude Steel Output",
            parameters={"scenario_data": {"demand": "crude_steel_demand"}},
        )

        Plant.set_configuration(
            "HBI Storage",
            parameters={
                "capacity": config["hbi_storage_size"],
                "soc_start": config["hbi_storage_soc_start"],
            },
        )

        Plant.set_configuration(
            "Crude Steel Storage",
            parameters={
                "capacity": config["crude_storage_size"],
                "soc_start": config["crude_storage_soc_start"],
            },
        )

        Plant.set_configuration(
            "Hydrogen Storage",
            parameters={
                "capacity": config["h2_storage_size"],
                "soc_start": config["h2_storage_soc_start"],
                "efficiency": config["h2_storage_efficiency"],
            },
        )

        Plant.set_configuration(
            "PEM", parameters={"power_max": config["electrolyzer_production_rate"]}
        )
        Plant.set_configuration(
            "DRI Compactor", parameters={"power_max": config["dri_power_max"]}
        )

        eaf_load_profile_dri = np.zeros(
            int(round(config["batch_time"] * (1 / timestep_length_hours)))
        )
        eaf_load_profile_dri[0] = config["eaf_batch_size_tls"]
        eaf_load_profile_electricity = (
            np.ones(int(round(config["batch_time"] * (1 / timestep_length_hours))))
            * config["eaf_batch_size_tls"]
            * config["electricity_mwh_per_tls"]
            / int(round(config["batch_time"] * (1 / timestep_length_hours)))
        )
        Plant.set_configuration(
            "EAF Trigger",
            parameters={
                "max_parallel": config["eaf_entities"],
                "load_profile_material": eaf_load_profile_dri,
                "load_profile_energy": eaf_load_profile_electricity,
            },
        )

        # SET COSTS
        Plant.set_configuration(
            "Source Hydrogen", parameters={"cost": config["cost_hydrogen_€_per_th2"]}
        )

        Plant.set_configuration(
            "Source Electricity",
            parameters={"scenario_data": {"cost": "cost_electricity"}},
        )

        Plant.set_configuration(
            "Source Oxygen", parameters={"cost": config["cost_oxygen_€_per_to2"]}
        )
        Plant.set_configuration(
            "Source Natural Gas",
            parameters={"cost": config["cost_natural_gas_€_per_tng"]},
        )

        Plant.set_configuration(
            "CO2 Emissions", parameters={"cost": config["cost_emissions_€_per_tco2"]}
        )

        Plant.set_configuration(
            "Source Lime", parameters={"cost": config["cost_lime_€_per_t"]}
        )
        Plant.set_configuration(
            "Source Scrap", parameters={"cost": config["cost_scrap_€_per_t"]}
        )
        Plant.set_configuration(
            "Source Iron Ore", parameters={"cost": config["cost_iron_ore_€_per_t"]}
        )
        Plant.set_configuration(
            "Oxygen Sales", parameters={"cost": config["cost_oxygen_€_per_to2"]}
        )

    elif plant_type == "Hydrogen":
        # CREATE 100% H2 Plant layout

        # ADD FLOWTYPES
        Plant.add_flowtype(
            "Carbon",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "CO2",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Crude Steel",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Direct Reduced Iron",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            description="Mass flowtype of direct reduced iron",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Electricity",
            "energy",
            unit_flow="MWh",
            unit_flowrate="MW",
            description="Electrical energy proviced/consumed",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "HBI",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Hydrogen",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            description="Hydrogen provided / consumed",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Iron Ore",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Lime",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Oxygen",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            description="Mass flowtype of oxygen",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Scrap",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )
        Plant.add_flowtype(
            "Water",
            "material",
            unit_flow="t",
            unit_flowrate="t/h",
            conversion_factor=1,
            color="#9999AA",
        )

        # ADD SOURCES
        Plant.add_component("Source Iron Ore", "source", flowtype="Iron Ore")
        Plant.add_component("Source Hydrogen", "source", flowtype="Hydrogen")
        Plant.add_component("Source Water", "source", flowtype="Water")
        Plant.add_component("ambient_gains", "source", flowtype="heat")
        Plant.add_component("Source Electricity", "source", flowtype="Electricity")
        Plant.add_component("Source Scrap", "source", flowtype="Scrap")
        Plant.add_component("Source Lime", "source", flowtype="Lime")
        Plant.add_component("Source Carbon", "source", flowtype="Carbon")

        # ADD SINKS
        Plant.add_component("losses_energy", "sink", flowtype="energy_losses")
        Plant.add_component("losses_material", "sink", flowtype="material_losses")
        Plant.add_component("CO2 Emissions", "sink", flowtype="CO2")
        Plant.add_component("Crude Steel Output", "sink", flowtype="Crude Steel")
        Plant.add_component("Oxygen Sales", "sink", flowtype="Oxygen")
        Plant.add_component("DRI Slack", "sink", flowtype="Direct Reduced Iron")
        Plant.add_component("Water Sink", "sink", flowtype="Water")

        # ADD STORAGES
        Plant.add_component("Crude Steel Storage", "storage", flowtype="Crude Steel")
        Plant.add_component("Hydrogen Storage", "storage", flowtype="Hydrogen")
        Plant.add_component("HBI Storage", "storage", flowtype="HBI")

        # ADD POOLS
        Plant.add_component("Pool Hydrogen", "pool", flowtype="Hydrogen")
        Plant.add_component("Pool DRI", "pool", flowtype="Direct Reduced Iron")
        Plant.add_component("Pool Electricity", "pool", flowtype="Electricity")
        Plant.add_component("Pool Oxygen", "pool", flowtype="Oxygen")

        # ADD CONVERTERS
        Plant.add_component("DRI", "converter")
        Plant.add_component("PEM", "converter")
        Plant.add_component("EAF", "converter")
        Plant.add_component("DRI Compactor", "converter")
        Plant.add_component("HBI Preheater", "converter")

        # ADD TRIGGERDEMANDS
        Plant.add_component("EAF Trigger", "triggerdemand")

        # ADD DEADTIMES
        Plant.add_component("HBI Storage Deadtime", "deadtime")
        Plant.add_component("EAF Process Time", "deadtime")

        # ADD CONNECTIONS
        Plant.add_connection("Crude Steel Storage", "Crude Steel Output")
        Plant.add_connection("Source Electricity", "Pool Electricity")

        # DRI
        Plant.add_connection("DRI", "Pool DRI", weight=1)
        Plant.add_connection(
            "Source Iron Ore", "DRI", weight=config["iron_ore_pellets_t_per_tdri"]
        )
        Plant.add_connection(
            "Pool Electricity",
            "DRI",
            weight=config["electricity_mwh_per_tdri"]
            + config["preheater_electricity_mwh_per_tdri"],
        )
        Plant.add_connection(
            "Pool Hydrogen", "DRI", weight=config["h2_electric_preheat_t_per_tdri"]
        )
        Plant.add_connection("Pool DRI", "DRI Slack")
        Plant.add_connection("DRI", "Water Sink", to_losses=True)

        # DRI Storage path
        Plant.add_connection("Pool DRI", "DRI Compactor", weight=1)
        Plant.add_connection(
            "Pool Electricity",
            "DRI Compactor",
            weight=config["hbi_compact_electricity_mwh_per_tDRI"],
        )
        Plant.add_connection(
            "Pool Electricity",
            "HBI Preheater",
            weight=config["hbi_reheat_electricity_mwh_per_tDRI"],
        )
        Plant.add_connection("DRI Compactor", "HBI Storage", weight=1, flowtype="HBI")
        Plant.add_connection("HBI Storage", "HBI Storage Deadtime", weight=1)
        Plant.add_connection("HBI Storage Deadtime", "HBI Preheater", weight=1)
        Plant.add_connection("HBI Preheater", "Pool DRI", weight=1)

        # EAF
        Plant.add_connection(
            "Pool DRI",
            "EAF",
            weight=config["dri_t_per_tls"] * (1 - config["scrap_share_per_tls"]),
        )
        Plant.add_connection("Source Lime", "EAF", weight=config["lime_t_per_tls"])
        Plant.add_connection(
            "Source Scrap",
            "EAF",
            weight=config["dri_t_per_tls"] * config["scrap_share_per_tls"],
        )
        Plant.add_connection("Source Carbon", "EAF", weight=config["carbon_t_per_tls"])
        Plant.add_connection("EAF", "EAF Trigger", weight=1, flowtype="Crude Steel")
        Plant.add_connection("EAF Process Time", "Crude Steel Storage", weight=1)
        Plant.add_connection("EAF Trigger", "EAF Process Time", weight=1)
        Plant.add_connection(
            "EAF",
            "CO2 Emissions",
            weight=config["co2_out_t_per_tls"] * (1 - config["scrap_share_per_tls"]),
        )
        Plant.add_connection("Pool Electricity", "EAF Trigger", weight=1)
        Plant.add_connection("EAF Trigger", "losses_energy")

        # PEM / Hydrogen
        Plant.add_connection("Source Water", "PEM", weight=config["water_t_per_th2"])
        Plant.add_connection(
            "Pool Electricity", "PEM", weight=config["electricity_mwh_per_th2"]
        )
        Plant.add_connection("PEM", "Pool Hydrogen", weight=1)
        Plant.add_connection("Pool Hydrogen", "Hydrogen Storage")
        Plant.add_connection("Hydrogen Storage", "Pool Hydrogen")
        Plant.add_connection("Source Hydrogen", "Pool Hydrogen")

        # oxygen
        Plant.add_connection(
            "PEM", "Pool Oxygen", weight=config["oxygen_out_t_per_th2"]
        )
        Plant.add_connection("Pool Oxygen", "Oxygen Sales")
        Plant.add_connection("Pool Oxygen", "EAF", weight=config["oxygen_t_per_tls"])

        # SET COMPONENT OPERATING CONSTRAINTS
        Plant.set_configuration(
            "HBI Storage Deadtime", delay=config["hbi_min_storage_time"]
        )
        Plant.set_configuration(
            "DRI",
            power_min=config["dri_power_min"],
            power_max=config["dri_power_max"],
            max_pos_ramp_power=config["dri_ramp_up"],
            max_neg_ramp_power=config["dri_ramp_down"],
        )  ###!!!
        Plant.set_configuration(
            "Crude Steel Output", scenario_data={"demand": "crude_steel_demand"}
        )
        Plant.set_configuration(
            "HBI Storage",
            capacity=config["hbi_storage_size"],
            soc_start=config["hbi_storage_soc_start"],
        )
        Plant.set_configuration(
            "Crude Steel Storage",
            capacity=config["crude_storage_size"],
            soc_start=config["crude_storage_soc_start"],
        )
        Plant.set_configuration(
            "Hydrogen Storage",
            capacity=config["h2_storage_size"],
            soc_start=config["h2_storage_soc_start"],
            efficiency=config["h2_storage_efficiency"],
        )
        Plant.set_configuration("PEM", power_max=config["electrolyzer_production_rate"])
        Plant.set_configuration("DRI Compactor", power_max=config["dri_power_max"])

        eaf_load_profile_dri = np.zeros(
            int(round(config["batch_time"] * (1 / timestep_length_hours)))
        )
        eaf_load_profile_dri[0] = config["eaf_batch_size_tls"]
        eaf_load_profile_electricity = (
            np.ones(int(round(config["batch_time"] * (1 / timestep_length_hours))))
            * config["eaf_batch_size_tls"]
            * config["electricity_mwh_per_tls"]
            / int(round(config["batch_time"] * (1 / timestep_length_hours)))
        )
        Plant.set_configuration(
            "EAF Trigger",
            max_parallel=config["eaf_entities"],
            load_profile_material=eaf_load_profile_dri,
            load_profile_energy=eaf_load_profile_electricity,
        )

        # SET COSTS
        Plant.set_configuration(
            "Source Hydrogen", cost=config["cost_hydrogen_€_per_th2"]
        )
        Plant.set_configuration(
            "Source Electricity", scenario_data={"cost": "cost_electricity"}
        )
        Plant.set_configuration(
            "CO2 Emissions", cost=config["cost_emissions_€_per_tco2"]
        )
        Plant.set_configuration("Source Lime", cost=config["cost_lime_€_per_t"])
        Plant.set_configuration("Source Scrap", cost=config["cost_scrap_€_per_t"])
        Plant.set_configuration("Source Iron Ore", cost=config["cost_iron_ore_€_per_t"])
        Plant.set_configuration("Oxygen Sales", cost=config["cost_oxygen_€_per_to2"])

    return Plant, Testscenario
