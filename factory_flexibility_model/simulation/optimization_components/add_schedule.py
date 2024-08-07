# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_schedule.py
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
import numpy as np
from gurobipy import GRB


# CODE START
def add_schedule(simulation, component, t_start, t_end):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the schedule handed over as 'Component'
    :param component: components.schedule-object
    :return: simulation.m is beeing extended
    """

    interval_length = t_end - t_start + 1
    # get number of individual flexible demands:
    rows = len(component.demands)

    # create availability matrix for the demands
    availability = np.ones((interval_length, rows))
    for row in range(rows):
        for column in range(
            int(component.demands[row, 0]), int(component.demands[row, 1]) + 1
        ):
            availability[column - 1, row] = 0
    simulation.MVars[f"X_{component.key}_availability"] = availability

    # create decision variables for the demands
    simulation.MVars[f"E_{component.key}_in"] = simulation.m.addMVar(
        (interval_length, rows), vtype=GRB.CONTINUOUS, name=f"{component.name}_Pin"
    )
    logging.debug(
        f"        - Variable(s):  Energy_in for {rows} part demands of {component.name}"
    )

    # define constraint: input and output must be equal at any timestep to ensure, that the Component just does flowtype control
    simulation.m.addConstrs(
        simulation.MVars[component.outputs[0].key][t]
        == simulation.MVars[component.inputs[0].key][t]
        for t in range(interval_length)
    )
    logging.debug(f"        - Constraint:   Energy_in == Energy_out for {component.name}")

    # define constraint: taken inputs for demand fulfillment must equal the used input in every timestep
    simulation.m.addConstrs(
        gp.quicksum(simulation.MVars[f"E_{component.key}_in"][t][:])
        == simulation.MVars[component.inputs[0].key][t]
        for t in range(interval_length)
    )
    logging.debug(
        f"        - Constraint:   Energy demands must be fed by inputs within {component.name}"
    )

    # define constraint: each part demand must have its individual demand fulfilled
    simulation.m.addConstrs(
        gp.quicksum(simulation.MVars[f"E_{component.key}_in"][0 : interval_length, i])
        == component.demands[i, 2]
        for i in range(rows)
    )
    logging.debug(
        f"        - Constraint:   Each part demand of {component.name} must have its demand fulfilled"
    )

    # define constraint: part demands are only allowed to be fed while available
    simulation.m.addConstrs(
        simulation.MVars[f"E_{component.key}_in"][0 : interval_length, i]
        @ availability[0 : interval_length, i]
        == 0
        for i in range(rows)
    )
    logging.debug(
        f"        - Constraint:   Part demands of {component.name} can only be fed when available"
    )

    # define constraint: adhere power_max constraints per part demand
    simulation.m.addConstrs(
        simulation.MVars[f"E_{component.key}_in"][t, i] / simulation.interval_length
        <= component.demands[i, 3]
        for t in range(interval_length)
        for i in range(rows)
    )
    logging.debug(
        f"        - Constraint:   Adhere the power_max constraints for every part demand of {component.name}"
    )

    # define constraint: adhere power_max for total power if needed
    if component.power_max_limited:
        simulation.m.addConstrs(
            gp.quicksum(simulation.MVars[f"E_{component.key}_in"][t][:])
            / simulation.interval_length
            <= component.power_max[t]
            for t in range(interval_length)
        )
        logging.debug(
            f"        - Constraint:   power_total(t) <= power_max for {component.name}"
        )

    return (
        simulation.m,
        simulation.MVars,
        simulation.C_objective,
        simulation.R_objective,
    )
