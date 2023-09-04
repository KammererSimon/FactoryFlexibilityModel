# FACTORY MODEL MAIN
#     This skript is used to call the factory_model functionalities during ongoing development.
#     Right now there is no GUI or regular way to test the package, so this file is used to create a dummy environment.
#     Configuration of the process is done within the config.ini. (NOT in git!!!)

import logging
import os
import time

# IMPORT ENDOGENOUS COMPONENTS
# from joblib import Parallel, delayed
import pandas as pd

from factory_flexibility_model.io import factory_import as imp
from factory_flexibility_model.io import read_config as rc
from factory_flexibility_model.simulation import Simulation as fs
from tests import DRI_factories as dri
from tests import testfactory as tf
from tests import testscenario as ts

# READ CONFIG


def simulate_dri(simulation_task, **kwargs):
    file = f"C:\\Users\\smsikamm\\Documents\\Daten\\DRI-Setups\\iteration test\\{simulation_task['layout']}_NG{simulation_task['natural_gas_cost']}_EL{simulation_task['avg_electricity_price']}_VOL{simulation_task['volatility']}_CO2{simulation_task['CO2_price']}_{simulation_task['month']}.fsim"
    problem_file = f"C:\\Users\\smsikamm\\Documents\\Daten\\DRI-Setups\\problems\\{simulation_task['layout']}_NG{simulation_task['natural_gas_cost']}_EL{simulation_task['avg_electricity_price']}_VOL{simulation_task['volatility']}_CO2{simulation_task['CO2_price']}_{simulation_task['month']}.fsim"

    if not os.path.isfile(file) and not os.path.isfile(problem_file):

        t_start = time.time()

        factory = simulation_task["factory"]
        scenario = simulation_task["scenario"]

        # set variable Simulation parameters in the scenario
        if not simulation_task["layout"] == "Hydrogen":
            factory.set_configuration(
                "Source Natural Gas",
                parameters={"cost": simulation_task["natural_gas_cost"]},
            )

        factory.set_configuration(
            "CO2 Emissions", parameters={"cost": simulation_task["CO2_price"]}
        )
        scenario.cost_electricity = simulation_task["cost_electricity"]
        scenario.cost_electricity = (
            scenario.cost_electricity - scenario.cost_electricity.mean()
        ) * simulation_task["volatility"] + simulation_task["avg_electricity_price"]
        scenario.cost_electricity[scenario.cost_electricity < 0] = 0

        simulation = fs.Simulation(factory=factory, scenario=scenario)
        t_start = time.time()
        simulation.simulate(
            threshold=0.01, solver_config={"max_solver_time": 250}, **kwargs
        )
        simulation_task["solver_time"] = time.time() - t_start
        simulation.info = simulation_task
        if simulation.simulated:
            simulation.save(file, overwrite=True)
            logging.info(
                f"Simulation number {simulation_task['simulation_number']} finished within: {round((time.time()-t_start), 2)} s"
            )
        else:
            simulation.save(
                f"C:\\Users\\smsikamm\\Documents\\Daten\\DRI-Setups\\problems\\{simulation_task['layout']}_NG{simulation_task['natural_gas_cost']}_EL{simulation_task['avg_electricity_price']}_VOL{simulation_task['volatility']}_CO2{simulation_task['CO2_price']}_{simulation_task['month']}.fsim"
            )
            logging.warning(
                f"Simulation number {simulation_task['simulation_number']} aborted due to solver timeout"
            )
    else:
        logging.info(
            f"Simulation {simulation_task['simulation_number']} is already solved"
        )


def script_based():
    config = rc.read_config("config.ini")
    # CREATE A FACTORY LAYOUT FOR TESTING
    [Testfactory, Testscenario] = tf.create_testfactory(
        config["CASE"]["testfactory_key"],
        config["PATHS"]["data_path"],
        enable_slacks=config["SLACKS"]["enable_slacks"],
    )

    # SIMULATION
    simulation = fs.Simulation(
        Testfactory,
        Testscenario,
    )
    simulation.simulate(treshold=0.001)

    # Simulation.save("Testsim", overwrite=True)
    # Simulation = imp.import_simulation("Testsim")

    simulation.create_dash(config["CASE"]["dashboard_version"])


def excel_import():
    config = rc.read_config("config.ini")
    # CREATE A FACTORY LAYOUT FOR TESTING
    Testscenario = ts.create_testscenario(config["PATHS"]["data_path"])
    Testfactory = imp.import_factory_layout_from_excel(
        config["PATHS"]["factory_excel_path"]
    )

    # SIMULATION
    simulation = fs.Simulation(
        Testfactory,
        Testscenario,
    )
    simulation.simulate(treshold=0.001)
    simulation.write_results_to_excel("path")
    simulation.create_dash(config["CASE"]["dashboard_version"])


