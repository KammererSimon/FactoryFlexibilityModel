# -----------------------------------------------------------------------------
# Project Name: Factory_Flexibility_Model
# File Name: add_flows.py
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
