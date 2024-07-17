# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_converter.py
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
def add_converter(simulation, component, t_start, t_end):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the converter handed over as 'Component'

    :param component: components.converter-object
    :return: simulation.m is being extended
    """
    interval_length = t_end - t_start + 1

    # create a timeseries of decision variables to represent the utilization U(t)
    simulation.MVars[f"P_{component.key}"] = simulation.m.addMVar(
        interval_length, vtype=GRB.CONTINUOUS, name=f"P_{component.name}"
    )
    logging.debug(
        f"        - Variable:     {component.name} (timeseries of the nominal power of {component.name})"
    )

    # add variables to express the positive and negative deviations from the nominal operating point
    simulation.MVars[f"P_{component.key}_devpos"] = simulation.m.addMVar(
        interval_length, vtype=GRB.CONTINUOUS, name=f"P_{component.name}_devpos"
    )
    simulation.MVars[f"P_{component.key}_devneg"] = simulation.m.addMVar(
        interval_length, vtype=GRB.CONTINUOUS, name=f"P_{component.name}_devneg"
    )

    # is the operating power of the converter limited? If yes: add power_max and power_min constraints
    if component.power_max_limited:
        simulation.m.addConstr(
            simulation.MVars[f"P_{component.key}"]
            <= component.power_max[t_start : t_end + 1]
            * component.availability[t_start : t_end + 1]
        )
        logging.debug(
            f"        - Constraint:   {component.key} <= {component.name}_max"
        )

    if component.power_min_limited:
        simulation.m.addConstr(
            simulation.MVars[f"P_{component.key}"]
            >= component.power_min[t_start : t_end + 1]
            * component.availability[t_start : t_end + 1]
        )
        logging.debug(f"        - Constraint:   {component.key} >= {component.key}_min")

    # Calculate the efficiency of operation for each timestep based on the deviations
    simulation.MVars[f"Eta_{component.key}"] = simulation.m.addMVar(
        interval_length, vtype=GRB.CONTINUOUS, name=f"Eta_{component.name}"
    )
    logging.debug(
        f"        - Variable:     {component.name}                              "
        f"(Operating efficiency of {component.name}"
    )

    if component.eta_variable:
        if simulation.problem_class["grade"] < 2:
            simulation.problem_class["grade"] = 2
        simulation.m.addConstrs(
            simulation.MVars[f"Eta_{component.key}"][t]
            == component.eta_max
            - simulation.MVars[f"P_{component.key}_devpos"][t]
            * component.delta_eta_high
            - simulation.MVars[f"P_{component.key}_devneg"][t] * component.delta_eta_low
            for t in range(interval_length)
        )
        logging.debug(f"        - Constraint:   Calculate Eta(t) for {component.name}")
    else:
        simulation.m.addConstrs(
            simulation.MVars[f"Eta_{component.key}"][t] == 1
            for t in range(interval_length)
        )
        logging.debug(f"        - Constraint:   {component.name} fixed to 100%")

    # calculate the absolute operating point out of the nominal operating point, the deviations and the switching state
    # Can the Converter be turned on/off regardless of the power constraints?
    if component.switchable:
        simulation.problem_class["type"] = "mixed integer"
        # introduce a variable representing the switching state of the converter
        simulation.MVars[f"Bool_{component.key}_state"] = simulation.m.addMVar(
            interval_length, vtype=GRB.BINARY, name=f"{component.name}_state"
        )

        # calculate the operating point concerning the switching state
        simulation.m.addConstrs(
            simulation.MVars[f"P_{component.key}"][t]
            == (
                component.power_nominal
                - simulation.MVars[f"P_{component.key}_devneg"][t]
                + simulation.MVars[f"P_{component.key}_devpos"][t]
            )
            * simulation.MVars[f"Bool_{component.key}_state"][t]
            for t in range(interval_length)
        )
    else:
        # calculate the operating point without a switching state
        simulation.m.addConstr(
            simulation.MVars[f"P_{component.key}"]
            == component.power_nominal
            - simulation.MVars[f"P_{component.key}_devneg"]
            + simulation.MVars[f"P_{component.key}_devpos"]
        )

    # set ramping constraints if needed:
    if component.ramp_power_limited:
        simulation.m.addConstr(
            simulation.MVars[f"P_{component.key}"][1:interval_length]
            <= simulation.MVars[f"P_{component.key}"][0 : interval_length - 1]
            + component.power_ramp_max_pos
        )  # restrict ramping up
        simulation.m.addConstr(
            simulation.MVars[f"P_{component.key}"][1:interval_length]
            >= simulation.MVars[f"P_{component.key}"][0 : interval_length - 1]
            - component.power_ramp_max_neg
        )  # restrict ramping down
        logging.debug(
            f"        - Constraint:   Ramping constraints for {component.name}"
        )

    # set the flows of incoming connections
    for connection in component.inputs:
        simulation.m.addConstr(
            simulation.MVars[connection.key]
            == simulation.MVars[f"P_{component.key}"]
            * connection.weight
            * simulation.interval_length
        )

    # set the flows of outgoing connections
    for connection in component.outputs:
        if connection.flowtype.is_energy():
            simulation.m.addConstr(
                simulation.MVars[connection.key]
                == simulation.MVars[f"P_{component.key}"]
                * connection.weight
                * simulation.interval_length
                * simulation.MVars[f"Eta_{component.key}"]
            )
            logging.debug(
                f"        - Added energy output calculation with losses for {connection.name}"
            )
        else:
            simulation.m.addConstr(
                simulation.MVars[connection.key]
                == simulation.MVars[f"P_{component.key}"]
                * connection.weight
                * simulation.interval_length
            )
            logging.debug(
                f"        - Added material output calculation for {connection.name}"
            )

    # calculate the resulting energy losses: losses(t) = sum(inputs(t)) - sum(outputs(t))
    simulation.m.addConstr(
        simulation.MVars[component.to_Elosses.key]
        == sum(simulation.MVars[input_i.key] for input_i in component.inputs_energy)
        - sum(simulation.MVars[output_i.key] for output_i in component.outputs_energy)
    )

    # calculate the resulting material losses: losses(t) = sum(inputs(t)) - sum(outputs(t))
    if not component.to_Mlosses == []:
        simulation.m.addConstr(
            simulation.MVars[component.to_Mlosses.key]
            == sum(
                simulation.MVars[input_i.key] for input_i in component.inputs_material
            )
            - sum(
                simulation.MVars[output_i.key]
                for output_i in component.outputs_material
            )
        )

    # is the converter afflicted with a ramping charge?
    if component.rampup_cost > 0:
        # If yes: Add an MVar for calculating the occuring rampups
        # create single float Mvar
        simulation.MVars[f"P_rampup_{component.key}"] = simulation.m.addMVar(
            interval_length - 1,
            vtype=GRB.CONTINUOUS,
            lb=0,
            name=f"P_rampup_{component.key}",
        )

        # define the Mvar as the realized rampup
        simulation.m.addConstrs(
            simulation.MVars[f"P_rampup_{component.key}"]
            >= simulation.MVars[f"P_{component.key}"][t + 1]
            - simulation.MVars[f"P_{component.key}"][t]
            for t in range(interval_length - 1)
        )

        # create new cost term
        simulation.C_objective.append(
            simulation.m.addMVar(
                1, vtype=GRB.CONTINUOUS, name=f"C_rampup_{component.key}"
            )
        )

        # define the cost term
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == gp.quicksum(simulation.MVars[f"P_rampup_{component.key}"])
            * component.rampup_cost
        )

        logging.debug(f"        - CostFactor:   Cost for ramping of {component.name}")

    # is the converter afflicted with a capacity charge?
    if component.capacity_charge > 0:
        # If yes: Add an MVar for the maximum used Power and add cost factor
        # create single float Mvar
        simulation.MVars[f"P_max_{component.key}"] = simulation.m.addMVar(
            1, vtype=GRB.CONTINUOUS, name=f"P_max_{component.key}"
        )

        # define the Mvar as the maximum used utilization
        simulation.m.addConstr(
            simulation.MVars[f"P_max_{component.key}"][0]
            == gp.max_(
                (
                    simulation.MVars[f"P_{component.key}"][t]
                    for t in range(interval_length)
                ),
                constant=0,
            )
        )

        # create new cost term
        simulation.C_objective.append(
            simulation.m.addMVar(
                1, vtype=GRB.CONTINUOUS, name=f"C_Capacity_{component.key}"
            )
        )

        # define the costs -> capacity_charge is specified on yearly basis and has to be broken down to simulation timeframe
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == simulation.interval_length
            * interval_length
            / 8760
            * component.capacity_charge
            * simulation.MVars[f"P_max_{component.key}"]
        )

        logging.debug(
            f"        - CostFactor:   Cost for capital costs of {component.name}"
        )
