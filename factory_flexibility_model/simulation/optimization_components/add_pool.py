#  CALLING PATH:
#  -> Simulation.simulate() -> Simulation.create_optimization_problem()

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
