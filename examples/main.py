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
from collections import deque
from multiprocessing import Process
from numbers import Number
from typing import Iterable

import numpy as np
import psutil
import torch
from ax.modelbridge.cross_validation import cross_validate
from ax.modelbridge.modelbridge_utils import observed_pareto_frontier
from ax.models.torch.botorch_modular.surrogate import Surrogate
from ax.plot.contour import interact_contour
from ax.plot.diagnostic import interact_cross_validation
from ax.plot.pareto_frontier import plot_pareto_frontier
from ax.plot.pareto_utils import (
    get_tensor_converter_model,
    get_observed_pareto_frontiers,
)
from ax.modelbridge.modelbridge_utils import observed_pareto_frontier
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
    observed_pareto_frontier_data = get_observed_pareto_frontiers(
        experiment=ax_client.experiment,
        data=ax_client.experiment.fetch_data(),
    )[0]
    render(plot_pareto_frontier(observed_pareto_frontier_data, CI_level=0.90))

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


def generate_volatilities(number_of_years: int) -> Iterable[Number]:
    return [1] * number_of_years


def simulate_scalarized(
    parameterization, index: int, trial_index: int, queue: multiprocessing.Queue
):
    queue.put(
        {
            "idx": index,
            "t_idx": trial_index,
            "res": {
                "quality": (parameterization.get("input"), 0.0),
            },
        }
    )
    print(f"Process {index} produced a result.")
    pass


def create_scalarized_experiment(index: int, volatility: Number) -> AxClient:
    storage_name = f"{time.strftime("%Y%m%d-%H%M%S")}_snapshot.json"
    ax_client = AxClient(torch_device=torch.device("cuda"))
    ax_client.create_experiment(
        name=f"experiment_{index}",
        parameters=[
            {
                "name": "input",
                "type": "range",
                "bounds": [0.0, 3000.0],
                "value_type": "float",
            },
        ],
        objectives={
            "quality": ObjectiveProperties(minimize=True),
        },
        parameter_constraints=None,
        outcome_constraints=None,
        overwrite_existing_experiment=True,
    )
    return ax_client


def simulate_multiyear_scalarized():
    import logging
    from ax.utils.common.logger import ROOT_STREAM_HANDLER

    ROOT_STREAM_HANDLER.setLevel(logging.CRITICAL)

    output_folder = f"{time.strftime("%Y%m%d-%H%M%S")}_output"
    os.makedirs(output_folder, exist_ok=True)
    os.chdir(output_folder)
    current_year = 2024
    number_of_years = 12
    max_parallelism = 3
    cpus = psutil.cpu_count(logical=False)
    volatilities = generate_volatilities(number_of_years)

    experiments: list[AxClient] = [
        create_scalarized_experiment(current_year + i, volatilities[i])
        for i in range(number_of_years)
    ]
    experiments: dict[int, tuple[AxClient, int]] = {
        i: (experiments[i], 0, 0) for i in range(len(experiments))
    }
    queue = multiprocessing.Queue()
    active_processes = 0
    max_trials = 100
    while experiments:
        if (
            active_processes >= cpus
            # Returns the amount of running instances of the year with the least running instances
            or list(sorted(experiments.items(), key=lambda item: item[1][2]))[0][1][2]
            >= max_parallelism
        ):
            # This is not thread-safe, but it doesn't need to be
            # We just want to clean out the result queue as much as possible
            res = queue.get(block=True)
            handle_simulation_result(experiments, max_trials, res)
            active_processes -= 1
            while not queue.empty():
                res = queue.get(block=True)
                handle_simulation_result(experiments, max_trials, res)
                active_processes -= 1

        # Returns the year which currently has the fewest running instances
        next_index = list(sorted(experiments.items(), key=lambda item: item[1][2]))[0][
            0
        ]
        experiment: AxClient
        experiment, arms, current_proc_count = experiments[next_index]
        # Getting next trial can't really be parallelized simply without running each year as a fully independent thing
        # Technically you can parallelize this function and then parallelize again in the parallelized stuff and still
        # balance, but it seems like rather little gain for the effort
        # At no computation for evaluating we hit 76% utilisation for instance
        # On a server, fitting the model will take up the slack, because there probably won't be CUDA
        # And numpy will grab all cores to get next trials
        parameterization, trial_index = experiment.get_next_trial()
        process = Process(
            target=simulate_scalarized,
            args=(
                parameterization,
                next_index,
                trial_index,
                queue,
            ),
        )
        process.start()

        # Update current stats
        current_proc_count += 1
        experiments[next_index] = (experiment, arms, current_proc_count)
        active_processes += 1


def handle_simulation_result(experiments, max_trials, res):
    experiment: AxClient
    experiment, completed_arms, current_proc_count = experiments[res["idx"]]
    experiment.complete_trial(trial_index=res["t_idx"], raw_data=res["res"])
    completed_arms += 1
    current_proc_count -= 1
    if completed_arms == max_trials:
        del experiments[res["idx"]]
    else:
        experiments[res["idx"]] = (experiment, completed_arms, current_proc_count)
