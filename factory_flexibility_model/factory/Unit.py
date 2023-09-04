import logging

import numpy as np


class Unit:
    def __init__(
        self,
        key: str,
        quantity_type: str,
        conversion_factor: float,
        magnitudes,
        units_flow,
        units_flowrate,
    ):
        """
        This function creates a unit-object.
        :param key: [str] identifier for the new unit
        :param quantity_type: [str] "mass", "energy" or "unknown"
        :param conversion_factor: The factor that transforms one unit of the given quantity to one unit of the base quantity of the quantity type
        :param magnitudes: [float list] A list of magnitudes that different prefixes for the unit are resembling. f.E. [1, 10, 100, 1000]
        :param units_flow: [str list] A list of units-descriptors that correspond to the given magnitudes when considering a flow f.e. [g, kg, t]
        :param units_flowrate: [str list] A list of units-descriptors that correspond to the given magnitudes when considering a flowrate f.e. [g/h, kg/h, t/h]
        """
        self.key = key
        self.conversion_factor = conversion_factor
        self.magnitudes = np.array(magnitudes)
        self.units_flow = units_flow
        self.units_flowrate = units_flowrate
        self.quantity_type = quantity_type

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
