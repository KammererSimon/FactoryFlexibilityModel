# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: WattsInsight
# File Name: simple_simulation_call.py
#
# Copyright (c) [2024]
# [Institute of Energy Systems, Energy Efficiency and Energy Economics
#  TU Dortmund
#  Simon Kammerer (simon.kammerer@tu-dortmund.de)]
# [Software Engineering by Algorithms and Logic
#  TU Dortmund
#  Constantin Chaumet (constantin.chaumet@tu-dortmund.de)]
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------
# INFO
"""
- Die funktion unten hat die zwei hyperparameter "storage_size" und "grid_capacity" als hyperparameter.
    Als Rückgabewert bekommst du die Gesamtkosten des Systems in €

- Im Sachkontext gucken wir damit, wie effizient ein Abfallverwerter laufen kann wenn man ihm unterschiedlich viel
Netzanschlusskapazität und Batteriespeicher zur Verfügung stellt.

- Die funktion hat noch zwei hardegecodete variablen für die investkosten in den Speicher + Leistungspreise die für den Netzanschluss zu zahlen sind mit drin.
    -> Die brauchen wir für den gesamtkostenterm damit wir in der optimierung nicht einfach for free beliebig viel speichern nutzen dürfen...

- Das betrachtete Simulationslayout liegt unter examples/Demo.
    Wenn du dir das im Detail angucken willst: poetry run gui -> Demo.ffm in der gui öffnen

- Wenn du dir ein simulationsergebnis im Detail angucken willst setzt den parameter "show_result" auf true, dann wird kein ergebnis zurückgegeben sondern stattdessen lokal das dashboard mit den ergebnissen des runs gehostet
    -> Kannste dir mal angucken um mal n gefühl zu bekommen was die simulation im detail so macht.

- Standardmäßig läuft das skript jetzt einfach still und leise durch. wenn du Wissen willst was passiert kannste das logginglevel verändern und in dem simulationsaufruf das solverlog aktivieren

"""

# IMPORTS
import logging
import os
from random import uniform

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.simulation.Scenario as sc
from factory_flexibility_model.simulation import Simulation as fs


def simulate(trial):
    """
    This function performs a single simulation run and returns the total cost value as a result.

    param storage_size: [float] The capacity of the installed battery storage in [kWh]
    param grid_capacity: [float] The maximum power of the electricity grid connection point in [kW]
    returns: [float] The total cost of operation including capital costs and depreciation costs in [€]
    """
    session_folder: str = "examples/Usecase_Blackbox_Optimizer_Study"
    show_results: bool = False

    storage_size: float = trial.suggest_float("storage_size", 0.0, 3000.0)
    grid_capacity: float = trial.suggest_float("grid_capacity", 0.0, 1600.0)

    # TODO: korrekt einbinden
    storage_power: float = trial.suggest_float("storage_power", 0.0, 6000.0)
    qnt_forklifts: int = trial.suggest_int(
        "qnt_forklifts", 1, 4
    )  # sollte m.E. besser sein als 4 booleans
    qnt_excavators: int = trial.suggest_int(
        "qnt_excavators", 1, 3
    )  # sollte m.E. besser sein als 3 booleans
    pv_capacity: float = trial.suggest_float("pv_capacity", 0.0, 3600.0)

    # define capex constants (Capital costs ignored)
    depreciation_period = 10  # [Years]
    capex_storage = (
        400 / 12 / depreciation_period
    )  # Monthly depreciation cost of battery storages in [€/kWh/month]
    capex_grid_capacity = (
        100 / 12 / depreciation_period
    )  # Monthly capacity charge for utilization of the power grid in [€/kW/month]
    capex_excavators = (
        500000 / 12 / depreciation_period
    )  # Monthly depreciation costs for an electric excavator [€]
    capex_forklifts = (
        62900 / 12 / depreciation_period
    )  # Monthly depreciation costs for an electric forklift [€]
    capex_storage_power = (
        75 / 12 / depreciation_period
    )  # Monthly depreciation costs for rectifiers and inverters in [€/kW/month]
    capex_pv = (
        1000 / 12 / depreciation_period
    )  # Monthly depreciation costs for Solar modules including inverters in [€/kWp/month]

    # set logging level to avoid any unnecessary console outputs from the simulation scripts
    logging.basicConfig(level=logging.ERROR)

    # check, that the session_folder is existing
    if not os.path.exists(session_folder):
        raise FileNotFoundError(
            f"The given session path ({session_folder}) does not exist!"
        )

    # create scenario-object from file
    scenario = sc.Scenario(scenario_file=f"{session_folder}\\scenarios\\default.sc")

    # create factory-object from file
    blueprint = bp.Blueprint()
    blueprint.import_from_file(f"{session_folder}\\layout\\Layout.factory")
    factory = blueprint.to_factory()

    # set hyperparameters
    factory.set_configuration(
        factory.get_key("Battery_storage"),
        {
            "capacity": storage_size,
            "power_max_charge": storage_power,
            "power_max_discharge": storage_power,
        },
    )
    factory.set_configuration(factory.get_key("Grid"), {"power_max": grid_capacity})
    factory.set_configuration(factory.get_key("PV"), {"power_max": pv_capacity})

    # Disable unutilized forklifts in the simulation layout
    if qnt_forklifts < 2:
        factory.set_configuration(factory.get_key("Forklift_2"), {"capacity": 0})
    if qnt_forklifts < 3:
        factory.set_configuration(factory.get_key("Forklift_3"), {"capacity": 0})
    if qnt_forklifts < 4:
        factory.set_configuration(factory.get_key("Forklift_4"), {"capacity": 0})

    # Disable unutilized excavators in the layout
    if qnt_excavators < 2:
        factory.set_configuration(factory.get_key("Excavator_2"), {"capacity": 0})
    if qnt_excavators < 3:
        factory.set_configuration(factory.get_key("Excavator_3"), {"capacity": 0})

    # create simulation object
    simulation = fs.Simulation(factory=factory, scenario=scenario)

    # run simulation
    simulation.simulate(
        threshold=0.000001, solver_config={"log_solver": False, "mip_gap": 0.01}
    )

    if show_results:
        simulation.create_dash()
    else:
        # calculate and return costs:
        capex = (
            capex_storage * storage_size
            + capex_storage_power * storage_power
            + capex_grid_capacity * grid_capacity
            + capex_pv * pv_capacity
            + capex_forklifts * qnt_forklifts
            + capex_excavators * qnt_excavators
        )
        opex = simulation.result["objective"]
        emissions = sum(simulation.result["total_emissions"])
        return (
            capex + opex,
            emissions,
        )


