#  CALLING PATH:
#  -> Simulation.simulate() -> Simulation.create_optimization_problem()

# IMPORTS
import logging

import numpy as np
from gurobipy import GRB


# CODE START
def add_storage(simulation, component):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the slack handed over as 'Component'
    :param component: components.slack-object
    :return: simulation.m is being extended
    """
    # create  variable for initial SOC
    simulation.MVars[f"SOC_{component.key}_start"] = simulation.m.addMVar(
        1, vtype=GRB.CONTINUOUS, name=f"SOC_{component.key}_start"
    )
    if component.soc_start_determined:
        simulation.m.addConstr(
            simulation.MVars[f"SOC_{component.key}_start"] == component.soc_start
        )
        logging.debug(
            f"        - Constraint:   SOC_start == {component.soc_start} for storage {component.name}"
        )
    else:
        simulation.m.addConstr(simulation.MVars[f"SOC_{component.key}_start"] <= 1)
        logging.debug(f"        - Variable:     SOC_start for storage {component.name}")

    # create variable for SOC
    simulation.MVars[f"SOC_{component.key}"] = simulation.m.addMVar(
        simulation.T, vtype=GRB.CONTINUOUS, name=f"SOC_{component.key}"
    )
    logging.debug(f"        - Variable:     SOC for storage {component.name} ")

    # calculate SOC for every timestep using cumsum + SOC_start
    cumsum_matrix = np.tril(
        np.ones(simulation.T)
    )  # create a matrix with ones on- and under the main diagonal to quickly perform cumsum-calculations in matrix form
    simulation.m.addConstr(
        simulation.MVars[f"SOC_{component.key}"]
        == cumsum_matrix
        @ (
            simulation.MVars[component.inputs[0].key]
            - simulation.MVars[component.outputs[0].key]
            - simulation.MVars[component.to_losses.key]
        )
        + component.capacity * simulation.MVars[f"SOC_{component.key}_start"][0]
    )

    logging.debug(
        f"        - Constraint:   Calculate SOC_end(t) for storage {component.name} "
    )

    # set SOC_end = SOC_start
    simulation.m.addConstr(
        simulation.MVars[f"SOC_{component.key}"][simulation.T - 1]
        == simulation.MVars[f"SOC_{component.key}_start"][0] * component.capacity
    )
    logging.debug(
        f"        - Constraint:   SOC_end == SOC_start for storage {component.name}"
    )

    # don't violate the capacity boundary: cumsum of all inputs and outputs plus initial soc must not be more than the capacity in any timestep
    simulation.m.addConstr(
        simulation.MVars[f"SOC_{component.key}"] <= component.capacity
    )
    logging.debug(
        f"        - Constraint:   Cumsum(E) <= Capacity for {component.name} "
    )

    # don't take out more than stored: cumsum of all inputs and outputs plus initial soc must be more than zero in any timestep
    simulation.m.addConstr(simulation.MVars[f"SOC_{component.key}"] >= 0)
    logging.debug(f"        - Constraint:   Cumsum(E) >= 0 for {component.name} ")

    # create Pcharge_max-constraint
    if component.power_max_charge > 0:
        simulation.m.addConstr(
            simulation.MVars[component.inputs[0].key]
            <= component.power_max_charge * simulation.interval_length
        )
        logging.debug(
            f"        - Constraint:   power_charge <= power_charge_max for {component.name}"
        )

    # create Pdischarge_max-constraint
    if component.power_max_discharge > 0:
        simulation.m.addConstr(
            simulation.MVars[component.outputs[0].key]
            <= component.power_max_discharge * simulation.interval_length
        )
        logging.debug(
            f"        - Constraint:   power_discharge <= power_discharge_max for {component.name}"
        )

    # create constraint to calculate the occuring losses if necessary
    if (
        component.leakage_SOC > 0
        or component.leakage_time > 0
        or component.efficiency < 1
    ):
        soc_leakage = component.leakage_SOC**simulation.time_reference_factor
        lin_leakage = (
            component.leakage_time
            * component.capacity
            * simulation.time_reference_factor
        )
        simulation.m.addConstrs(
            (
                simulation.MVars[component.to_losses.key][t]
                == simulation.MVars[f"SOC_{component.key}"][t] * soc_leakage
                + lin_leakage
                + simulation.MVars[component.outputs[0].key][t]
                * (1 / component.efficiency - 1)
            )
            for t in range(simulation.T)
        )
        logging.debug(
            f"        - Constraint:   E_losses = E_discharge * (1-efficiency) for {component.name}"
        )
    else:
        # make sure that there is no energy-disposal loophole using illegal losses
        simulation.m.addConstr(simulation.MVars[component.to_losses.key] == 0)

    # in case direct throughput is forbidden or the storage is directly connected to a pool on both sides and the efficiency is 100%: prohibit charging and discharging at the same timestep
    if (
        component.inputs[0].origin == component.outputs[0].destination
        and component.efficiency == 1
    ) or component.direct_throughput == False:
        # add helper variable to track if the storage is charging or discharging
        simulation.MVars[f"{component.key}_charging"] = simulation.m.addMVar(
            simulation.T, vtype=GRB.BINARY, name=f"{component.key}_charging"
        )
        # use big M method to force either input or output to be zero
        simulation.m.addConstrs(
            simulation.MVars[component.inputs[0].key][t]
            <= simulation.big_m * simulation.MVars[f"{component.key}_charging"][t]
            for t in range(simulation.T)
        )
        simulation.m.addConstrs(
            simulation.MVars[component.outputs[0].key][t]
            <= simulation.big_m * (1 - simulation.MVars[f"{component.key}_charging"][t])
            for t in range(simulation.T)
        )

        logging.debug(
            f"        - Constraint:   Preventing direct throughput on {component.name}"
        )

    # is the storage afflicted with a capital cost per used capacity?
    if component.capacity_charge > 0:
        # If yes: Add an MVar for the maximum used storage capacity and add cost factor
        # create single float Mvar
        simulation.MVars[f"SOC_max_{component.key}"] = simulation.m.addMVar(
            1, vtype=GRB.CONTINUOUS, name=f"SOC_max_{component.key}"
        )

        # define the Mvar as the maximum used utilization
        simulation.m.addConstrs(
            simulation.MVars[f"SOC_max_{component.key}"][0]
            >= simulation.MVars[f"SOC_{component.key}"][t]
            for t in range(simulation.T)
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
            * simulation.MVars[f"SOC_max_{component.key}"]
        )

        logging.debug(f"        - CostFactor:   capital costs of {component.name}")
