# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: Factory_Flexibility_Model
# File Name: create_emission_overview.py
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


def create_emission_overview(simulation):
    """
    This function takes a simulation object and creates a simple string that contains a formatted list of all the costs factors that determine the target function value of the solved simulation.

    :param simulation: [fm.simulation-object]
    :return: [str]
    """

    # get emission results from simulation
    emissions = simulation.result["total_emissions"]

    # initialize string
    detailed_emissions = "**Emission Sources:**"


    # iterate oer all components
    for component in simulation.factory.components.values():
        # only continue for sources and sinks
        if component.type in ["source", "sink"]:
            #calculate total emissions
            component_emissions = simulation.result[component.key]["emissions"]
            if sum(component_emissions) > 0:
                # add line with component emissions to the string if the source or sink caused emissions
                detailed_emissions = detailed_emissions + f"\n * **{simulation.factory.get_name(component.key)}:** {round(sum(component_emissions)/1000,2)} tCO2\n"

    detailed_emissions = detailed_emissions + f"\n * **Total Emissions:** {round(sum(simulation.result['total_emissions'])/1000, 2)} tCO2\n"

    # return created string
    return detailed_emissions
