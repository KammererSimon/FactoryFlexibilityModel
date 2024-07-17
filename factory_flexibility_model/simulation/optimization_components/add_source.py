# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_source.py
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
import gurobipy as gp
from gurobipy import GRB


# CODE START
def add_source(simulation, component, t_start, t_end):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the source handed over as 'Component'
    :param component: components.source-object
    :return: simulation.m is being extended
    """

    interval_length = t_end-t_start+1

    # create a timeseries of decision variables to represent the total inflow coming from the source
    simulation.MVars[f"E_{component.key}"] = simulation.m.addMVar(
        interval_length, vtype=GRB.CONTINUOUS, name=f"P_{component.key}"
    )

    logging.debug(
        f"        - Variable:     {component.name}                              (timeseries of global inputs from E_{component.name})"
    )

    # set the sum of outgoing flows to meet the fixed supply
    if component.determined:
        simulation.m.addConstr(
            gp.quicksum(
                simulation.MVars[component.outputs[o].key]
                for o in range(len(component.outputs))
            )
            == component.determined_power[t_start:t_end+1]
        )

    # add constraints to calculate the total inflow to the system as the sum of all flows of outgoing connections
    simulation.m.addConstr(
        gp.quicksum(
            simulation.MVars[component.outputs[o].key]
            for o in range(len(component.outputs))
        )
        == simulation.MVars[f"E_{component.key}"]
    )

    logging.debug(f"        - Constraint:   {component.name} == sum of outgoing flows")

    # is the maximum output power of the source limited? If yes: Add power_max constraint
    if component.power_max_limited:
        simulation.m.addConstr(
            gp.quicksum(
                simulation.MVars[component.outputs[o].key]
                for o in range(len(component.outputs))
            )
            / simulation.interval_length
            <= component.power_max[t_start:t_end+1] * component.availability[t_start:t_end+1]
        )
        logging.debug(
            f"        - Constraint:   {component.name} <= P_{component.name}_max"
        )
    elif simulation.factory.enable_slacks:
        simulation.m.addConstr(
            gp.quicksum(
                simulation.MVars[component.outputs[o].key]
                for o in range(len(component.outputs))
            )
            <= simulation.big_m
        )
        logging.debug(
            f"        - Constraint:   {component.name} <= SECURITY                            -> Prevent Model from being unbounded"
        )

    # is the minimum output power of the source limited? If yes: Add power_min constraint
    if component.power_min_limited:
        simulation.m.addConstr(
            gp.quicksum(
                simulation.MVars[component.outputs[o].key]
                for o in range(len(component.outputs))
            )
            / simulation.interval_length
            >= component.power_min[t_start:t_end+1]
        )

        logging.debug(
            f"        - Constraint:   {component.name} >= {component.name}_min"
        )

    # does the utilization of the source cost something? If yes: Add the corresponding cost factors
    if component.chargeable:
        if min(component.cost[t_start:t_end+1]) < 0:
            # if negative prices are possible the lower bound of the decision variable has to allow negative values
            simulation.C_objective.append(
                simulation.m.addMVar(
                    1,
                    vtype=GRB.CONTINUOUS,
                    lb=-GRB.INFINITY,
                    name=f"C_{component.key}",
                )
            )
        else:
            # otherwise the lower bound is kept at 0 for better solver performance
            simulation.C_objective.append(
                simulation.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}")
            )
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == component.cost[t_start:t_end+1] @ simulation.MVars[f"E_{component.key}"]
        )
        logging.debug(f"        - CostFactor:   Cost for usage of {component.name}")

    # is the source afflicted with a capacity charge?
    if component.capacity_charge > 0:
        # If yes: Add an MVar for the maximum used Power and add cost factor
        # create single float Mvar
        simulation.MVars[f"P_max_{component.key}"] = simulation.m.addMVar(
            1, vtype=GRB.CONTINUOUS, name=f"P_max_{component.key}"
        )

        # define the Mvar as the maximum used output power
        simulation.m.addConstr(
            simulation.MVars[f"P_max_{component.key}"][0]
            == gp.max_(
                (
                    simulation.MVars[f"E_{component.key}"][t]
                    for t in range(t_end-t_start+1)
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

        # define the costs -> capacity_charge is specified on yearly basis
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == simulation.interval_length
            * (t_end-t_start+1)
            / 8760
            * component.capacity_charge
            * simulation.MVars[f"P_max_{component.key}"]
        )

        logging.debug(
            f"        - CostFactor:   Cost for capacity charge of {component.name}"
        )

    # does the source cause direct or indirect emissions when used?
    if component.causes_emissions:
        # calculate total emissions
        simulation.emission_sources.append(
            simulation.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"CO2_{component.key}")
        )
        simulation.m.addConstr(
            simulation.emission_sources[-1]
            == component.co2_emissions_per_unit[t_start:t_end+1]
            @ simulation.MVars[f"E_{component.key}"]
        )
        logging.debug(
            f"        - EmissionFactor:   Emissions caused by usage of {component.name}"
        )
