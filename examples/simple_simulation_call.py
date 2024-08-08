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

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.simulation.Scenario as sc
from factory_flexibility_model.simulation import Simulation as fs


# CODE
def simulate(trial):
    """
    This function performs a single simulation run and returns the total cost value as a result.

    param storage_size: [float] The capacity of the installed battery storage in [kWh]
    param grid_capacity: [float] The maximum power of the electricity grid connection point in [kW]
    returns: [float] The total cost of operation including capital costs and depreciation costs in [€]
    """
    session_folder: str = "examples/Demo"
    show_results: bool = False

    storage_size: float = trial.suggest_float("storage_size", 0.0, 3000.0)
    grid_capacity: float = trial.suggest_float("grid_capacity", 0.0, 1600.0)

    # define capex constants
    capex_storage = 1  # Monthly capital and depreciation cost of battery storages in [€/kWh/month]
    capex_grid_capacity = 20  # Montly capacity charge for utilization of the powergrid in [€/kW/month]

    # set logging level to avoid any unnecessary console outputs from the simulation scripts
    logging.basicConfig(level=logging.ERROR)

    # check, that the session_folder is existing
    if not os.path.exists(session_folder):
        raise FileNotFoundError(f"The given session path ({session_folder}) does not exist!")

    # create scenario-object from file
    scenario = sc.Scenario(scenario_file=f"{session_folder}\\scenarios\\default.sc")

    # create factory-object from file
    blueprint = bp.Blueprint()
    blueprint.import_from_file(f"{session_folder}\\layout\\Layout.factory")
    factory = blueprint.to_factory()

    # set hyperparameters
    factory.set_configuration(factory.get_key("Speicher"), {"capacity": storage_size})
    factory.set_configuration(factory.get_key("Netzanbindung"), {"power_max": grid_capacity})

    # create simulation object
    simulation = fs.Simulation(factory=factory, scenario=scenario)

    # run simulation
    simulation.simulate(threshold=0.000001, solver_config={"log_solver": False, "mip_gap": 0.01})

    if show_results:
        simulation.create_dash()
    else:
        # calculate and return costs:
        capex = capex_storage * storage_size + capex_grid_capacity * grid_capacity
        opex = simulation.result["objective"]
        emissions = sum(simulation.result["total_emissions"])
        return capex + opex if capex + opex < 50000 else 50000 + 10000 * (capex + opex - 50000) / (
                    100000 + capex + opex - 50000), emissions
