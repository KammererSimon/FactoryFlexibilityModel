# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: Factory_Flexibility_Model
# File Name: main.py
#
# Copyright (c) [2024]
# [Institute of Energy Systems, Energy Efficiency and Energy Economics
#  TU Dortmund
#  Simon Kammerer (simon.kammerer@tu-dortmund.de)]
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
from examples.simple_simulation_call import simulate_ax


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

    simulate_ax()
    return

    logging.basicConfig(level=logging.WARNING)


    session_folder = sys.argv[1]

    # check, that the session_folder is existing
    if not os.path.exists(session_folder):
        raise FileNotFoundError(f"The given path ({session_folder}) does not exist!")

    # create scenario
    scenario = sc.Scenario(scenario_file=f"{session_folder}\\scenarios\\default.sc")

    # create factory
    blueprint = bp.Blueprint()
    blueprint.import_from_file(f"{session_folder}\\layout\\Layout.factory")
    factory = blueprint.to_factory()

    # setup, run and save simulation
    simulation = fs.Simulation(factory=factory, scenario=scenario)
    simulation.simulate(interval_length=730, threshold=0.000001, solver_config={"log_solver": False})
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
    simulation.create_dash()  # add  -> authentication={"user": "password"} <- to add a user login
