# IMPORT 3RD PARTY PACKAGES
import numpy as np
import openpyxl
import pandas as pd

# IMPORT ENDOGENOUS COMPONENTS
from factory_flexibility_model.factory import factory_model as fm
from factory_flexibility_model.simulation import scenario as sc


def create_steel_plant(data_path, plant_type, **kwargs):

    ### SIMULATION CONFIG ###
    filepath = f"{data_path}\\DRI Parameters.xlsx"
    simulation_length_timesteps = 672
    timestep_length_hours = 1
    if "enable_log" in kwargs:
        log = kwargs["enable_log"]
    else:
        log = False

    if "enable_slacks" in kwargs:
        enable_slacks = kwargs["enable_slacks"]
    else:
        enable_slacks = False

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
        enable_slacks=enable_slacks, enable_log=log, timefactor=timestep_length_hours
    )
    Plant.name = f"{plant_type}-DRI + EAF"
    Plant.max_timesteps = simulation_length_timesteps

    if plant_type == "CCS":
        # CREATE 100% NATURAL GAS + CCS LAYOUT

        # ADD FLOWS
        Plant.add_flow(
            "CO2",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#E57373",
        )
        Plant.add_flow(
            "Crude Steel",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#791FA3",
        )
        Plant.add_flow(
            "Direct Reduced Iron",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#BA69C7",
        )
        Plant.add_flow(
            "Electricity",
            "energy",
            unit="MWh",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#0D47A1",
        )
        Plant.add_flow(
            "HBI",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9C26B0",
        )
        Plant.add_flow(
            "Iron Ore",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#E0BFE8",
        )
        Plant.add_flow(
            "Lime",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#A18780",
        )
        Plant.add_flow(
            "Natural Gas",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#999911",
            connection_color="#999911",
        )
        Plant.add_flow(
            "Oxygen",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#4CD1E0",
        )
        Plant.add_flow(
            "Scrap",
            "material",
            unit="t",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#555555",
        )

        # ADD SOURCES
        Plant.add_component("Source Iron Ore", "source", flow="Iron Ore")
        Plant.add_component("ambient_gains", "source", flow="heat")
        Plant.add_component("Source Electricity", "source", flow="Electricity")
        Plant.add_component("Source Scrap", "source", flow="Scrap")
        Plant.add_component("Source Lime", "source", flow="Lime")
        Plant.add_component("Source Oxygen", "source", flow="Oxygen")
        Plant.add_component("Source Natural Gas", "source", flow="Natural Gas")

        # ADD SINKS
        Plant.add_component("losses_energy", "sink", flow="energy_losses")
        Plant.add_component("losses_material", "sink", flow="material_losses")
        Plant.add_component("CO2 Emissions", "sink", flow="CO2")
        Plant.add_component("CO2 Sink", "sink", flow="CO2")
        Plant.add_component("Crude Steel Output", "sink", flow="Crude Steel")
        Plant.add_component("DRI Slack", "sink", flow="Direct Reduced Iron")

        # ADD STORAGES
        Plant.add_component("Crude Steel Storage", "storage", flow="Crude Steel")
        Plant.add_component("HBI Storage", "storage", flow="HBI")

        # ADD POOLS
        Plant.add_component("Pool DRI", "pool", flow="Direct Reduced Iron")
        Plant.add_component("Pool Electricity", "pool", flow="Electricity")
        Plant.add_component("Pool CO2", "pool", flow="CO2")

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
        Plant.add_connection("DRI Compactor", "HBI Storage", weight=1, flow="HBI")
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
        Plant.add_connection("EAF", "EAF Trigger", weight=1, flow="Crude Steel")
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

        # ADD FLOWS
        Plant.add_flow(
            "Carbon",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9999AA",
        )
        Plant.add_flow(
            "CO2",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#E57373",
        )
        Plant.add_flow(
            "Crude Steel",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#791FA3",
        )
        Plant.add_flow(
            "Direct Reduced Iron",
            "material",
            unit_energy="t",
            unit_power="t/h",
            flow_description="Mass flow of direct reduced iron",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#BA69C7",
        )
        Plant.add_flow(
            "Electricity",
            "energy",
            unit_energy="MWh",
            unit_power="MW",
            flow_description="Electrical energy proviced/consumed",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#0D47A1",
        )
        Plant.add_flow(
            "HBI",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9C26B0",
        )
        Plant.add_flow(
            "Hydrogen",
            "material",
            unit_energy="t",
            unit_power="t/h",
            flow_description="Hydrogen provided / consumed",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#82C785",
        )
        Plant.add_flow(
            "Iron Ore",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#E0BFE8",
        )
        Plant.add_flow(
            "Lime",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#A18780",
        )
        Plant.add_flow(
            "Natural Gas",
            "material",
            unit_energy="t",
            unit_power="t/h",
            flow_description="Flow of natural gas",
            conversion_factor=1,
            component_color="#999911",
            connection_color="#999911",
        )
        Plant.add_flow(
            "Oxygen",
            "material",
            unit_energy="t",
            unit_power="t/h",
            flow_description="Mass flow of oxygen",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#4CD1E0",
        )
        Plant.add_flow(
            "Scrap",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#555555",
        )
        Plant.add_flow(
            "Water",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#82D4FA",
        )

        # ADD SOURCES
        Plant.add_component("Source Iron Ore", "source", flow="Iron Ore")
        Plant.add_component("Source Hydrogen", "source", flow="Hydrogen")
        Plant.add_component("Source Water", "source", flow="Water")
        Plant.add_component("ambient_gains", "source", flow="heat")
        Plant.add_component("Source Electricity", "source", flow="Electricity")
        Plant.add_component("Source Scrap", "source", flow="Scrap")
        Plant.add_component("Source Lime", "source", flow="Lime")
        Plant.add_component("Source Carbon", "source", flow="Carbon")
        Plant.add_component("Source Natural Gas", "source", flow="Natural Gas")
        Plant.add_component("Source Oxygen", "source", flow="Oxygen")

        # ADD SINKS
        Plant.add_component("losses_energy", "sink", flow="energy_losses")
        Plant.add_component("losses_material", "sink", flow="material_losses")
        Plant.add_component("CO2 Emissions", "sink", flow="CO2")
        Plant.add_component("Crude Steel Output", "sink", flow="Crude Steel")
        Plant.add_component("Oxygen Sales", "sink", flow="Oxygen")
        Plant.add_component("DRI Slack", "sink", flow="Direct Reduced Iron")
        Plant.add_component("Water Sink", "sink", flow="Water")

        # ADD STORAGES
        Plant.add_component("Crude Steel Storage", "storage", flow="Crude Steel")
        Plant.add_component("Hydrogen Storage", "storage", flow="Hydrogen")
        Plant.add_component("HBI Storage", "storage", flow="HBI")

        # ADD POOLS
        Plant.add_component("Pool Hydrogen", "pool", flow="Hydrogen")
        Plant.add_component("Pool DRI", "pool", flow="Direct Reduced Iron")
        Plant.add_component("Pool Electricity", "pool", flow="Electricity")
        Plant.add_component("Pool Oxygen", "pool", flow="Oxygen")
        Plant.add_component("DRI Composition", "pool", flow="Direct Reduced Iron")

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
            "H2 DRI", "DRI Composition", flow="Direct Reduced Iron", weight=1
        )
        Plant.add_connection(
            "Natural Gas DRI", "DRI Composition", flow="Direct Reduced Iron", weight=1
        )
        Plant.add_connection(
            "DRI Composition", "DRI Constraint", flow="Direct Reduced Iron", weight=1
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
        Plant.add_connection("DRI Compactor", "HBI Storage", weight=1, flow="HBI")
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
        Plant.add_connection("EAF", "EAF Trigger", weight=1, flow="Crude Steel")
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
            "HBI Storage Deadtime", delay=config["hbi_min_storage_time"]
        )
        Plant.set_configuration(
            "DRI Constraint",
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
        Plant.set_configuration("Oxygen Sales", cost=config["cost_oxygen_€_per_to2"])

    elif plant_type == "Hydrogen":
        # CREATE 100% H2 Plant layout

        # ADD FLOWS
        Plant.add_flow(
            "Carbon",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9999AA",
        )
        Plant.add_flow(
            "CO2",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#E57373",
        )
        Plant.add_flow(
            "Crude Steel",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#791FA3",
        )
        Plant.add_flow(
            "Direct Reduced Iron",
            "material",
            unit_energy="t",
            unit_power="t/h",
            flow_description="Mass flow of direct reduced iron",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#BA69C7",
        )
        Plant.add_flow(
            "Electricity",
            "energy",
            unit_energy="MWh",
            unit_power="MW",
            flow_description="Electrical energy proviced/consumed",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#0D47A1",
        )
        Plant.add_flow(
            "HBI",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#9C26B0",
        )
        Plant.add_flow(
            "Hydrogen",
            "material",
            unit_energy="t",
            unit_power="t/h",
            flow_description="Hydrogen provided / consumed",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#82C785",
        )
        Plant.add_flow(
            "Iron Ore",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#E0BFE8",
        )
        Plant.add_flow(
            "Lime",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#A18780",
        )
        Plant.add_flow(
            "Oxygen",
            "material",
            unit_energy="t",
            unit_power="t/h",
            flow_description="Mass flow of oxygen",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#4CD1E0",
        )
        Plant.add_flow(
            "Scrap",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#555555",
        )
        Plant.add_flow(
            "Water",
            "material",
            unit_energy="t",
            unit_power="t/h",
            conversion_factor=1,
            component_color="#9999AA",
            connection_color="#82D4FA",
        )

        # ADD SOURCES
        Plant.add_component("Source Iron Ore", "source", flow="Iron Ore")
        Plant.add_component("Source Hydrogen", "source", flow="Hydrogen")
        Plant.add_component("Source Water", "source", flow="Water")
        Plant.add_component("ambient_gains", "source", flow="heat")
        Plant.add_component("Source Electricity", "source", flow="Electricity")
        Plant.add_component("Source Scrap", "source", flow="Scrap")
        Plant.add_component("Source Lime", "source", flow="Lime")
        Plant.add_component("Source Carbon", "source", flow="Carbon")

        # ADD SINKS
        Plant.add_component("losses_energy", "sink", flow="energy_losses")
        Plant.add_component("losses_material", "sink", flow="material_losses")
        Plant.add_component("CO2 Emissions", "sink", flow="CO2")
        Plant.add_component("Crude Steel Output", "sink", flow="Crude Steel")
        Plant.add_component("Oxygen Sales", "sink", flow="Oxygen")
        Plant.add_component("DRI Slack", "sink", flow="Direct Reduced Iron")
        Plant.add_component("Water Sink", "sink", flow="Water")

        # ADD STORAGES
        Plant.add_component("Crude Steel Storage", "storage", flow="Crude Steel")
        Plant.add_component("Hydrogen Storage", "storage", flow="Hydrogen")
        Plant.add_component("HBI Storage", "storage", flow="HBI")

        # ADD POOLS
        Plant.add_component("Pool Hydrogen", "pool", flow="Hydrogen")
        Plant.add_component("Pool DRI", "pool", flow="Direct Reduced Iron")
        Plant.add_component("Pool Electricity", "pool", flow="Electricity")
        Plant.add_component("Pool Oxygen", "pool", flow="Oxygen")

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
        Plant.add_connection("DRI Compactor", "HBI Storage", weight=1, flow="HBI")
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
        Plant.add_connection("EAF", "EAF Trigger", weight=1, flow="Crude Steel")
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
