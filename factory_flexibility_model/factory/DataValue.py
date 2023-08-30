# IMPORT
import factory_flexibility_model.factory.Flowtype as ft


class DataValue:
    """
    This class is used to represent physical quantities by combining both a numerical value and a unit definition via a Flowtype.
    """

    def __init__(self, flowtype: ft.Flowtype, value: float, quantity_type: str):
        self.flowtype = flowtype  # flowtype of the entity
        self.value = value  # numerical value of the entity [single value or timeseries]
        self.quantity_type = quantity_type  # ["flow", "flowrate"]

    def set_value(self, value: float):
        """
        This function takes a value and sets it as Datavalue.value
        """
        self.value = value

    def value_expression(self, *, digits: int = 2) -> str:
        """
        This function returns a string describing the data in the correct unit and magnitude.

        :param digits: [int] Requested number of digits behind the decimal point; Standard: 2
        :return: [string] Description of the value with correct magnitude and unit
        """
        return self.flowtype.get_value_expression(
            self.value, self.quantity_type, digits
        )
