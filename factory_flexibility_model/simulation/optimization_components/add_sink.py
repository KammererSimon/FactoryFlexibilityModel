# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_sink.py
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
def add_sink(simulation, component, t_start, t_end):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to simulate the destination handed over as 'Component'
    :param component: components.destination-object
    :return: simulation.m is beeing extended
    """
    # Sinks may be determined in their power intake or the power consumption may be calculated during the optimization.
    # In the first case a constraint is created, that forces all connected inputs to meet the desired power in total
    # In the second case a MVar reflecting the resulting inflow is created, together with a constraint to calculate it

    interval_length = t_end - t_start + 1

    # create a timeseries of decision variables to represent the total inflow (energy/material) going into the sink
    simulation.MVars[f"E_{component.key}"] = simulation.m.addMVar(
        interval_length, vtype=GRB.CONTINUOUS, name=f"E_{component.name}"
    )
    logging.debug(
        f"        - Variable:     {component.name}                                  (timeseries of global outflows to {component.name})"
    )

    if component.determined:
        # set the incoming flow to meet the power demand
        simulation.m.addConstr(
            simulation.MVars[component.inputs[0].key]
            == component.demand[t_start : t_end + 1]
        )
        logging.debug(
            f"        - Constraint:   Sum of incoming flows == determined total demand              ({component.name} determined by timeseries)"
        )

    # set the inflow of the component to match the input flow
    simulation.m.addConstr(
        simulation.MVars[component.inputs[0].key]
        == simulation.MVars[f"E_{component.key}"]
    )
    logging.debug(f"        - Constraint:   {component.name} == sum of incoming flows")

    # is the total cumulative input of the sink limited? If yes: add sum constraint
    if component.max_total_input_limited:
        simulation.m.addConstr(
            gp.quicksum(simulation.MVars[f"E_{component.key}"])
            <= component.max_total_input
        )
        logging.debug(
            f"        - Constraint:   sum({component.name}(t)) <= {component.name}_max_total"
        )

    # is the maximum output power of the destination limited? If yes: Add power_max constraint
    if component.power_max_limited:
        simulation.m.addConstr(
            simulation.MVars[f"E_{component.key}"]
            <= component.power_max[t_start : t_end + 1]
            * component.availability[t_start : t_end + 1]
        )
        logging.debug(
            f"        - Constraint:   {component.key} <= {component.name}_max"
        )

    # is the minimum output power of the source limited? If yes: Add power_min constraint
    if component.power_min_limited:
        simulation.m.addConstrs(
            simulation.MVars[f"E_{component.key}"] / interval_length
            >= component.power_min[t]
            for t in range(interval_length)
        )
        logging.debug(
            f"        - Constraint:   {component.name} >= {component.name}_min"
        )

    # does the utilization of the destination cost something? If yes: Add the corresponding cost factors
    if component.chargeable:
        simulation.C_objective.append(
            simulation.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}")
        )
        simulation.m.addConstr(
            simulation.C_objective[-1]
            == component.cost[t_start : t_end + 1]
            @ simulation.MVars[f"E_{component.key}"]
        )
        logging.debug(f"        - CostFactor:   Cost for dumping into {component.name}")

    # does the utilization of the destination create revenue? If yes: Add the corresponding negative cost factors
    if component.refundable:
        simulation.R_objective.append(
            simulation.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"R_{component.key}")
        )
        simulation.m.addConstr(
            simulation.R_objective[-1]
            == component.revenue[t_start : t_end + 1]
            @ simulation.MVars[f"E_{component.key}"]
        )
        logging.debug(
            f"        - CostFactor:   Revenue for sales generated by {component.name}"
        )

    if component.causes_emissions:
        # additional emissions
        simulation.emission_sources.append(
            simulation.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"CO2_{component.key}")
        )
        simulation.m.addConstr(
            simulation.emission_sources[-1]
            == component.co2_emissions_per_unit[t_start : t_end + 1]
            @ simulation.MVars[f"E_{component.key}"]
        )
        logging.debug(
            f"        - EmissionFactor:   Emissions caused by usage of {component.name}"
        )
