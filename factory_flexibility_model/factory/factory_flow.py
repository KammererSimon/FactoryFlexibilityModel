# FACTORY FLOW
# This package specifies a flow of energy/material

# IMPORT ENDOGENOUS COMPONENTS
import factory_flexibility_model.input_validations as iv


class flow:
    def __init__(self, name, flow_type, **kwargs):
        # specify valid inputs for "flow_type"
        valid_types = ["energy", "material", "unspecified"]

        # set the name (input validation happenes during factory.add_flow)
        self.name = name

        # set the flowtype
        if flow_type in valid_types:
            self.type = flow_type
        else:
            raise Exception(f"'{flow_type}' is not a valid type for a flow")

        # define, if the flow represents a type of losses or not
        if "to_losses" in kwargs:
            self.to_losses = iv.input(kwargs["to_losses"], "boolean")
        else:
            self.to_losses = False

        # set the name for the energy / throughput of the flow
        if "unit_energy" in kwargs:
            self.unit_energy = iv.input(kwargs["unit_energy"], "string")
        else:
            self.unit_energy = "unit_energy"

        # set the name for the power / flowrate of the flow
        if "unit_power" in kwargs:
            self.unit_power = iv.input(kwargs["unit_power"], "string")
        else:
            self.unit_power = "unit_power"

        # define a color that components with flows of this kind will be displayed
        if "component_color" in kwargs:
            # If color is specified use the value that has been handed over
            self.component_color = iv.input(kwargs["component_color"], "string")
        else:
            # otherwise use grey
            self.component_color = "#777777"

        # define a color that connections with flows of this kind will be displayed
        if "connection_color" in kwargs:
            # If color is specified use the value that has been handed over
            self.connection_color = iv.input(kwargs["connection_color"], "string")
        else:
            # otherwise use grey
            self.connection_color = "#999999"

        # specify the conversion-factor that converts one unit of the flow to kg/kWh
        if "conversion_factor" in kwargs:
            # If conversion factor is specified use the value that has been handed over
            self.conversion_factor = iv.input(kwargs["conversion_factor"], "float")
        else:
            # otherwise use 1:1 ratio
            self.conversion_factor = 1

        # specify a description for the flow to appear in evaluation diagrams
        if "flow_description" in kwargs:
            self.flow_description = kwargs["flow_description"]
        else:
            self.flow_description = f"Flow of {name}"

    def is_unknown(self):
        """
        Returns the information whether the flow is still considered as unknown
        :return: True/False
        """

        if self.name == "unknown":
            return True

        return False

    def is_energy(self):
        """
        Returns the information whether the flow can represent an energy
        :return: True/False
        """

        if self.type == "energy":
            return True

        return False

    def is_material(self):
        """
        Returns the information whether the flow can represent a material
        :return: True/false
        """

        if self.type == "material":
            return True

        return False

    def is_losses(self):
        """
        Returns the information whether the flow represents losses
        :return: True/False
        """

        if self.to_losses:
            return True

        return False
