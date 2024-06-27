# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_triggerdemand.py
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
def add_triggerdemand(simulation, component, interval_length):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the triggerdemand handed over as 'Component'
    :param component: components.triggerdemand-object
    :return: simulation.m is beeing extended
    """

    # create Matrix with all executable load-profiles
    possibilities = component.Tend - component.Tstart - component.profile_length + 2
    if component.input_energy:
        profiles_energy = np.zeros(
            [possibilities, component.Tend - component.Tstart + 1]
        )
    if component.input_material:
        profiles_material = np.zeros(
            [possibilities, component.Tend - component.Tstart + 1]
        )
    parallelcheck = np.zeros([possibilities, component.Tend - component.Tstart + 1])

    for i in range(possibilities):
        if component.input_energy:
            profiles_energy[
                i, i : i + component.profile_length
            ] = component.load_profile_energy
        if component.input_material:
            profiles_material[
                i, i : i + component.profile_length
            ] = component.load_profile_material
        parallelcheck[i, i : i + component.profile_length] = np.ones(
            component.profile_length
        )

    # create decision variable vector
    simulation.MVars[f"{component.key}_executions"] = simulation.m.addMVar(
        possibilities, vtype=GRB.INTEGER, name=f"{component.key}_executions"
    )
    logging.debug(
        f"        - Variable:     {component.name}_executions                                 (List of triggered events at triggerdemand {component.name})"
    )

    # guarantee the required amount of executions
    if component.executions > 0:
        simulation.m.addConstr(
            sum(simulation.MVars[f"{component.key}_executions"]) == component.executions
        )
        logging.debug(
            f"        - Constraint:     Guarantee the required amount of process executions at {component.name}"
        )

    # limit the number of parallel executions
    if component.max_parallel > 0:
        simulation.m.addConstr(
            parallelcheck.transpose() @ simulation.MVars[f"{component.key}_executions"]
            <= np.ones(component.Tend - component.Tstart + 1) * component.max_parallel
        )
        logging.debug(
            f"        - Constraint:   Limit the maximum parallel executions at {component.name}"
        )

    # calculate resulting load profile
    if component.input_energy:
        simulation.MVars[f"{component.key}_loadprofile_energy"] = simulation.m.addMVar(
            interval_length,
            vtype=GRB.CONTINUOUS,
            name=f"{component.key}_loadprofile_energy",
        )
    if component.input_material:
        simulation.MVars[
            f"{component.key}_loadprofile_material"
        ] = simulation.m.addMVar(
            interval_length,
            vtype=GRB.CONTINUOUS,
            name=f"{component.key}_loadprofile_material",
        )
    logging.debug(
        f"        - Variable:     {component.name}_loadprofile                                 (resulting load profile of triggerdemand {component.name})"
    )

    if component.Tstart > 1:
        if component.input_energy:
            simulation.m.addConstr(
                simulation.MVars[f"{component.key}_loadprofile_energy"][
                    : component.Tstart - 1
                ]
                == 0
            )
        if component.input_material:
            simulation.m.addConstr(
                simulation.MVars[f"{component.key}_loadprofile_material"][
                    : component.Tstart - 1
                ]
                == 0
            )

    if component.input_energy:
        simulation.m.addConstr(
            simulation.MVars[f"{component.key}_loadprofile_energy"][
                component.Tstart - 1 : component.Tend
            ]
            == profiles_energy.transpose()
            @ simulation.MVars[f"{component.key}_executions"]
        )
    if component.input_material:
        simulation.m.addConstr(
            simulation.MVars[f"{component.key}_loadprofile_material"][
                component.Tstart - 1 : component.Tend
            ]
            == profiles_material.transpose()
            @ simulation.MVars[f"{component.key}_executions"]
        )

    if component.Tend < interval_length:
        if component.input_energy:
            simulation.m.addConstr(
                simulation.MVars[f"{component.key}_loadprofile_energy"][
                    component.Tend + 1 :
                ]
                == 0
            )
        if component.input_material:
            simulation.m.addConstr(
                simulation.MVars[f"{component.key}_loadprofile_material"][
                    component.Tend + 1 :
                ]
                == 0
            )
    logging.debug(f"        - Constraint:   Calculate load profile at {component.name}")

    # set validate and output connection to match the load profile
    if component.input_energy:
        simulation.m.addConstr(
            simulation.MVars[component.input_energy.key]
            == simulation.MVars[f"{component.key}_loadprofile_energy"]
            * simulation.interval_length
        )
        simulation.m.addConstr(
            simulation.MVars[component.output_energy.key]
            == simulation.MVars[f"{component.key}_loadprofile_energy"]
            * simulation.interval_length
        )
    if component.input_material:
        simulation.m.addConstr(
            simulation.MVars[component.input_material.key]
            == simulation.MVars[f"{component.key}_loadprofile_material"]
        )
        simulation.m.addConstr(
            simulation.MVars[component.output_material.key]
            == simulation.MVars[f"{component.key}_loadprofile_material"]
        )
