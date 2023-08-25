# FACTORY FLOW
# This package specifies a flowtype of energy/material

# IMPORT ENDOGENOUS COMPONENTS
import factory_flexibility_model.input_validations as iv


class flowtype:
    def __init__(
        self,
        name,
        resource_type,
        *,
        to_losses=None,
        unit_flow=None,
        unit_flowrate=None,
        conversion_factor=None,
        description=None,
        color=None,
    ):
        """
        This function creates a new flowtype-object and adds it to the factory
        :param name: [String] name identifier for the new flowtype
        :param resource_type: [string] "energy" / "material" / "unspecified"
        :param to_losses: [Boolean] Specifies if the connection is deducting losses
        :param unit_flow: [String] Unit description for labeling flows of the flowtype
        :param unit_flowrate: [String] Unit description for labeling the flowrate of the flowtype
        :param conversion_factor: [float] conversion factor between one unit of the flow and one baseunit of the flow ressource type
        :param description: [String] Description of the flow, just for GUI and labeling purposes
        :param color: [String; #XXXXXX] Color code for displaying the flow in GUI and Figures
        """

        # specify valid inputs for "flow_type"
        valid_types = ["energy", "material", "unspecified"]

        # set the name (validate validation happenes during factory.add_flow)
        self.name = name

        # set the flowtype
        if resource_type in valid_types:
            self.type = resource_type
        else:
            raise Exception(f"'{resource_type}' is not a valid type for a flowtype")

        # define, if the flowtype represents a type of losses or not
        if to_losses is not None:
            self.to_losses = iv.validate(to_losses, "boolean")
        else:
            self.to_losses = False

        # set the name for the throughput of the flowtype
        if unit_flow is not None:
            self.unit_flow = iv.validate(unit_flow, "string")
        else:
            self.unit_flow = "flow_units"

        # set the name for flowrate of the flowtype
        if unit_flowrate is not None:
            self.unit_flowrate = iv.validate(unit_flowrate, "string")
        else:
            self.unit_flowrate = "flowrate_units"

        # define a color that components with flows of this kind will be displayed
        if color is not None:
            # If color is specified use the value that has been handed over
            self.ccolor = iv.validate(color, "string")
        else:
            # otherwise use grey
            self.color = "#777777"

        # specify a description for the flowtype to appear in evaluation diagrams
        if description is not None:
            self.description = description
        else:
            self.description = f"Flowtype of {name}"

    def is_unknown(self):
        """
        Returns the information whether the flowtype is still considered as unknown
        :return: True/False
        """

        if self.name == "unknown":
            return True

        return False

    def is_energy(self):
        """
        Returns the information whether the flowtype can represent an energy
        :return: True/False
        """

        if self.type == "energy":
            return True

        return False

    def is_material(self):
        """
        Returns the information whether the flowtype can represent a material
        :return: True/false
        """

        if self.type == "material":
            return True

        return False

    def is_losses(self):
        """
        Returns the information whether the flowtype represents losses
        :return: True/False
        """

        if self.to_losses:
            return True

        return False
