# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: solve.py
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
import time
import gurobipy as gp
from gurobipy import GRB
import factory_flexibility_model.io.input_validations as iv


# CODE START
def solve(simulation, solver_config):
    """
    This function calls the gurobi.optimize routine that solves the optimization problem. all configurations handed over in solver_config are adapted.
    :param simulation: [simulation-object]
    :param solver_config: [dict] dictionary with parameter/value combinations specifying configurations for the gurobi solver
    """

    # adjust gurobi configuration if the problem is non-convex / quadratic
    if simulation.problem_class["grade"] > 1:
        simulation.m.params.NonConvex = 2

    # set maximum runtime if specified
    if "max_solver_time" in solver_config:
        simulation.m.setParam(
            GRB.Param.TimeLimit,
            iv.validate(solver_config["max_solver_time"], "float"),
        )

    # set solver method if specified
    if "solver_method" in solver_config:
        simulation.m.setParam(
            gp.GRB.Param.Method, iv.validate(solver_config["solver_method"], "int")
        )

    # set barrier solve tolerance if specified
    if "barrier_tolerance" in solver_config:
        simulation.m.setParam(
            gp.GRB.Param.BarConvTol,
            iv.validate(solver_config["barrier_tolerance"], "0..1"),
        )

    # set MIP gap if specified
    if "mip_gap" in solver_config:
        simulation.m.setParam(
            'MIPGap', iv.validate(solver_config["mip_gap"], "0..1"),
        )

    # CALL SOLVER
    logging.info(f"CALLING THE SOLVER")
    simulation.m.optimize()
    if simulation.enable_time_tracking:
        logging.info(f"Solver Time: {round(time.time() - simulation.t_step, 2)}s")
        simulation.t_step = time.time()
