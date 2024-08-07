# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_thermalsystem.py
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

# IMPORTS
import logging

import gurobipy as gp
from gurobipy import GRB


# CODE START
def add_thermalsystem(simulation, component, t_start, t_end):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the thermalsystem handed over as 'Component'
    :param component: components.thermalsystem-object
    :return: simulation.m is beeing extended
    """
    interval_length = t_end - t_start + 1

    # create a timeseries of decision variables to represent the total inflow going into the thermal demand:
    simulation.MVars[f"E_{component.key}_in"] = simulation.m.addMVar(
        interval_length, vtype=GRB.CONTINUOUS, name=f"E_{component.key}_in"
    )
    simulation.m.addConstrs(
        (
            simulation.MVars[f"E_{component.key}_in"][t]
            == gp.quicksum(
                simulation.MVars[component.inputs[input_id].key][t]
                for input_id in range(len(component.inputs))
            )
        )
        for t in range(interval_length)
    )
    logging.debug(
        f"        - Variable:     {component.name}_in                                 (timeseries of incoming thermal energy at {component.name})"
    )

    # create a timeseries of decision variables to represent the total outflow going out of the thermal demand:
    simulation.MVars[f"E_{component.key}_out"] = simulation.m.addMVar(
        interval_length, vtype=GRB.CONTINUOUS, name=f"E_{component.key}_out"
    )
    simulation.m.addConstrs(
        (
            simulation.MVars[f"E_{component.key}_out"][t]
            == gp.quicksum(
                simulation.MVars[component.outputs[output_id].key][t]
                for output_id in range(len(component.outputs))
            )
        )
        for t in range(interval_length)
    )
    logging.debug(
        f"        - Variable:     {component.name}_out                                  (timeseries of removed thermal energy at {component.name})"
    )

    # create a timeseries for the internal temperature:
    simulation.MVars[f"T_{component.key}"] = simulation.m.addMVar(
        interval_length, vtype=GRB.CONTINUOUS, name=f"T_{component.key}"
    )
    logging.debug(
        f"        - Variable:     {component.key}                                  (Internal Temperature of {component.name})"
    )

    # set the starting temperature:
    if component.temperature_start is None:
        temperature_start = (min(component.temperature_min)+max(component.temperature_max))/2
    else:
        temperature_start = component.temperature_start

    simulation.m.addConstr(
        simulation.MVars[f"T_{component.key}"][0] == temperature_start)
    logging.debug(f"        - Constraint:   {component.name}[0] = {temperature_start}")


    # add constraint for the thermal R-C-factory
    simulation.m.addConstrs(
        (
            simulation.MVars[f"T_{component.key}"][t]
            == simulation.MVars[f"T_{component.key}"][t - 1]
            + (  # t-1 temperature
                component.temperature_ambient[t - 1]
                - simulation.MVars[f"T_{component.key}"][t - 1]
            )
            * simulation.time_reference_factor
            / (component.R * component.C)
            + (  # thermal inertia
                simulation.MVars[f"E_{component.key}_in"][t - 1]
                - simulation.MVars[f"E_{component.key}_out"][t - 1]
            )
            * simulation.time_reference_factor
            / component.C
        )
        for t in range(1, interval_length)
    )  # heating/cooling impact

    # keep the temperature within the allowed boundaries during Simulation interval:
    simulation.m.addConstrs(
        (simulation.MVars[f"T_{component.key}"][t] >= component.temperature_min[t])
        for t in range(interval_length)
    )
    simulation.m.addConstrs(
        (simulation.MVars[f"T_{component.key}"][t] <= component.temperature_max[t])
        for t in range(interval_length)
    )
    logging.debug(
        f"        - Constraint:   Tmin < T_{component.name} < Tmax for {component.name}"
    )

    # set the end temperature:
    if component.sustainable:
        simulation.m.addConstr(
            simulation.MVars[f"T_{component.key}"][interval_length - 1]
            + (
                component.temperature_ambient[interval_length - 1]
                - simulation.MVars[f"T_{component.key}"][interval_length - 1]
            )
            * simulation.time_reference_factor
            / (component.R * component.C)
            + (
                simulation.MVars[f"E_{component.key}_in"][interval_length - 1]
                - simulation.MVars[f"E_{component.key}_out"][interval_length - 1]
            )
            * simulation.time_reference_factor
            / component.C
            == temperature_start
        )
        logging.debug(f"        - Constraint:   T_{component.name}[T] = Tstart")
    else:
        # keep the temperature within allowed boundaries at timestep T+1
        simulation.m.addConstr(
            simulation.MVars[f"T_{component.key}"][interval_length - 1]
            + (
                component.temperature_ambient[interval_length - 1]
                - simulation.MVars[f"T_{component.key}"][interval_length - 1]
            )
            * simulation.time_reference_factor
            / (component.R * component.C)
            + (
                simulation.MVars[f"E_{component.key}_in"][interval_length - 1]
                - simulation.MVars[f"E_{component.key}_out"][interval_length - 1]
            )
            * simulation.time_reference_factor
            / component.C
            >= component.temperature_min[interval_length - 1]
        )

        simulation.m.addConstr(
            simulation.MVars[f"T_{component.key}"][interval_length - 1]
            + (
                component.temperature_ambient[interval_length - 1]
                - simulation.MVars[f"T_{component.key}"][interval_length - 1]
            )
            * simulation.time_reference_factor
            / (component.R * component.C)
            + (
                simulation.MVars[f"E_{component.key}_in"][interval_length - 1]
                - simulation.MVars[f"E_{component.key}_out"][interval_length - 1]
            )
            * simulation.time_reference_factor
            / component.C
            <= component.temperature_max[interval_length - 1]
        )

    # calculate the losses:
    simulation.m.addConstrs(
        simulation.MVars[component.to_losses.key][t]
        - simulation.MVars[component.from_gains.key][t]
        == (
            simulation.MVars[f"T_{component.key}"][t] - component.temperature_ambient[t]
        )
        * simulation.time_reference_factor
        / component.R
        for t in range(interval_length)
    )

    logging.debug(
        f"        - Constraint:     calculation of thermal losses for {component.name}"
    )
