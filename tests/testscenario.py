# IMPORT 3RD PARTY PACKAGES
import numpy as np
import pandas as pd

# IMPORT ENDOGENOUS COMPONENTS
from factory_flexibility_model.simulation import Scenario as sc


def create_testscenario(data_path):

    Testscenario = sc.Scenario()
    Testscenario.number_of_timesteps = 168
    Testscenario.cost_co2_per_kg = 0.0814
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
    Testscenario.car_data = pd.read_excel(inputs["car_data"], sheet_name="Tabelle1")
    Testscenario.availability = timeseries["availability"]
    Testscenario.solar_radiation = timeseries["radiation"]
    Testscenario.cost_gas = timeseries["cost_gas"]
    Testscenario.cost_electricity = timeseries["cost_electricity"]
    Testscenario.cost_electricity_lingen = timeseries["cost_electricity_lingen1"]
    Testscenario.cost_electricity_lingen2 = timeseries["cost_electricity_lingen2"]
    Testscenario.cost_electricity_lingen3 = timeseries["cost_electricity_lingen3"]
    Testscenario.cost_electricity_lingen4 = timeseries["cost_electricity_lingen4"]
    Testscenario.cost_electricity_lingen5 = timeseries["cost_electricity_lingen5"]
    Testscenario.cost_electricity_lingen6 = timeseries["cost_electricity_lingen6"]
    Testscenario.revenue_electricity = timeseries["revenue_electricity"]
    Testscenario.Pmax_electricity_grid = float(config["Egrid_max"])
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

    return Testscenario
