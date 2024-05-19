#  CALLING PATH:
#  -> Simulation.simulate() -> Simulation.create_optimization_problem()

# IMPORTS
import logging
import gurobipy as gp
from gurobipy import GRB


# CODE START
def add_heatpump(simulation, component):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the heatpump handed over as 'Component'

    :param component: components.heatpump-object
    :return: simulation.m is beeing extended
    """

    # create a timeseries of decision variables to represent the utilization U(t)
    simulation.MVars[f"P_{component.key}"] = simulation.m.addMVar(simulation.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}")
    logging.debug(f"        - Variable:     {component.name} (timeseries of the nominal power of {component.name})")

    # is the operating power of the heatpump limited? If yes: add power_max constraints
    if component.power_max_limited:
        simulation.m.addConstr(simulation.MVars[f"P_{component.key}"]<= component.power_max)
        logging.debug(f"        - Constraint:   {component.key} <= {component.name}_max")

    # set the flow coming from the main input
    simulation.m.addConstr(simulation.MVars[component.input_main.key] == simulation.MVars[f"P_{component.key}"])

    # set the flow coming from the gains input
    simulation.m.addConstr(simulation.MVars[component.input_gains.key] == simulation.MVars[f"P_{component.key}"] * (component.cop-1))

    # set flow at output
    simulation.m.addConstr(simulation.MVars[component.outputs[0].key] == simulation.MVars[f"P_{component.key}"] * component.cop)