# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_storage.py
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

import numpy as np
from gurobipy import GRB


# CODE START
def add_storage(simulation, component, t_start, t_end):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the slack handed over as 'Component'
    :param component: components.slack-object
    :return: simulation.m is being extended
    """

    interval_length = t_end-t_start+1

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
        interval_length, vtype=GRB.CONTINUOUS, name=f"SOC_{component.key}"
    )
    logging.debug(f"        - Variable:     SOC for storage {component.name} ")

    # calculate SOC for every timestep using cumsum + SOC_start
    cumsum_matrix = np.tril(
        np.ones(interval_length)
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
        simulation.MVars[f"SOC_{component.key}"][interval_length - 1]
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
    if component.power_max_charge is not None:
        simulation.m.addConstr(
            simulation.MVars[component.inputs[0].key]
            <= component.power_max_charge * simulation.interval_length
        )
        logging.debug(
            f"        - Constraint:   power_charge <= power_charge_max for {component.name}"
        )

    # create Pdischarge_max-constraint
    if component.power_max_discharge is not None:
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
            for t in range(interval_length)
        )
        logging.debug(
            f"        - Constraint:   Energy_losses = Energy_discharge * (1-efficiency) for {component.name}"
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
            interval_length, vtype=GRB.BINARY, name=f"{component.key}_charging"
        )
        # use big M method to force either input or output to be zero
        simulation.m.addConstrs(
            simulation.MVars[component.inputs[0].key][t]
            <= simulation.big_m * simulation.MVars[f"{component.key}_charging"][t]
            for t in range(interval_length)
        )
        simulation.m.addConstrs(
            simulation.MVars[component.outputs[0].key][t]
            <= simulation.big_m * (1 - simulation.MVars[f"{component.key}_charging"][t])
            for t in range(interval_length)
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
            for t in range(interval_length)
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
            * interval_length
            / 8760
            * component.capacity_charge
            * simulation.MVars[f"SOC_max_{component.key}"]
        )

        logging.debug(f"        - CostFactor:   capital costs of {component.name}")
