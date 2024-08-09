# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: WattsInsight
# File Name: main.py
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

# FACTORY MODEL MAIN
#     This skript is used to call the main functionalities of the factory flexibility model
import datetime
import logging
import multiprocessing
import os
import signal
import sys
import threading
import webbrowser
from multiprocessing import Process
from wsgiref.simple_server import make_server

import psutil
from ax import Models
from ax.modelbridge.generation_node import GenerationStep
from ax.modelbridge.generation_strategy import GenerationStrategy
from ax.models.torch.botorch_modular.surrogate import Surrogate
from botorch.acquisition.multi_objective import qNoisyExpectedHypervolumeImprovement
from botorch.acquisition.multi_objective.logei import (
    qLogNoisyExpectedHypervolumeImprovement,
)
from botorch.models import SaasFullyBayesianSingleTaskGP

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.simulation.Scenario as sc
from examples.simple_simulation_call import evaluate

# IMPORTS
from factory_flexibility_model.io import factory_import as imp
from factory_flexibility_model.simulation import Simulation as fs

import atexit

proc: list[Process] = []

from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.utils.measurement.synthetic_functions import hartmann6


def cleanup():
    global proc
    print("Cleaning up...")
    for p in proc:
        p.kill()
        p.terminate()


def sigHandler(signo, frame):
    sys.exit(0)


def run_optimizer():
    ax_client = AxClient(
        generation_strategy=GenerationStrategy(
            steps=[
                GenerationStep(
                    model=Models.SOBOL,
                    num_trials=5,  # How many trials should be produced from this generation step
                    min_trials_observed=3,  # How many trials need to be completed to move to next model
                    max_parallelism=psutil.cpu_count(
                        logical=False
                    ),  # Max parallelism for this step
                    model_kwargs={},  # Any kwargs you want passed into the model
                    model_gen_kwargs={},  # Any kwargs you want passed to `modelbridge.gen`
                ),
                GenerationStep(
                    model=Models.BOTORCH_MODULAR,
                    model_kwargs={
                        "surrogate": Surrogate(SaasFullyBayesianSingleTaskGP),
                        "botorch_acqf_class": qLogNoisyExpectedHypervolumeImprovement,
                    },
                    num_trials=-1,
                    max_parallelism=8,
                ),
            ]
        )
    )
    ax_client.create_experiment(
        name="SPIES_USE_CASE",
        parameters=[
            {
                "name": "storage_size",
                "type": "range",
                "bounds": [0.0, 3000.0],
                "value_type": "float",
            },
            {
                "name": "grid_capacity",
                "type": "range",
                "bounds": [0.0, 1600.0],
                "value_type": "float",
            },
            {
                "name": "storage_power",
                "type": "range",
                "bounds": [0.0, 6000.0],
                "value_type": "float",
            },
            {
                "name": "pv_capacity",
                "type": "range",
                "bounds": [0.0, 3600.0],
                "value_type": "float",
            },
            {
                "name": "forklift_count",
                "type": "range",
                "bounds": [1, 4],
                "value_type": "int",
            },
            {
                "name": "excavator_count",
                "type": "range",
                "bounds": [1, 3],
                "value_type": "int",
            },
        ],
        objectives={
            "capex": ObjectiveProperties(minimize=True),
            "emissions": ObjectiveProperties(minimize=True),
        },
        parameter_constraints=None,
        outcome_constraints=None,
    )

    queue = multiprocessing.Queue()
    for i in range(100):

        ret = ax_client.get_next_trials(12)
        parameters_trial_index = ret[0]
        print(f"Got {len(parameters_trial_index)} new trials\n\n")

        for trial_index, params in parameters_trial_index.items():
            process = Process(
                target=evaluate,
                args=(
                    params,
                    trial_index,
                    queue,
                ),
            )
            process.start()

        n_result = 0
        while n_result < len(parameters_trial_index):
            res = queue.get(block=True)
            n_result += 1
            ax_client.complete_trial(trial_index=res["idx"], raw_data=res["res"])

    ax_client.save_to_json_file()
    ax_client.get_pareto_optimal_parameters()


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
    simulation.simulate(
        interval_length=730, threshold=0.000001, solver_config={"log_solver": False}
    )
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
