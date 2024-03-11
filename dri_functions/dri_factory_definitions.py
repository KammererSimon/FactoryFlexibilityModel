# IMPORTS
import numpy as np
import os

import factory_flexibility_model.simulation.Scenario as sc
import factory_flexibility_model.factory.Blueprint as bp
from factory_flexibility_model.io.set_logger import set_logging_level

# FUNCTIONS
def create_steel_plant(model_parameters, plant_type, config = None):

    # configure logger
    if "enable_log" in config and config["enable_log"]:
        set_logging_level(config["enable_log"])

    # CREATE FACTORY OBJECT
    blueprint = bp.Blueprint()
    blueprint.import_from_file(rf"{os.getcwd()}\simulations\input_data\{plant_type}")
    blueprint.info["enable_slacks"] = config["enable_slacks"]
    plant = blueprint.to_factory()

    # CREATE SCENARIO

    # inititalize blank scenario
    scenario = sc.Scenario(f"{os.getcwd()}\\simulations\\input_data\\Partial")

    # add scenario parameters according to the selected plant type
    if plant_type == "Partial":

        # SET MASS BALANCES
        plant.connections[plant.get_key("EAF -> Pool CO2")].weight_origin = model_parameters["co2_out_t_per_tls"] * (1 - model_parameters["scrap_share_per_tls"])
        plant.connections[plant.get_key("Hydrogen DRI -> Pool CO2")].weight_origin = model_parameters["h2_setup_co2_out_t_per_tdri"]
        plant.connections[plant.get_key("Natural Gas DRI -> Pool CO2")].weight_origin = model_parameters["co2_out_t_per_tdri"]
        plant.connections[plant.get_key("PEM -> Pool Oxygen")].weight_origin = model_parameters["oxygen_out_t_per_th2"]
        plant.connections[plant.get_key("Pool DRI -> EAF")].weight_destination = model_parameters["dri_t_per_tls"] * (1 - model_parameters["scrap_share_per_tls"])
        plant.connections[plant.get_key("Pool Electricity -> DRI Compactor")].weight_destination = model_parameters["hbi_compact_electricity_mwh_per_tDRI"] + model_parameters["hbi_reheat_electricity_mwh_per_tDRI"]
        plant.connections[plant.get_key("Pool Electricity -> Hydrogen DRI")].weight_destination = model_parameters["electricity_mwh_per_tdri"]
        plant.connections[plant.get_key("Pool Electricity -> Natural Gas DRI")].weight_destination = model_parameters["electricity_mwh_per_tdri"]
        plant.connections[plant.get_key("Pool Electricity -> PEM")].weight_destination = model_parameters["electricity_mwh_per_th2"]
        plant.connections[plant.get_key("Pool Hydrogen -> Hydrogen DRI")].weight_destination = model_parameters["h2_gas_preheat_t_per_tdri"]
        plant.connections[plant.get_key("Pool Oxygen -> EAF")].weight_destination = model_parameters["oxygen_t_per_tls"]
        plant.connections[plant.get_key("Source Carbon -> Hydrogen DRI")].weight_destination = model_parameters["carbon_h2_t_per_tdri"]
        plant.connections[plant.get_key("Source Iron Ore -> Hydrogen DRI")].weight_destination = model_parameters["iron_ore_pellets_t_per_tdri"]
        plant.connections[plant.get_key("Source Iron Ore -> Natural Gas DRI")].weight_destination = model_parameters["iron_ore_pellets_t_per_tdri"]
        plant.connections[plant.get_key("Source Lime -> EAF")].weight_destination = model_parameters["lime_t_per_tls"]
        plant.connections[plant.get_key("Source Natural Gas -> Natural Gas DRI")].weight_destination = model_parameters["natural_gas_t_per_tdri"]
        plant.connections[plant.get_key("Source Scrap -> EAF")].weight_destination = model_parameters["dri_t_per_tls"] * model_parameters["scrap_share_per_tls"]
        plant.connections[plant.get_key("Source Water -> PEM")].weight_destination = model_parameters["water_t_per_th2"]

        # SET MARKET SCENARIO
        scenario.configurations[plant.get_key("Oxygen Sales")] = {"cost": model_parameters["cost_oxygen_€_per_to2"]}
        scenario.configurations[plant.get_key("Source Hydrogen")] = {"cost": model_parameters["cost_hydrogen_€_per_th2"]}
        scenario.configurations[plant.get_key("Source Iron Ore")] = {"cost": model_parameters["cost_iron_ore_€_per_t"]}
        scenario.configurations[plant.get_key("Source Lime")] = {"cost": model_parameters["cost_lime_€_per_t"]}
        scenario.configurations[plant.get_key("Source Oxygen")] = {"cost": model_parameters["cost_oxygen_€_per_to2"]}
        scenario.configurations[plant.get_key("Source Scrap")] = {"cost": model_parameters["cost_scrap_€_per_t"]}

        # SET COMPONENT OPERATING CONSTRAINTS
        scenario.configurations[plant.get_key("PEM")] = {"power_max": model_parameters["electrolyzer_size"]}
        scenario.configurations[plant.get_key("DRI Compactor")] = {"power_max": model_parameters["dri_power_max"]}
        scenario.configurations[plant.get_key("DRI Restrictions")] = {"power_min": model_parameters["dri_power_min"],
                                                                    "power_max": model_parameters["dri_power_max"],
                                                                    "max_pos_ramp_power": model_parameters["dri_ramp_up"],
                                                                    "max_neg_ramp_power":  model_parameters["dri_ramp_down"]}


        scenario.configurations[plant.get_key("EAF Trigger")] = {"max_parallel": model_parameters["eaf_entities"],
                                                                 "load_profile_material": [model_parameters["eaf_batch_size_tls"]]}

        scenario.configurations[plant.get_key("HBI Storage Deadtime")] = {"delay": model_parameters["hbi_min_storage_time"]}
        scenario.configurations[plant.get_key("HBI Storage")] = {"capacity": model_parameters["hbi_storage_size"],
                                                                 "soc_start": model_parameters["hbi_storage_soc_start"]}
        scenario.configurations[plant.get_key("Hydrogen Storage")] = {"capacity": model_parameters["h2_storage_size"],
                                                                      "soc_start": model_parameters["h2_storage_soc_start"],
                                                                      "efficiency": model_parameters["h2_storage_efficiency"]}

        hourly_production_t = model_parameters["annual_dri_production_mtons"] * 1000000 / 8760
        scenario.configurations[plant.get_key("Demand Schedule")] = {"demands": np.array([[1, blueprint.info["timesteps"], hourly_production_t * blueprint.info["timesteps"], 10000000]])}

    elif plant_type == "CCS":

        # SET MASS BALANCES
        plant.connections[plant.get_key("EAF -> Pool CO2 Emissions")].weight_origin = model_parameters["co2_out_t_per_tls"] * (1 - model_parameters["scrap_share_per_tls"])
        plant.connections[plant.get_key("Natural Gas DRI -> Pool CO2")].weight_origin = model_parameters["co2_out_t_per_tdri"]
        plant.connections[plant.get_key("Pool DRI -> EAF")].weight_destination = model_parameters["dri_t_per_tls"] * (1 - model_parameters["scrap_share_per_tls"])
        plant.connections[plant.get_key("Pool Electricity -> DRI Compactor")].weight_destination = model_parameters["hbi_compact_electricity_mwh_per_tDRI"] + model_parameters["hbi_reheat_electricity_mwh_per_tDRI"]
        plant.connections[plant.get_key("Pool Electricity -> Natural Gas DRI")].weight_destination = model_parameters["electricity_mwh_per_tdri"]
        plant.connections[plant.get_key("Pool Oxygen -> EAF")].weight_destination = model_parameters["oxygen_t_per_tls"]
        plant.connections[plant.get_key("Source Iron Ore -> Natural Gas DRI")].weight_destination = model_parameters["iron_ore_pellets_t_per_tdri"]
        plant.connections[plant.get_key("Source Lime -> EAF")].weight_destination = model_parameters["lime_t_per_tls"]
        plant.connections[plant.get_key("Source Natural Gas -> Natural Gas DRI")].weight_destination = model_parameters["natural_gas_t_per_tdri"]
        plant.connections[plant.get_key("Source Scrap -> EAF")].weight_destination = model_parameters["dri_t_per_tls"] * model_parameters["scrap_share_per_tls"]
        plant.connections[plant.get_key("CCS -> Pool CO2 Emissions")].weight_destination = 1-model_parameters["ccs_efficiency"]
        plant.connections[plant.get_key("CCS -> CO2 Storage")].weight_destination = model_parameters["ccs_efficiency"]
        plant.connections[plant.get_key("Pool Electricity -> CCS")].weight_destination = model_parameters["electricity_mwh_per_t_sequestered"]

        # SET MARKET SCENARIO
        scenario.configurations[plant.get_key("Oxygen Sales")] = {"cost": model_parameters["cost_oxygen_€_per_to2"]}
        scenario.configurations[plant.get_key("Source Iron Ore")] = {"cost": model_parameters["cost_iron_ore_€_per_t"]}
        scenario.configurations[plant.get_key("Source Lime")] = {"cost": model_parameters["cost_lime_€_per_t"]}
        scenario.configurations[plant.get_key("Source Oxygen")] = {"cost": model_parameters["cost_oxygen_€_per_to2"]}
        scenario.configurations[plant.get_key("Source Scrap")] = {"cost": model_parameters["cost_scrap_€_per_t"]}

        # SET COMPONENT OPERATING CONSTRAINTS
        scenario.configurations[plant.get_key("DRI Compactor")] = {"power_max": model_parameters["dri_power_max"]}
        scenario.configurations[plant.get_key("Natural Gas DRI")] = {"power_min": model_parameters["dri_power_min"],
                                                                    "power_max": model_parameters["dri_power_max"],
                                                                    "max_pos_ramp_power": model_parameters["dri_ramp_up"],
                                                                    "max_neg_ramp_power":  model_parameters["dri_ramp_down"]}


        scenario.configurations[plant.get_key("EAF Trigger")] = {"max_parallel": model_parameters["eaf_entities"],
                                                                 "load_profile_material": [model_parameters["eaf_batch_size_tls"]]}

        scenario.configurations[plant.get_key("HBI Storage Deadtime")] = {"delay": model_parameters["hbi_min_storage_time"]}
        scenario.configurations[plant.get_key("HBI Storage")] = {"capacity": model_parameters["hbi_storage_size"],
                                                                 "soc_start": model_parameters["hbi_storage_soc_start"]}

        hourly_production_t = model_parameters["annual_dri_production_mtons"] * 1000000 / 8760
        scenario.configurations[plant.get_key("Demand Schedule")] = {"demands": np.array([[1, blueprint.info["timesteps"], hourly_production_t * blueprint.info["timesteps"], 10000000]])}

    elif plant_type == "Hydrogen":

        # SET MASS BALANCES
        plant.connections[plant.get_key("EAF -> Pool CO2")].weight_origin = model_parameters["co2_out_t_per_tls"] * (1 - model_parameters["scrap_share_per_tls"])
        plant.connections[plant.get_key("Hydrogen DRI -> Pool CO2")].weight_origin = model_parameters["h2_setup_co2_out_t_per_tdri"]
        plant.connections[plant.get_key("PEM -> Pool Oxygen")].weight_origin = model_parameters["oxygen_out_t_per_th2"]
        plant.connections[plant.get_key("Pool DRI -> EAF")].weight_destination = model_parameters["dri_t_per_tls"] * (1 - model_parameters["scrap_share_per_tls"])
        plant.connections[plant.get_key("Pool Electricity -> DRI Compactor")].weight_destination = model_parameters["hbi_compact_electricity_mwh_per_tDRI"] + model_parameters["hbi_reheat_electricity_mwh_per_tDRI"]
        plant.connections[plant.get_key("Pool Electricity -> Hydrogen DRI")].weight_destination = model_parameters["electricity_mwh_per_tdri"]
        plant.connections[plant.get_key("Pool Electricity -> PEM")].weight_destination = model_parameters["electricity_mwh_per_th2"]
        plant.connections[plant.get_key("Pool Hydrogen -> Hydrogen DRI")].weight_destination = model_parameters["h2_gas_preheat_t_per_tdri"]
        plant.connections[plant.get_key("Pool Oxygen -> EAF")].weight_destination = model_parameters["oxygen_t_per_tls"]
        plant.connections[plant.get_key("Source Carbon -> Hydrogen DRI")].weight_destination = model_parameters["carbon_h2_t_per_tdri"]
        plant.connections[plant.get_key("Source Iron Ore -> Hydrogen DRI")].weight_destination = model_parameters["iron_ore_pellets_t_per_tdri"]
        plant.connections[plant.get_key("Source Lime -> EAF")].weight_destination = model_parameters["lime_t_per_tls"]
        plant.connections[plant.get_key("Source Scrap -> EAF")].weight_destination = model_parameters["dri_t_per_tls"] * model_parameters["scrap_share_per_tls"]
        plant.connections[plant.get_key("Source Water -> PEM")].weight_destination = model_parameters["water_t_per_th2"]

        # SET MARKET SCENARIO
        scenario.configurations[plant.get_key("Oxygen Sales")] = {"cost": model_parameters["cost_oxygen_€_per_to2"]}
        scenario.configurations[plant.get_key("Source Hydrogen")] = {"cost": model_parameters["cost_hydrogen_€_per_th2"]}
        scenario.configurations[plant.get_key("Source Iron Ore")] = {"cost": model_parameters["cost_iron_ore_€_per_t"]}
        scenario.configurations[plant.get_key("Source Lime")] = {"cost": model_parameters["cost_lime_€_per_t"]}
        scenario.configurations[plant.get_key("Source Oxygen")] = {"cost": model_parameters["cost_oxygen_€_per_to2"]}
        scenario.configurations[plant.get_key("Source Scrap")] = {"cost": model_parameters["cost_scrap_€_per_t"]}

        # SET COMPONENT OPERATING CONSTRAINTS
        scenario.configurations[plant.get_key("PEM")] = {"power_max": model_parameters["electrolyzer_size"]}
        scenario.configurations[plant.get_key("DRI Compactor")] = {"power_max": model_parameters["dri_power_max"]}
        scenario.configurations[plant.get_key("Hydrogen DRI")] = {"power_min": model_parameters["dri_power_min"],
                                                                  "power_max": model_parameters["dri_power_max"],
                                                                  "max_pos_ramp_power": model_parameters["dri_ramp_up"],
                                                                  "max_neg_ramp_power":  model_parameters["dri_ramp_down"]}


        scenario.configurations[plant.get_key("EAF Trigger")] = {"max_parallel": model_parameters["eaf_entities"],
                                                                 "load_profile_material": [model_parameters["eaf_batch_size_tls"]]}

        scenario.configurations[plant.get_key("HBI Storage Deadtime")] = {"delay": model_parameters["hbi_min_storage_time"]}
        scenario.configurations[plant.get_key("HBI Storage")] = {"capacity": model_parameters["hbi_storage_size"],
                                                                 "soc_start": model_parameters["hbi_storage_soc_start"]}
        scenario.configurations[plant.get_key("Hydrogen Storage")] = {"capacity": model_parameters["h2_storage_size"],
                                                                      "soc_start": model_parameters["h2_storage_soc_start"],
                                                                      "efficiency": model_parameters["h2_storage_efficiency"]}

        hourly_production_t = model_parameters["annual_dri_production_mtons"] * 1000000 / 8760
        scenario.configurations[plant.get_key("Demand Schedule")] = {"demands": np.array([[1, blueprint.info["timesteps"], hourly_production_t * blueprint.info["timesteps"], 10000000]])}

    return plant, scenario