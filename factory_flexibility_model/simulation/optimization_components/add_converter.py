#  CALLING PATH:
#  -> Simulation.simulate() -> Simulation.create_optimization_problem()

# IMPORTS
import logging

import gurobipy as gp
from gurobipy import GRB


# CODE START
def add_converter(simulation, component):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the converter handed over as 'Component'

    :param component: components.converter-object
    :return: simulation.m is being extended
    """
    # create a timeseries of decision variables to represent the utilization U(t)
    simulation.MVars[f"P_{component.key}"] = simulation.m.addMVar(
        simulation.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}"
    )
    logging.debug(
        f"        - Variable:     P_{component.name} timeseries of the nominal power of {component.name}"
    )

    # add variables to express the positive and negative deviations from the nominal operating point
    simulation.MVars[f"P_{component.key}_devpos"] = simulation.m.addMVar(
        simulation.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}_devpos"
    )
    simulation.MVars[f"P_{component.key}_devneg"] = simulation.m.addMVar(
        simulation.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}_devneg"
    )

    # is the operating power of the converter limited? If yes: add power_max and power_min constraints
    if component.power_max_limited:
        simulation.m.addConstr(
            simulation.MVars[f"P_{component.key}"]
            <= component.power_max * component.availability
        )
        logging.debug(
            f"        - Constraint:   P_{component.key} <= P_{component.name}_max"
        )

    if component.power_min_limited:
        simulation.m.addConstr(
            simulation.MVars[f"P_{component.key}"]
            >= component.power_min * component.availability
        )
        logging.debug(
            f"        - Constraint:   P_{component.key} >= P_{component.key}_min"
        )

    # Calculate the efficiency of operation for each timestep based on the deviations
    simulation.MVars[f"Eta_{component.key}"] = simulation.m.addMVar(
        simulation.T, vtype=GRB.CONTINUOUS, name=f"Eta_{component.name}"
    )
    logging.debug(
        f"        - Variable:     Eta_{component.name}                              "
        f"(Operating efficiency of {component.name}"
    )

    if component.eta_variable:
        if simulation.problem_class["grade"] < 2:
            simulation.problem_class["grade"] = 2
        simulation.m.addConstrs(
            simulation.MVars[f"Eta_{component.key}"][t]
            == component.eta_max
            - simulation.MVars[f"P_{component.key}_devpos"][t]
            * component.delta_eta_high
            - simulation.MVars[f"P_{component.key}_devneg"][t] * component.delta_eta_low
            for t in range(simulation.T)
        )
        logging.debug(f"        - Constraint:   Calculate Eta(t) for {component.name}")
    else:
        simulation.m.addConstrs(
            simulation.MVars[f"Eta_{component.key}"][t] == 1
            for t in range(simulation.T)
        )
        logging.debug(
            f"        - Constraint:   Eta(t) for {component.name} fixed to 100%"
        )

    # calculate the absolute operating point out of the nominal operating point, the deviations and the switching state
    # Can the Converter be turned on/off regardless of the power constraints?
    if component.switchable:
        simulation.problem_class["type"] = "mixed integer"
        # introduce a variable representing the switching state of the converter
        simulation.MVars[f"Bool_{component.key}_state"] = simulation.m.addMVar(
            simulation.T, vtype=GRB.BINARY, name=f"{component.name}_state"
        )

        # calculate the operating point concerning the switching state
        simulation.m.addConstrs(
            simulation.MVars[f"P_{component.key}"][t]
            == (
                component.power_nominal
                - simulation.MVars[f"P_{component.key}_devneg"][t]
                + simulation.MVars[f"P_{component.key}_devpos"][t]
            )
            * simulation.MVars[f"Bool_{component.key}_state"][t]
            for t in range(simulation.T)
        )
    else:
        # calculate the operating point without a switching state
        simulation.m.addConstr(
            simulation.MVars[f"P_{component.key}"]
            == component.power_nominal
            - simulation.MVars[f"P_{component.key}_devneg"]
            + simulation.MVars[f"P_{component.key}_devpos"]
        )

    # set ramping constraints if needed:
    if component.ramp_power_limited:
        simulation.m.addConstr(
            simulation.MVars[f"P_{component.key}"][1 : simulation.T]
            <= simulation.MVars[f"P_{component.key}"][0 : simulation.T - 1]
            + component.power_ramp_max_pos
        )  # restrict ramping up
        simulation.m.addConstr(
            simulation.MVars[f"P_{component.key}"][1 : simulation.T]
            >= simulation.MVars[f"P_{component.key}"][0 : simulation.T - 1]
            - component.power_ramp_max_neg
        )  # restrict ramping down
        logging.debug(
            f"        - Constraint:   Ramping constraints for {component.name}"
        )

    # set the flows of incoming connections
    for connection in component.inputs:
        simulation.m.addConstr(
            simulation.MVars[connection.key]
            == simulation.MVars[f"P_{component.key}"]
            * connection.weight_destination
            * simulation.interval_length
        )

    # set the flows of outgoing connections
    for connection in component.outputs:
        if connection.flowtype.is_energy():
            simulation.m.addConstr(
                simulation.MVars[connection.key]
                == simulation.MVars[f"P_{component.key}"]
                * connection.weight_origin
                * simulation.interval_length
                * simulation.MVars[f"Eta_{component.key}"]
            )
            logging.debug(
                f"        - added energy output calculation with losses for {connection.name}"
            )
        else:
            simulation.m.addConstr(
                simulation.MVars[connection.key]
                == simulation.MVars[f"P_{component.key}"]
                * connection.weight_origin
                * simulation.interval_length
            )
            logging.debug(
                f"        - added material output calculation for {connection.name}"
            )

    # calculate the resulting energy losses: losses(t) = sum(inputs(t)) - sum(outputs(t))
    simulation.m.addConstr(
        simulation.MVars[component.to_Elosses.key]
        == sum(simulation.MVars[input_i.key] for input_i in component.inputs_energy)
        - sum(simulation.MVars[output_i.key] for output_i in component.outputs_energy)
    )

    # calculate the resulting material losses: losses(t) = sum(inputs(t)) - sum(outputs(t))
    if not component.to_Mlosses == []:
        simulation.m.addConstr(
            simulation.MVars[component.to_Mlosses.key]
            == sum(
                simulation.MVars[input_i.key] for input_i in component.inputs_material
            )
            - sum(
                simulation.MVars[output_i.key]
                for output_i in component.outputs_material
            )
        )

    # is the converter afflicted with a ramping charge?
    if component.rampup_cost > 0:
        # If yes: Add an MVar for calculating the occuring rampups
        # create single float Mvar
        simulation.MVars[f"P_rampup_{component.key}"] = simulation.m.addMVar(
            simulation.T - 1,
            vtype=GRB.CONTINUOUS,
            lb=0,
            name=f"P_rampup_{component.key}",
        )

        # define the Mvar as the realized rampup
        simulation.m.addConstrs(
            simulation.MVars[f"P_rampup_{component.key}"]
            >= simulation.MVars[f"P_{component.key}"][t + 1]
            - simulation.MVars[f"P_{component.key}"][t]
            for t in range(simulation.T - 1)
        )

        # create new cost term
        simulation.C_objective.append(
            simulation.m.addMVar(
                1, vtype=GRB.CONTINUOUS, name=f"C_rampup_{component.key}"
            )
        )

        # define the cost term
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == gp.quicksum(simulation.MVars[f"P_rampup_{component.key}"])
            * component.rampup_cost
        )

        logging.debug(f"        - CostFactor:   Cost for ramping of {component.name}")

    # is the converter afflicted with a capacity charge?
    if component.capacity_charge > 0:
        # If yes: Add an MVar for the maximum used Power and add cost factor
        # create single float Mvar
        simulation.MVars[f"P_max_{component.key}"] = simulation.m.addMVar(
            1, vtype=GRB.CONTINUOUS, name=f"P_max_{component.key}"
        )

        # define the Mvar as the maximum used utilization
        simulation.m.addConstr(
            simulation.MVars[f"P_max_{component.key}"][0]
            == gp.max_(
                (
                    simulation.MVars[f"P_{component.key}"][t]
                    for t in range(simulation.T)
                ),
                constant=0,
            )
        )

        # create new cost term
        simulation.C_objective.append(
            simulation.m.addMVar(
                1, vtype=GRB.CONTINUOUS, name=f"C_Capacity_{component.key}"
            )
        )

        # define the costs -> capacity_charge is specified on yearly basis and has to be broken down to simulation timeframe
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == simulation.interval_length
            * simulation.T
            / 8760
            * component.capacity_charge
            * simulation.MVars[f"P_max_{component.key}"]
        )

        logging.debug(
            f"        - CostFactor:   Cost for capital costs of {component.name}"
        )
