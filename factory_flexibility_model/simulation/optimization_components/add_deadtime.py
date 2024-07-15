# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_deadtime.py
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


# CODE START
def add_deadtime(simulation, component, t_start, t_end):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the deadtime handed over as 'Component'

    :param component: components.deadtime-object
    :return: simulation.m is beeing extended
    """
    interval_length = t_end - t_start + 1

    # calculate the number of timesteps required to match the scenario - timescale:
    delay = component.delay / simulation.time_reference_factor
    if not delay % 1 == 0:
        logging.warning(
            f"Warning: The delay of {component.name} has been rounded to {delay}, since to clean conversion to the scenario timestep length is possible"
        )
    delay = int(delay)

    # check, if the deadtime is slacked:
    if len(component.outputs) == 1:
        # no slacks...
        # set output_flow = slack for start interval
        simulation.m.addConstr(simulation.MVars[component.outputs[0].key][0:delay] == 0)

        # set output(t) = input(t-delay) for middle interval
        simulation.m.addConstr(
            simulation.MVars[component.outputs[0].key][delay : interval_length]
            == simulation.MVars[component.inputs[0].key][0 : interval_length - delay]
        )

        # set input(t) = slack for end interval
        simulation.m.addConstr(
            simulation.MVars[component.inputs[0].key][
                interval_length - delay : interval_length - 1
            ]
            == 0
        )

    else:
        # set output_flow = slack for start interval
        simulation.m.addConstrs(
            simulation.MVars[component.outputs[1].key][t]
            == simulation.MVars[component.inputs[0].key][t]
            for t in range(delay)
        )

        # set output(t) = input(t-delay) for middle interval
        simulation.m.addConstrs(
            simulation.MVars[component.outputs[1].key][t + delay]
            == simulation.MVars[component.inputs[1].key][t]
            for t in range(interval_length - delay)
        )

        # set input(t) = slack for end interval
        simulation.m.addConstrs(
            simulation.MVars[component.inputs[1].key][interval_length - t - 1]
            == simulation.MVars[component.outputs[0].key][t]
            for t in range(delay)
        )