def create_simulation_file():
    config = rc.read_config("config.ini")
    # CREATE A FACTORY LAYOUT FOR TESTING
    [Testfactory, Testscenario] = tf.create_testfactory(
        config["CASE"]["testfactory_key"],
        config["PATHS"]["data_path"],
        enable_slacks=config["SLACKS"]["enable_slacks"],
    )

    # SIMULATION
    simulation = fs.Simulation(
        Testfactory,
        Testscenario,
    )
    simulation.simulate(treshold=0.001)

    simulation.save(config["PATHS"]["simulation_path"], overwrite=True)


def dashboard_development():
    config = rc.read_config("config.ini")
    simulation = imp.import_simulation(config["PATHS"]["simulation_path"])
    simulation.create_dash()


def blueprint_development():
    import factory_flexibility_model.factory.Blueprint as bp
    import factory_flexibility_model.simulation.Scenario as sc

    example = "Testlayout"  # "DRI_steel_factory"

    scenario = sc.Scenario(
        parameter_file=rf"examples\{example}\parameters.txt",
        timeseries_file=rf"examples\{example}\timeseries.txt",
    )

    blueprint = bp.Blueprint()
    blueprint.import_from_file(f"examples\\{example}")
    logging.basicConfig(level=logging.DEBUG)
    factory = blueprint.to_factory()

    simulation = fs.Simulation(factory=factory, scenario=scenario)
    simulation.simulate(log_solver=False)
    simulation.create_dash()
    print("check")


def gui_development():
    from factory_flexibility_model.ui import kivy_gui as fg

    gui = fg.factory_GUIApp()
    gui.run()


def dri():
    import tests.DRI_factories as dri

    config = rc.read_config("config.ini")
    t_start = time.time()

    # CREATE STEEL PLANT LAYOUT
    [Testfactory, Testscenario] = dri.create_steel_plant(
        config["PATHS"]["data_path_dri"],
        config["CASE"]["testfactory_key"],
        enable_slacks=config["SLACKS"]["enable_slacks"],
    )
    logging.info(f"Building plant infrastructure model finished: {time.time()-t_start}")

    # SIMULATION
    simulation = fs.Simulation(factory=Testfactory, scenario=Testscenario)
    simulation.simulate(
        threshold=0.001,
    )
    simulation.save(config["CASE"]["testfactory_key"], overwrite=True)
    simulation.create_dash()


def dri_iteration():
    from tests import DRI_factories as dri

    config = rc.read_config("config.ini")
    layout = "Partial"
    natural_gas_costs = [100]
    avg_electricity_prices = [
        20,
        30,
        35,
        40,
        45,
        50,
        55,
        60,
        65,
        70,
        75,
        80,
        85,
        90,
        95,
        100,
    ]
    volatilitys = [0, 0.5, 1, 1.5, 2]
    CO2_prices = [25, 50, 75]
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    [testfactory, testscenario] = dri.create_steel_plant(
        config["PATHS"]["data_path_dri"],
        layout,
        enable_slacks=config["SLACKS"]["enable_slacks"],
    )

    testscenario.enable_time_tracking = config["LOGS"]["enable_time_tracking"]

    simulation_list = list()
    i = 0
    for avg_electricity_price in avg_electricity_prices:
        for natural_gas_cost in natural_gas_costs:
            for volatility in volatilitys:
                for CO2_price in CO2_prices:
                    for month in months:
                        i += 1
                        simulation_list.append(
                            {
                                "avg_electricity_price": avg_electricity_price,
                                "layout": layout,
                                "natural_gas_cost": natural_gas_cost,
                                "volatility": volatility,
                                "CO2_price": CO2_price,
                                "scenario": testscenario,
                                "factory": testfactory,
                                "month": month,
                                "cost_electricity": testscenario.cost_electricity[
                                    (month - 1) * 672 : month * 672
                                ],
                                "simulation_number": i,
                            }
                        )

    for x in simulation_list:
        simulate_dri(x)


#    results = Parallel(n_jobs=2)(delayed(simulate_dri)(x) for x in simulation_list)


