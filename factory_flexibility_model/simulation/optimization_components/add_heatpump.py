# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_heatpump.py
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
def add_heatpump(simulation, component, t_start, t_end):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the heatpump handed over as 'Component'

    :param component: components.heatpump-object
    :return: simulation.m is beeing extended
    """

    interval_length = t_end-t_start+1

    # create a timeseries of decision variables to represent the utilization U(t)
    simulation.MVars[f"P_{component.key}"] = simulation.m.addMVar(interval_length, vtype=GRB.CONTINUOUS, name=f"P_{component.name}")
    logging.debug(f"        - Variable:     {component.name} (timeseries of the nominal power of {component.name})")

    # is the operating power of the heatpump limited? If yes: add power_max constraints
    if component.power_max_limited:
        simulation.m.addConstr(simulation.MVars[f"P_{component.key}"]<= component.power_max[t_start:t_end+1])
        logging.debug(f"        - Constraint:   {component.key} <= {component.name}_max")

    # set the flow coming from the main input
    simulation.m.addConstr(simulation.MVars[component.input_main.key] == simulation.MVars[f"P_{component.key}"])

    # set the flow coming from the gains input
    simulation.m.addConstr(simulation.MVars[component.input_gains.key] == simulation.MVars[f"P_{component.key}"] * (component.cop[t_start:t_end+1]-1))

    # set flow at output
    simulation.m.addConstr(simulation.MVars[component.outputs[0].key] == simulation.MVars[f"P_{component.key}"] * component.cop[t_start:t_end+1])