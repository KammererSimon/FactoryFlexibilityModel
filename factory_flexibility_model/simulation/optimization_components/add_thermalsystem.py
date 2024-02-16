#  CALLING PATH:
#  -> Simulation.simulate() -> Simulation.create_optimization_problem()

# IMPORTS
import logging

import gurobipy as gp
from gurobipy import GRB


# CODE START
def add_thermalsystem(simulation, component):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the thermalsystem handed over as 'Component'
    :param component: components.thermalsystem-object
    :return: simulation.m is beeing extended
    """
    # create a timeseries of decision variables to represent the total inflow going into the thermal demand:
    simulation.MVars[f"E_{component.key}_in"] = simulation.m.addMVar(
        simulation.T, vtype=GRB.CONTINUOUS, name=f"E_{component.key}_in"
    )
    simulation.m.addConstrs(
        (
            simulation.MVars[f"E_{component.key}_in"][t]
            == gp.quicksum(
                simulation.MVars[component.inputs[input_id].key][t]
                for input_id in range(len(component.inputs))
            )
        )
        for t in range(simulation.T)
    )
    logging.debug(
        f"        - Variable:     {component.name}_in                                 (timeseries of incoming thermal energy at {component.name})"
    )

    # create a timeseries of decision variables to represent the total outflow going out of the thermal demand:
    simulation.MVars[f"E_{component.key}_out"] = simulation.m.addMVar(
        simulation.T, vtype=GRB.CONTINUOUS, name=f"E_{component.key}_out"
    )
    simulation.m.addConstrs(
        (
            simulation.MVars[f"E_{component.key}_out"][t]
            == gp.quicksum(
                simulation.MVars[component.outputs[output_id].key][t]
                for output_id in range(len(component.outputs))
            )
        )
        for t in range(simulation.T)
    )
    logging.debug(
        f"        - Variable:     {component.name}_out                                  (timeseries of removed thermal energy at {component.name})"
    )

    # create a timeseries for the internal temperature:
    simulation.MVars[f"T_{component.key}"] = simulation.m.addMVar(
        simulation.T, vtype=GRB.CONTINUOUS, name=f"T_{component.key}"
    )
    logging.debug(
        f"        - Variable:     {component.key}                                  (Internal Temperature of {component.name})"
    )

    # set the starting temperature:
    simulation.m.addConstr(
        simulation.MVars[f"T_{component.key}"][0] == component.temperature_start
    )
    logging.debug(f"        - Constraint:   {component.name}[0] = Tstart")

    # add constraint for the thermal R-C-factory
    simulation.m.addConstrs(
        (
            simulation.MVars[f"T_{component.key}"][t]
            == simulation.MVars[f"T_{component.key}"][t - 1]
            + (  # t-1 temperature
                component.temperature_ambient[t - 1]
                - simulation.MVars[f"T_{component.key}"][t - 1]
            )
            * simulation.time_reference_factor
            / (component.R * component.C)
            + (  # thermal inertia
                simulation.MVars[f"E_{component.key}_in"][t - 1]
                - simulation.MVars[f"E_{component.key}_out"][t - 1]
            )
            * simulation.time_reference_factor
            / component.C
        )
        for t in range(1, simulation.T)
    )  # heating/cooling impact

    # keep the temperature within the allowed boundaries during Simulation interval:
    simulation.m.addConstrs(
        (simulation.MVars[f"T_{component.key}"][t] >= component.temperature_min[t])
        for t in range(simulation.T)
    )
    simulation.m.addConstrs(
        (simulation.MVars[f"T_{component.key}"][t] <= component.temperature_max[t])
        for t in range(simulation.T)
    )
    logging.debug(
        f"        - Constraint:   Tmin < T_{component.name} < Tmax for {component.name}"
    )

    # set the end temperature:
    if component.sustainable:
        simulation.m.addConstr(
            simulation.MVars[f"T_{component.key}"][simulation.T - 1]
            + (
                component.temperature_ambient[simulation.T - 1]
                - simulation.MVars[f"T_{component.key}"][simulation.T - 1]
            )
            * simulation.time_reference_factor
            / (component.R * component.C)
            + (
                simulation.MVars[f"E_{component.key}_in"][simulation.T - 1]
                - simulation.MVars[f"E_{component.key}_out"][simulation.T - 1]
            )
            * simulation.time_reference_factor
            / component.C
            == component.temperature_start
        )
        logging.debug(f"        - Constraint:   T_{component.name}[T] = Tstart")
    else:
        # keep the temperature within allowed boundaries at timestep T+1
        simulation.m.addConstr(
            simulation.MVars[f"T_{component.key}"][simulation.T - 1]
            + (
                component.temperature_ambient[simulation.T - 1]
                - simulation.MVars[f"T_{component.key}"][simulation.T - 1]
            )
            * simulation.time_reference_factor
            / (component.R * component.C)
            + (
                simulation.MVars[f"E_{component.key}_in"][simulation.T - 1]
                - simulation.MVars[f"E_{component.key}_out"][simulation.T - 1]
            )
            * simulation.time_reference_factor
            / component.C
            >= component.temperature_min[simulation.T - 1]
        )

        simulation.m.addConstr(
            simulation.MVars[f"T_{component.key}"][simulation.T - 1]
            + (
                component.temperature_ambient[simulation.T - 1]
                - simulation.MVars[f"T_{component.key}"][simulation.T - 1]
            )
            * simulation.time_reference_factor
            / (component.R * component.C)
            + (
                simulation.MVars[f"E_{component.key}_in"][simulation.T - 1]
                - simulation.MVars[f"E_{component.key}_out"][simulation.T - 1]
            )
            * simulation.time_reference_factor
            / component.C
            <= component.temperature_max[simulation.T - 1]
        )

    # calculate the losses:
    simulation.m.addConstrs(
        simulation.MVars[component.to_losses.key][t]
        - simulation.MVars[component.from_gains.key][t]
        == (
            simulation.MVars[f"T_{component.key}"][t] - component.temperature_ambient[t]
        )
        * simulation.time_reference_factor
        / component.R
        for t in range(simulation.T)
    )

    logging.debug(
        f"        - Constraint:     calculation of thermal losses for {component.name}"
    )
