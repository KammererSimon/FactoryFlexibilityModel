import logging
import os
import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.simulation.Scenario as sc
from factory_flexibility_model.simulation import Simulation as fs

def simulate(storage_size: float = 0,
             grid_capacity: float=500,
             session_folder: str ="examples/Demo",
             show_results: bool = True):

    """
    This function performs a single simulation run and returns the total cost value as a result.

    param storage_size: [float] The capacity of the installed battery storage in [kWh]
    param grid_capacity: [float] The maximum power of the electricity grid connection point in [kW]
    returns: [float] The total cost of operation including capital costs and depreciation costs in [€]
    """

    # define capex constants
    capex_storage = 10          # Annual capital and depreciation cost of battery storages in [€/kWh/a]
    capex_grid_capacity = 220   # Annual capacity charge for utilization of the powergrid in [€/kW/a]

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
    simulation.simulate(interval_length=730, threshold=0.000001, solver_config={"log_solver": False, "mip_gap": 0.01})

    # calculate costs:
    capex = capex_storage * storage_size + capex_grid_capacity * grid_capacity
    opex = simulation.result["objective"]

    if show_results:
        simulation.create_dash()
    else:
        return capex + opex

