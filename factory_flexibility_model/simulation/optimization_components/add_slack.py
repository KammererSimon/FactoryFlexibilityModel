# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_slack.py
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

from gurobipy import GRB


# CODE START
def add_slack(simulation, component, t_start, t_end):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the slack handed over as 'Component'
    :param component: components.slack-object
    :return: simulation.m is beeing extended
    """
    # slacks don't need any power restrictions or other constraints.
    # All they basically have to do is to be usable in any situation but be very expensive then.
    # So just two cost terms are being created here

    interval_length = t_end - t_start + 1

    # add a cost term for negative slack usage to the target function
    for i in range(len(component.inputs)):
        simulation.C_objective.append(
            simulation.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}_neg")
        )
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == component.cost[0 : interval_length]
            @ simulation.MVars[component.inputs[i].key][0 : interval_length]
        )
        logging.debug(f"        - CostFactor:   C_{component.key}_negative")

    # add a cost term for negative slack usage to the target function
    for i in range(len(component.outputs)):
        simulation.C_objective.append(
            simulation.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}_pos")
        )
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == component.cost[0 : interval_length]
            @ simulation.MVars[component.outputs[i].key][0 : interval_length]
        )
        logging.debug(f"        - CostFactor:   C_{component.key}_positive")
