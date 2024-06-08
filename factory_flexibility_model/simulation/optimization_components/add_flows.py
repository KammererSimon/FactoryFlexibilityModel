#  CALLING PATH:
#  -> Simulation.simulate() -> Simulation.create_optimization_problem()

# IMPORTS
import logging

from gurobipy import GRB


# CODE START
def add_flows(simulation, interval_length):
    """This function adds a MVar for the flowtype on every existing connection to te optimization problem
    :return: self.m is beeing extended
    """
    # iterate over all existing connections
    for connection in simulation.factory.connections.values():
        # create a timeseries of decision variables for the flowtype on every connection in the graph
        simulation.MVars[connection.key] = simulation.m.addMVar(
            interval_length, vtype=GRB.CONTINUOUS, name=connection.key
        )

        logging.debug(
            f"        - Variable:     {connection.name}                                (timeseries of flowtype on connection {connection.name})"
        )
