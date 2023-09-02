import logging

import numpy as np


class Unit:
    def __init__(self, *, key: str = "unit"):
        self.key = "unspecified_unit"
        self.conversion_factor = 1
        self.magnitudes = np.array([1, 1000, 1000000, 1000000000, 1000000000000])
        self.units_flow = [" kWh", " MWh", " GWh", " TWh", " PWh"]
        self.units_flowrate = [" kW", " MW", " GW", " TW", " PW"]
        self.quantity_type = "energy"

        if key == "kW" or key == "energy":
            self.conversion_factor = 1
            self.magnitudes = np.array([1, 1000, 1000000, 1000000000, 1000000000000])
            self.units_flow = [" kWh", " MWh", " GWh", " TWh", " PWh"]
            self.units_flowrate = [" kW", " MW", " GW", " TW", " PW"]
            self.resource_type = "energy"
        elif key == "kg" or key == "mass":
            self.conversion_factor = 1
            self.magnitudes = np.array([1, 1000, 1000000, 1000000000, 1000000000000])
            self.units_flow = [" kg", " t", " kt", " mt", " gt"]
            self.units_flowrate = [" kg/h", " t/h", " kt/h", " mt/h", " gt/h"]
            self.resource_type = "material"
        elif key == "J":
            self.conversion_factor = 1 / 3.6
            self.magnitudes = np.array([1, 1000, 1000000, 1000000000])
            self.units_flow = [" MJ", " GJ", " TJ", " PJ"]
            self.units_flowrate = [" MJ/s", " GJ/s", " TJ/s", " PJ/s"]
            self.resource_type = "energy"
        else:
            if not key == "unit":
                logging.warning(
                    f"{key} is unknown as a unit prefix. The unit is created without further specification"
                )
            self.magnitudes = np.array([1, 1000, 1000000, 1000000000, 1000000000000])
            self.units_flow = [" Units", "k Units", "m. Units", "bn. Units", "T. Units"]
            self.units_flowrate = [
                " Units/h",
                "k Units/h",
                "m. Units/h",
                "bn. Units/h",
                "trillion Units/h",
            ]
            self.resource_type = "unspecified"

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
            return f"{round(value/self.magnitudes[magnitude], digits)}{self.units_flow[magnitude]}"
        elif quantity_type in ("flowrate", "Flow"):
            return f"{round(value/self.magnitudes[magnitude], digits)}{self.units_flowrate[magnitude]}"
        else:
            logging.error(
                f"The type '{quantity_type}' is an invalid argument for the .get_value_expression()-function. Valid types are 'flow' and 'flowrate'!"
            )
            return f"{value} [UNIT ERROR]"

    def is_energy(self) -> bool:
        """
        :return: True, if the unit describes an energy value
        """
        return self.resource_type == "energy"

    def is_material(self) -> bool:
        """
        :return: True, if the unit describes a material value
        """
        return self.resource_type == "material"

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
