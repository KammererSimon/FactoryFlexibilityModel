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

import logging
import multiprocessing
import os
import sys
import time
from multiprocessing import Process

import numpy as np
import torch
from ax.modelbridge.cross_validation import cross_validate
from ax.modelbridge.modelbridge_utils import observed_pareto_frontier
from ax.models.torch.botorch_modular.surrogate import Surrogate
from ax.plot.contour import interact_contour
from ax.plot.diagnostic import interact_cross_validation
from ax.plot.pareto_utils import (
    get_tensor_converter_model,
)
from ax.service.utils.report_utils import (
    _pareto_frontier_scatter_2d_plotly,
)
from ax.utils.notebook.plotting import render
from botorch.acquisition.multi_objective.logei import (
    qLogNoisyExpectedHypervolumeImprovement,
)
from botorch.models import SaasFullyBayesianSingleTaskGP
from matplotlib import pyplot as plt

import factory_flexibility_model.factory.Blueprint as bp
import factory_flexibility_model.simulation.Scenario as sc
from examples.simple_simulation_call import simulate_ax

# IMPORTS
from factory_flexibility_model.io import factory_import as imp
from factory_flexibility_model.simulation import Simulation as fs

proc: list[Process] = []

from ax.service.ax_client import AxClient, ObjectiveProperties


def cleanup():
    global proc
    print("Cleaning up...")
    for p in proc:
        p.kill()
        p.terminate()


def sigHandler(signo, frame):
    sys.exit(0)