# CODE
def simulate_ax(parameterization, trial_index, queue):
    """
    This function performs a single simulation run and returns the total cost value as a result.

    param storage_size: [float] The capacity of the installed battery storage in [kWh]
    param grid_capacity: [float] The maximum power of the electricity grid connection point in [kW]
    returns: [float] The total cost of operation including capital costs and depreciation costs in [€]
    """
    session_folder: str = "examples/Usecase_Blackbox_Optimizer_Study"
    show_results: bool = False

    storage_size: float = parameterization.get("storage_size")
    grid_capacity: float = parameterization.get("grid_capacity")
    storage_power: float = parameterization.get("storage_power")
    qnt_forklifts: int = parameterization.get("forklift_count")
    qnt_excavators: int = parameterization.get("excavator_count")
    pv_capacity: float = parameterization.get("pv_capacity")

    # define capex constants (Capital costs ignored)
    depreciation_period = 10  # [Years]
    capex_storage = (
        400 / 12 / depreciation_period
    )  # Monthly depreciation cost of battery storages in [€/kWh/month]
    capex_grid_capacity = (
        100 / 12 / depreciation_period
    )  # Monthly capacity charge for utilization of the power grid in [€/kW/month]
    capex_excavators = (
        500000 / 12 / depreciation_period
    )  # Monthly depreciation costs for an electric excavator [€]
    capex_forklifts = (
        62900 / 12 / depreciation_period
    )  # Monthly depreciation costs for an electric forklift [€]
    capex_storage_power = (
        75 / 12 / depreciation_period
    )  # Monthly depreciation costs for rectifiers and inverters in [€/kW/month]
    capex_pv = (
        1000 / 12 / depreciation_period
    )  # Monthly depreciation costs for Solar modules including inverters in [€/kWp/month]

    # set logging level to avoid any unnecessary console outputs from the simulation scripts
    logging.basicConfig(level=logging.ERROR)

    # check, that the session_folder is existing
    if not os.path.exists(session_folder):
        raise FileNotFoundError(
            f"The given session path ({session_folder}) does not exist!"
        )

    # create scenario-object from file
    scenario = sc.Scenario(scenario_file=f"{session_folder}\\scenarios\\default.sc")

    # create factory-object from file
    blueprint = bp.Blueprint()
    blueprint.import_from_file(f"{session_folder}\\layout\\Layout.factory")
    factory = blueprint.to_factory()

    # set hyperparameters
    factory.set_configuration(
        factory.get_key("Battery_storage"),
        {
            "capacity": storage_size,
            "power_max_charge": storage_power,
            "power_max_discharge": storage_power,
        },
    )
    factory.set_configuration(factory.get_key("Grid"), {"power_max": grid_capacity})
    factory.set_configuration(factory.get_key("PV"), {"power_max": pv_capacity})

    # Disable unutilized forklifts in the simulation layout
    if qnt_forklifts < 2:
        factory.set_configuration(factory.get_key("Forklift_2"), {"capacity": 0})
    if qnt_forklifts < 3:
        factory.set_configuration(factory.get_key("Forklift_3"), {"capacity": 0})
    if qnt_forklifts < 4:
        factory.set_configuration(factory.get_key("Forklift_4"), {"capacity": 0})

    # Disable unutilized excavators in the layout
    if qnt_excavators < 2:
        factory.set_configuration(factory.get_key("Excavator_2"), {"capacity": 0})
    if qnt_excavators < 3:
        factory.set_configuration(factory.get_key("Excavator_3"), {"capacity": 0})

    # create simulation object
    simulation = fs.Simulation(factory=factory, scenario=scenario)

    # run simulation
    simulation.simulate(
        threshold=0.000001,
        solver_config={
            "log_solver": False,
            "mip_gap": 0.01,
        },
    )

    if show_results:
        simulation.create_dash()
    else:
        # calculate and return costs:
        capex = (
            capex_storage * storage_size
            + capex_storage_power * storage_power
            + capex_grid_capacity * grid_capacity
            + capex_pv * pv_capacity
            + capex_forklifts * qnt_forklifts
            + capex_excavators * qnt_excavators
        )
        opex = simulation.result["objective"]
        emissions = sum(simulation.result["total_emissions"])
        emissions = uniform(0, 1000)
        queue.put(
            {
                "idx": trial_index,
                "res": {
                    "capex": (
                        abs(capex + opex),
                        0.0,
                    ),
                    "emissions": (emissions, 0.0),
                },
            }
        )
