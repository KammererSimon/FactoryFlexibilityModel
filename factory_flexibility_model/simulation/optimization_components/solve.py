#  CALLING PATH:
#  -> Simulation.simulate()

# IMPORTS
import logging
import time

import gurobipy as gp
from gurobipy import GRB

import factory_flexibility_model.io.input_validations as iv


# CODE START
def solve(simulation, solver_config):
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

    # CALL SOLVER
    logging.info(f"CALLING THE SOLVER")
    simulation.m.optimize()
    if simulation.enable_time_tracking:
        logging.info(f"Solver Time: {round(time.time() - simulation.t_step, 2)}s")
        simulation.t_step = time.time()
