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
import datetime
import logging
import os
import signal
import sys
import threading
import webbrowser
from multiprocessing import Process
from wsgiref.simple_server import make_server

import optuna
from optuna_dashboard import wsgi

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.simulation.Scenario as sc
from examples import bayesian_sampler
from examples.simple_simulation_call import simulate
# IMPORTS
from factory_flexibility_model.io import factory_import as imp
from factory_flexibility_model.simulation import Simulation as fs

import atexit
proc: list[Process] = []


def cleanup():
    global proc
    print("Cleaning up...")
    for p in proc:
        p.kill()
        p.terminate()


def sigHandler(signo, frame):
    sys.exit(0)


def run_optimizer():
    global proc, thread
    atexit.register(cleanup)
    signal.signal(signal.SIGTERM, sigHandler)
    signal.signal(signal.SIGINT, sigHandler)

    val = input("Enter your postgres password: ")
    storage = optuna.storages.RDBStorage(f"postgresql://postgres:{val}@localhost:5432/ffm")
    sampler = optuna.integration.BoTorchSampler(
        candidates_func=bayesian_sampler.singletask_qehvi_candidates_func,
        n_startup_trials=5,
        independent_sampler=optuna.samplers.QMCSampler(),
    )
    search_space = {"storage_size": range(0, 3000,100),
                    "grid_capacity": range(0, 1600,100),
                    #"pv_capacity": range(0, 3600, 200),
                    #"storage_power": range(0, 6000, 200),  #TODO: prüfen und uncomment
                    #"qnt_forklifts": [1, 2, 3, 4],
                    #"qnt_excavators": [1, 2, 3]
                    }


    study = optuna.create_study(
        storage=storage,
        directions=["minimize", "minimize"],
        study_name=f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}_FFM",
        sampler=optuna.samplers.GridSampler(search_space)
    )

    app = wsgi(storage)
    httpd = make_server("localhost", 8080, app)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    webbrowser.open("http://localhost:8080/", new=0, autoraise=True)

    for i in range(24):
        p = Process(target=study.optimize, args=(simulate,), kwargs={"n_trials": 20})
        p.start()
        proc.append(p)
        print(f"Started Process {i}")
    for p in proc:
        p.join()


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


def optuna_dashboard():
    val = input("Enter your postgres password: ")
    storage = optuna.storages.RDBStorage(f"postgresql://postgres:{val}@localhost:5432/ffm")
    app = wsgi(storage)
    httpd = make_server("localhost", 8080, app)
    webbrowser.open("http://localhost:8080/", new=0, autoraise=True)
    httpd.serve_forever()
