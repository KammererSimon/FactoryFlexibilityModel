# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_pool.py
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


# CODE START
def add_pool(simulation, component):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the pool handed over as 'Component'
    :param component: components.pool-object
    :return: simulation.m is beeing extended
    """
    # create constraint that ensures, that the sum of inputs equals the sum of outputs in every timestep
    simulation.m.addConstr(
        gp.quicksum(
            simulation.MVars[component.inputs[input_id].key]
            for input_id in range(len(component.inputs))
        )
        == gp.quicksum(
            simulation.MVars[component.outputs[output_id].key]
            for output_id in range(len(component.outputs))
        )
    )
    logging.debug(
        f"        - Constraint:   Energy equilibrium for Pool {component.name}"
    )