def dri_results():

    data = pd.DataFrame(
        columns=[
            "Layout",
            "cost_natural_gas",
            "avg_cost_electricity",
            "volantility_electricity",
            "cost_CO2",
            "co2_per_ton",
            "cost_per_ton",
            "hbi_storage_rate",
            "co2_capture_rate",
            "cost_electricity",
        ]
    )

    data = data.append(
        {
            "Layout": "Which of the three DRI Layouts was used for this run?",
            "cost_natural_gas": "Fixed natural Gas price in [€/t]",
            "avg_cost_electricity": "Average cost of the electricity timeseries in [€/MWh]",
            "volantility_electricity": "An index describing the peak-to-peak value that the underlying timeseries has been scaled to. 0=stationary, 1=original, 2=doubled, etc..",
            "variation": "used month of the german electricity price timeseries of 2022",
            "cost_CO2": "Fixed price for CO2-allowances in [€/tCO2]",
            "co2_per_ton": "Amount of resulting CO2 emissions of the steel production [tCO2/tLS]",
            "cost_per_ton": "OPEX of the steel production [€/tLS]",
            "hbi_storage_rate": "Ratio of total DRI taking the storage path vs the total amount of DRI being fed into EAF [%]",
            "co2_capture_rate": "Ratio of captured CO2 vs produced CO2 [%]",
            "rate_h2_in_dri": "Ratio of DRI produced using Hydrogen vs total DRI production volume [%]",
            "h2_storage_rate": "Ratio of total Hydrogen taking the storage path vs the total amount of H2 being fed into DRI [%]",
            "solver_time": "Required runtime of the Simulation [s]",
            "cost_electricity": "Average cost of purchased electricity resulting from the optimized operation profile [€/MWh]",
        },
        ignore_index=True,
    )

    file_list = []
    for root, dirs, files in os.walk(
        "C:\\Users\\smsikamm\\Documents\\Daten\\DRI-Setups\\iteration test"
    ):
        for file in files:
            if file.endswith(".fsim"):
                file_list.append(os.path.join(root, file))

    for file in file_list:
        simulation = imp.import_simulation(file)
        # calculate cost per ton of produced crude steel
        cost_per_ton = simulation.result["objective"] / sum(
            simulation.result["Crude Steel Output"]["utilization"]
        )
        logging.debug(f"cost_per_ton: {round(cost_per_ton, 2)}€")

        # calculate co2 emissions per ton of produced crude steel
        co2_per_ton = sum(simulation.result["CO2 Emissions"]["utilization"]) / sum(
            simulation.result["Crude Steel Output"]["utilization"]
        )
        logging.debug(f"co2_per_ton: {round(co2_per_ton, 3)}t")

        if simulation.info["layout"] == "CCS":
            # calculate co2 capture rate
            co2_capture_rate = sum(simulation.result["CCS_to_CO2 Sink"]) / sum(
                simulation.result["DRI_to_Pool CO2"]
            )
        else:
            co2_capture_rate = 0
        logging.debug(f"co2_capture_rate: {round(co2_capture_rate, 3) * 100}%")

        # calculate ratio of H2 and NG used for DRI
        if simulation.info["layout"] == "Partial":
            rate_h2_in_dri = sum(simulation.result["H2 DRI_to_DRI Composition"]) / sum(
                simulation.result["DRI Composition"]["utilization"]
            )
        elif simulation.info["layout"] == "CCS":
            rate_h2_in_dri = 0
        else:
            rate_h2_in_dri = 1
        logging.debug(f"rate_h2_in_dri: {round(rate_h2_in_dri, 3) * 100}%")

        # calculate h2_storage_rate
        if simulation.info["layout"] == "Partial":
            h2_storage_rate = sum(
                simulation.result["Pool Hydrogen_to_Hydrogen Storage"]
            ) / sum(simulation.result["Pool Hydrogen_to_H2 DRI"])
        elif simulation.info["layout"] == "Hydrogen":
            h2_storage_rate = sum(
                simulation.result["Pool Hydrogen_to_Hydrogen Storage"]
            ) / sum(simulation.result["Pool Hydrogen_to_DRI"])
        else:
            h2_storage_rate = 0
        logging.debug(f"h2_storage_rate: {round(h2_storage_rate, 3) * 100}%")

        # calculate hbi_storage_rate
        hbi_storage_rate = sum(simulation.result["Pool DRI_to_DRI Compactor"]) / sum(
            simulation.result["Pool DRI"]["utilization"]
        )

        # calculate achieved electricity price
        cost_electricity = sum(
            simulation.result["Source Electricity"]["utilization"]
            * simulation.scenario.cost_electricity
        ) / sum(simulation.result["Source Electricity"]["utilization"])
        logging.debug(f"price_electricity: {round(cost_electricity, 2)}€/MWh")

        data = data.append(
            {
                "Layout": simulation.info["layout"],
                "cost_natural_gas": simulation.info["natural_gas_cost"],
                "avg_cost_electricity": simulation.info["avg_electricity_price"],
                "volantility_electricity": simulation.info["volatility"],
                "variation": simulation.info["month"],
                "cost_CO2": simulation.info["CO2_price"],
                "co2_per_ton": co2_per_ton,
                "cost_per_ton": cost_per_ton,
                "hbi_storage_rate": hbi_storage_rate,
                "co2_capture_rate": co2_capture_rate,
                "rate_h2_in_dri": rate_h2_in_dri,
                "h2_storage_rate": h2_storage_rate,
                "solver_time": simulation.info["solver_time"],
                "cost_electricity": cost_electricity,
            },
            ignore_index=True,
        )

    data.to_excel(
        "C:\\Users\\smsikamm\\Documents\\Daten\\DRI-Setups\\iteration test\\CCS_Auswertung.xlsx",
        index=False,
    )
    # Simulation.create_dash()
