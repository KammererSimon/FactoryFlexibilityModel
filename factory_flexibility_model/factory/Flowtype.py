# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: Factory_Flexibility_Model
# File Name: Flowtype.py
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
import factory_flexibility_model.factory.Unit as Unit
import factory_flexibility_model.ui.utility.color as c


class Flowtype:
    def __init__(
        self,
        key,
        *,
        unit: Unit.Unit,
        description: str = "",
        color: str | list[float] = None,
        represents_losses: bool = False,
        name: str = None,
    ):
        """
        This function creates a new flowtype-object and adds it to the factory
        :param name: [String] name identifier for the new flowtype
        :param unit: [factory_flexibility_model.factory.Unit] Unit description given as a Unit-object
        :param description: [String] Description of the flow, just for GUI and labeling purposes
        :param color: [factory_flexibility_model.ui.utility.color] Object containing color code for displaying the flow in GUI and Figures
        """

        # set the key and name (validate validation happens during factory.add_flow)
        self.key = key
        if name is None:
            self.name = key
        else:
            self.name = name

        self.represents_losses = represents_losses

        # define a color that components with flows of this kind will be displayed
        if color is not None:
            # If color is specified use the value that has been handed over
            self.color = c.color(color)
        else:
            # otherwise use grey
            self.color = c.color("#777777")

        # set the unit of the flow type as a new unit or a given unit object
        self.unit = unit

        # specify a description for the flowtype to appear in evaluation diagrams
        if description == "":
            self.description = f"Flowtype of {name}"
        else:
            self.description = description

    def get_value_expression(
        self, value: float, quantity_type: str, *, digits: int = 2
    ) -> str:
        """
        This function takes a numeric value, the information wether it describes a flow or a flowrate and optionally a number of rounding digits.
        It returns a string describing the data in the correct unit and magnitude.
        F.e: 15000000 + "flow" -> "1.5GW"
        :param value: [float] a numeric value in the base unit (kW/kg)
        :param type: [string] "Flow" or "Flowrate"
        :param digits: [int] Requested number of digits behind the decimal point; Standard: 2
        :return: [string] Description of the value with correct magnitude and unit
        """

        return f"{self.unit.get_value_expression(value=value, quantity_type=quantity_type, digits=digits)}"

    def is_unknown(self) -> bool:
        """
        Returns the information whether the flowtype is still considered as unknown
        :return: True/False
        """

        return self.key == "unknown"

    def is_energy(self) -> bool:
        """
        Returns the information whether the flowtype can represent an energy
        :return: True/False
        """

        return self.unit.is_energy()

    def is_material(self) -> bool:
        """
        Returns the information whether the flowtype can represent a material
        :return: True/false
        """

        return self.unit.is_mass()

    def is_losses(self) -> bool:
        """
        Returns the information whether the flowtype represents losses
        :return: True/False
        """

        return self.represents_losses

    def unit_flow(self) -> str:
        """
        :return: [string] Standard unit description of the flow
        """
        return self.unit.get_unit_flow()

    def unit_flowrate(self) -> str:
        """
        :return: [string] Standard unit description of the flowrate
        """
        return self.unit.get_unit_flowrate()