def run_ax_optimizer():
    storage_name = f"{time.strftime("%Y%m%d-%H%M%S")}_snapshot.json"
    ax_client = AxClient(torch_device=torch.device("cuda"))
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
            "costs": ObjectiveProperties(minimize=True, threshold=500000),
            "emissions": ObjectiveProperties(minimize=True, threshold=90000),
        },
        parameter_constraints=None,
        outcome_constraints=None,
        overwrite_existing_experiment=True,
    )

    # Note that the transformation stack of the factory modelbridge already calls IntToFloat, UnitX, StandardizeY
    # This makes calling Standardize as output transform and Normalize and Round as Input Transform pointless.
    # Reverse UnitX should bring it to the optimized original space,
    # and reverse IntToFloat should do what round would have done
    ax_client.generation_strategy._steps[1].model_kwargs.update(
        {
            "surrogate": Surrogate(
                SaasFullyBayesianSingleTaskGP,
                # mll_options={
                #     "num_samples": 256,
                #     "warmup_steps": 512,
                # },
            ),
            "botorch_acqf_class": qLogNoisyExpectedHypervolumeImprovement,  # Or Noisy Variant
            "acquisition_options": {"prune_baseline": True},
        }
    )

    queue = multiprocessing.Queue()
    total_trials = 100
    while total_trials > 0:
        ret = ax_client.get_next_trials(24)
        parameters_trial_index = ret[0]
        print(f"Got {len(parameters_trial_index)} new trials\n\n")

        for trial_index, params in parameters_trial_index.items():
            process = Process(
                target=simulate_ax,
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
            total_trials -= 1

        ax_client.save_to_json_file(filepath=storage_name)

    ax_client.save_to_json_file(filepath=storage_name)


def ax_plot_results():
    val = input("Enter filename to load: ")
    ax_client = AxClient.load_from_json_file(val)
    ax_client.fit_model()
    model = ax_client.generation_strategy.model

    _pareto_frontier_scatter_2d_plotly(experiment=ax_client.experiment).show()
    mb = get_tensor_converter_model(
        experiment=ax_client.experiment, data=ax_client.experiment.lookup_data()
    )
    pareto_indices = [
        int(s.arm_name[:-2])
        for s in observed_pareto_frontier(
            modelbridge=mb,
            objective_thresholds=ax_client.experiment.optimization_config.objective_thresholds,
            # objective_thresholds=[
            #     ObjectiveThreshold(
            #         metric=ax_client.experiment.optimization_config.objective_thresholds[
            #             0
            #         ].metric.clone(),
            #         bound=9999999.0,
            #         relative=False,
            #     ),
            #     ObjectiveThreshold(
            #         metric=ax_client.experiment.optimization_config.objective_thresholds[
            #             1
            #         ].metric.clone(),
            #         bound=9999999.0,
            #         relative=False,
            #     ),
            # ],
        )
    ]

    cv_results = cross_validate(model)
    cross_validation_plot = interact_cross_validation(cv_results)
    render(cross_validation_plot)
    cost_contour_plot = interact_contour(model=model, metric_name="costs")
    for i, trace in enumerate(cost_contour_plot.data["data"]):
        if trace["type"] == "scatter":
            x = []
            y = []
            t = []
            for j in pareto_indices:
                x.append(trace["x"][j])
                y.append(trace["y"][j])
                t.append(trace["text"][j])
            cost_contour_plot.data["data"][i]["x"] = x
            cost_contour_plot.data["data"][i]["y"] = y
            cost_contour_plot.data["data"][i]["text"] = t
            cost_contour_plot.data["data"][i]["marker"]["opacity"] = 0.6
            cost_contour_plot.data["data"][i]["marker"]["color"] = "red"

    for i in range(len(cost_contour_plot.data["data"])):
        if "colorscale" not in cost_contour_plot.data["data"][i]:
            continue
        colorscale = np.asarray(cost_contour_plot.data["data"][i]["colorscale"])
        viridis = plt.cm.get_cmap("viridis", len(colorscale[:, 0]))
        colors = viridis(np.linspace(0, 1, len(colorscale[:, 0]))).tolist()
        for j in range(len(colors)):
            colors[j] = f"rgb{tuple([int(255.0*x) for x in colors[j]])}"
        cost_contour_plot.data["data"][i]["colorscale"] = colors

    render(cost_contour_plot)

    emission_contour_plot = interact_contour(model=model, metric_name="emissions")
    for i, trace in enumerate(emission_contour_plot.data["data"]):
        if trace["type"] == "scatter":
            x = []
            y = []
            t = []
            for j in pareto_indices:
                x.append(trace["x"][j])
                y.append(trace["y"][j])
                t.append(trace["text"][j])
            emission_contour_plot.data["data"][i]["x"] = x
            emission_contour_plot.data["data"][i]["y"] = y
            emission_contour_plot.data["data"][i]["text"] = t
            emission_contour_plot.data["data"][i]["marker"]["opacity"] = 0.6
            emission_contour_plot.data["data"][i]["marker"]["color"] = "red"
    for i in range(len(emission_contour_plot.data["data"])):
        if "colorscale" not in emission_contour_plot.data["data"][i]:
            continue
        colorscale = np.asarray(emission_contour_plot.data["data"][i]["colorscale"])
        viridis = plt.cm.get_cmap("viridis", len(colorscale[:, 0]))
        colors = viridis(np.linspace(0, 1, len(colorscale[:, 0]))).tolist()
        for j in range(len(colors)):
            colors[j] = f"rgb{tuple([int(255.0*x) for x in colors[j]])}"
        emission_contour_plot.data["data"][i]["colorscale"] = colors
    render(emission_contour_plot)

    render(ax_client.get_feature_importances())


# def run_optimizer():
#     global proc, thread
#     atexit.register(cleanup)
#     signal.signal(signal.SIGTERM, sigHandler)
#     signal.signal(signal.SIGINT, sigHandler)
#
#     val = input("Enter your postgres password: ")
#     storage = optuna.storages.RDBStorage(
#         f"postgresql://postgres:{val}@localhost:5432/ffm"
#     )
#
#     study = optuna.create_study(
#         storage=storage,
#         directions=["minimize", "minimize"],
#         study_name=f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}_FFM",
#         sampler=TPESampler(),
#     )
#
#     app = wsgi(storage)
#     httpd = make_server("localhost", 8080, app)
#     thread = threading.Thread(target=httpd.serve_forever)
#     thread.daemon = True
#     thread.start()
#     webbrowser.open("http://localhost:8080/", new=0, autoraise=True)
#
#     for i in range(24):
#         p = Process(target=study.optimize, args=(simulate,), kwargs={"n_trials": 8})
#         p.start()
#         proc.append(p)
#         print(f"Started Process {i}")
#     for p in proc:
#         p.join()


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


# def optuna_dashboard():
#     val = input("Enter your postgres password: ")
#     storage = optuna.storages.RDBStorage(
#         f"postgresql://postgres:{val}@localhost:5432/ffm"
#     )
#     app = wsgi(storage)
#     httpd = make_server("localhost", 8080, app)
#     webbrowser.open("http://localhost:8080/", new=0, autoraise=True)
#     httpd.serve_forever()
