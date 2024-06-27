# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: Factory_Flexibility_Model
# File Name: create_cost_overview.py
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

# This script is called on the following paths:
# -> fm.dash.create_dash() -> update_plots_overview()


def create_cost_overview(simulation):
    """
    This function takes a simulation object and creates a simple string that contains a formatted list of all the costs factors that determine the target function value of the solved simulation.

    :param simulation: [fm.simulation-object]
    :return: [str]
    """

    # get cost results from simulation
    costs = simulation.result["costs"]

    # get currency from factory
    currency = simulation.factory.currency

    # define cost_types and their display names
    cost_types = {
        "inputs": "Cost and revenue of inputs",
        "outputs": "Cost and revenue of outputs",
        "converter_ramping": "Converter operation cost",
        "capacity_provision": "Costs for capacity provision",
        "emission_allowances": "Emission cost",
        "slacks": "Slack cost",
    }

    # initialize string
    detailed_costs = ""

    # iterate over all cost types
    for cost_type, cost_items in costs.items():

        #  Skip iteration if no cost items of current type exist
        if cost_items == {}:
            continue

        # write headline for current cost type
        detailed_costs = detailed_costs + f"\n **{cost_types[cost_type]}:** \n"

        # iterate over all cost items
        for item, value in cost_items.items():

            # write line with bulletpoint for current cost item
            if value > 0:
                detailed_costs = (
                    detailed_costs
                    + f"\n * **Cost of {simulation.factory.get_name(item)}:** {round(value,2)}{currency}\n"
                )
            elif value < 0:
                detailed_costs = (
                    detailed_costs
                    + f"\n * **Revenue from {simulation.factory.get_name(item)}:** {round(value,2)}{currency}\n"
                )

    return detailed_costs
