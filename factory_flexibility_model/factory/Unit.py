# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: Factory_Flexibility_Model
# File Name: Unit.py
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

# CODE START
class Unit:
    def __init__(
        self,
        key: str,
        quantity_type: str,
        conversion_factor: float,
        magnitudes,
        units_flow,
        units_flowrate,
        *,
        name: str = None,
    ):
        """
        This function creates a unit-object.
        :param key: [str] identifier for the new unit
        :param quantity_type: [str] "mass", "energy" or "unknown"
        :param conversion_factor: The factor that transforms one unit of the given quantity to one unit of the base quantity of the quantity type
        :param magnitudes: [float list] A list of magnitudes that different prefixes for the unit are resembling. f.E. [1, 10, 100, 1000]
        :param units_flow: [str list] A list of units-descriptors that correspond to the given magnitudes when considering a flow f.e. [g, kg, t]
        :param units_flowrate: [str list] A list of units-descriptors that correspond to the given magnitudes when considering a flowrate f.e. [g/h, kg/h, t/h]
        :param name: [str] Description of the Unit for use in GUI
        """
        self.key = key
        self.conversion_factor = conversion_factor
        self.magnitudes = np.array(magnitudes)
        self.units_flow = units_flow
        self.units_flowrate = units_flowrate
        self.quantity_type = quantity_type
        if name is None:
            self.name = key
        else:
            self.name = name

    def get_value_expression(
        self, value: float, quantity_type: str, *, digits: int = 2
    ) -> str:
        """
        This function takes a numeric value, the information wether it describes a flow or a flowrate and optionally a number of rounding digits.
        It returns a string describing the data in the correct unit and magnitude.
        F.e: 15000000 + "flow" -> "1.5GW"
        :param value: [float] a numeric value in the base unit (kW/kg)
        :param type: [string] "flow" or "flowrate"
        :param digits: [int] Requested number of digits behind the decimal point; Standard: 2
        :return: [string] Description of the value with correct magnitude and unit
        """

        magnitude = np.argmin(abs(value - self.magnitudes))

        if quantity_type in ("flow", "Flow"):
            return f"{round(value/self.magnitudes[magnitude], digits)} {self.units_flow[magnitude]}"
        elif quantity_type in ("flowrate", "Flow"):
            return f"{round(value/self.magnitudes[magnitude], digits)} {self.units_flowrate[magnitude]}"
        else:
            logging.error(
                f"The type '{quantity_type}' is an invalid argument for the .get_value_expression()-function. Valid types are 'flow' and 'flowrate'!"
            )
            return f"{value} [UNIT ERROR]"

    def is_energy(self) -> bool:
        """
        :return: True, if the unit describes an energy value
        """
        return self.quantity_type == "energy"

    def is_mass(self) -> bool:
        """
        :return: True, if the unit describes a material value
        """
        return self.quantity_type == "mass"

    def get_unit_flow(self) -> str:
        """
        :return: [string] Standard unit description of the flow
        """
        return self.units_flow[0]

    def get_unit_flowrate(self) -> str:
        """
        :return: [string] Standard unit description of the flowrate
        """
        return self.units_flowrate[0]
