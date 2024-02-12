#  CALLING PATH:
#  -> Simulation.simulate() -> Simulation.create_optimization_problem()

# IMPORTS
import logging

from gurobipy import GRB


# CODE START
def add_slack(simulation, component):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the slack handed over as 'Component'
    :param component: components.slack-object
    :return: simulation.m is beeing extended
    """
    # slacks don't need any power restrictions or other constraints.
    # All they basically have to do is to be usable in any situation but be very expensive then.
    # So just two cost terms are being created here

    # add a cost term for negative slack usage to the target function
    for i in range(len(component.inputs)):
        simulation.C_objective.append(
            simulation.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}_neg")
        )
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == component.cost[0 : simulation.T]
            @ simulation.MVars[component.inputs[i].key][0 : simulation.T]
        )
        logging.debug(f"        - CostFactor:   C_{component.key}_negative")

    # add a cost term for negative slack usage to the target function
    for i in range(len(component.outputs)):
        simulation.C_objective.append(
            simulation.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}_pos")
        )
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == component.cost[0 : simulation.T]
            @ simulation.MVars[component.outputs[i].key][0 : simulation.T]
        )
        logging.debug(f"        - CostFactor:   C_{component.key}_positive")
