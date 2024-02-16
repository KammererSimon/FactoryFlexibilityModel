# FACTORY MODEL MAIN
#     This skript is used to call the main functionalities of the factory flexibility model

import logging
import os
import sys

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.simulation.Scenario as sc

# IMPORTS
from factory_flexibility_model.io import factory_import as imp
from factory_flexibility_model.simulation import Simulation as fs


def gui():
    """
    This function opens the simulation setup gui.
    """
    from factory_flexibility_model.ui import kivy_gui as fg

    # create gui instance
    gui = fg.factory_GUIApp()

    # run gui
    gui.run()


def simulate_session():
    """
    This function takes the path to a session folder and conducts the simulation.
    """

    logging.basicConfig(level=logging.DEBUG)

    session_folder = sys.argv[1]

    # check, that the session_folder is existing
    if not os.path.exists(session_folder):
        raise FileNotFoundError(f"The given path ({session_folder}) does not exist!")

    # create scenario
    scenario = sc.Scenario(session_folder=session_folder)

    # create factory
    blueprint = bp.Blueprint()
    blueprint.import_from_file(session_folder)
    factory = blueprint.to_factory()

    # setup, run and save simulation
    simulation = fs.Simulation(factory=factory, scenario=scenario)
    simulation.simulate(threshold=0.000001)
    simulation.save(rf"{session_folder}\simulations")

    # run dashboard
    simulation.create_dash()


def dash():
    r"""
    This function imports a given (solved) simulation file and loads it into the plotly dashboard for analysis.
    :param simulation_data: [str] Path to a solved simulation file. Typically stored under "session_folder\simulations\*simulation_name*.sim"
    """

    # import simulation
    simulation = imp.import_simulation(sys.argv[1])

    # create and run dashboard
    simulation.create_dash()
