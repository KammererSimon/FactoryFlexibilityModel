# FACTORY COMPONENTS
# This script contains the classes that specify all the components used to create a factory architecture.
# "Component" is a general parent class, all other classes are children representing a specific technical behaviour.

# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: Factory_Flexibility_Model
# File Name: Components.py
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

# IMPORT
import logging

import numpy as np

import factory_flexibility_model.factory.Connection as co
import factory_flexibility_model.factory.Flowtype as ft
import factory_flexibility_model.io.input_validations as iv


# COMPONENT PARENT CLASS
class Component:
    def __init__(self, key: str, factory, *, flowtype: str = None, name: str = None):
        self.factory = (
            factory  # enables callbacks to the factory the Component is assigned to
        )
        if name is None:
            self.name = key  # Identifier, only used for console and GUI-outputs
        else:
            self.name = name
        self.key = key  # Identifier for internal use
        self.description = ""  # Placeholder for a description of the Component for better identification
        self.determined = (
            False  # only useful for some subclasses, but defining it for all of
        )
        self.from_slack = (
            None  # Placeholder for a possible connection coming from a slack component
        )
        self.inputs = (
            []
        )  # initialize list, which stores pointers to all input connections
        self.max_inputs = (
            1  # maximum number of connectable inputs -> 1 for most components
        )
        self.max_outputs = (
            1  # maximum number of connectable outputs -> 1 for most components
        )
        self.outputs = (
            []
        )  # initialize list, which stores pointers to all output connections
        self.to_slack = (
            None  # Placeholder for a possible connection to a slack component
        )
        self.type = "unknown"  # set keyword "unknown" if no type is specified

        # delivered by the scenario
        self.scenario_data = (
            {}
        )  # empty dictionary. If the Component requires data, that will only been
        # known when the scenario is specified this will be stored here as a list
        # of attribute:value combinations

        # FLOWTYPE DETERMINATION
        if flowtype is not None:
            if isinstance(flowtype, ft.Flowtype):
                self.flowtype = flowtype
            elif isinstance(flowtype, str):
                try:
                    self.flowtype = factory.flowtypes[flowtype]
                except:
                    logging.warning(
                        f"Given flowtype {flowtype} is not defined within {factory.name}. Flowtype is set as 'unknown' to proceed."
                    )
                    self.flowtype = factory.flowtypes[
                        "unknown"
                    ]  # initialize with "unknown"

        else:
            self.flowtype = factory.flowtypes["unknown"]  # initialize with "unknown"

    def set_input(self, connection: co.Connection):
        """
        This function sets the given connection as an input for the component
        :param connection: [fm.Connection-object]
        """

        # If the input comes from a slack: store it within .from_slack
        if connection.type == "slack":
            self.from_slack = connection

        # Otherwise make sure that the component allows for another input
        elif len(self.inputs) < self.max_inputs:

            # add connection to the inputs list
            self.inputs.append(connection)

            # if self doesn't have its flowtype already determined it is checked, whether the flowtype can be specified via the connection
            if self.flowtype.is_unknown():
                if not connection.flowtype.is_unknown():
                    self.update_flowtype(connection.flowtype)
            elif connection.flowtype.is_unknown():
                connection.update_flowtype(self.flowtype)

        # If not: create exception
        else:
            logging.critical(
                f"ERROR: Cannot create connection '{connection.name}', because {self.name} doesn't accept any more inputs"
            )
            raise Exception

    def set_output(self, connection: co.Connection):
        """
        This function sets the given connection as an output for the component
        :param connection: [fm.Connection-object]
        """

        # If the output goes to a slack: store it within .to_slack
        if connection.type == "slack":
            self.to_slack = connection

        # If the output goes to losses: Raise exception! Valid loss-connections are handled by components individually
        elif connection.type == "losses":
            logging.critical(
                f"ERROR: Components of type {self.type} are not allowed to have a connection to losses"
            )
            raise Exception

        # If the connection is valid till now: make sure that the component allows for another output
        elif len(self.outputs) < self.max_outputs:

            # add connection to the outputs-list
            self.outputs.append(connection)

            # if self doesn't have its flowtype already determined it is checked, whether the flowtype can be specified via the connection
            if self.flowtype.is_unknown():
                if not connection.flowtype.is_unknown():
                    self.update_flowtype(connection.flowtype)
            elif connection.flowtype.is_unknown():
                connection.update_flowtype(self.flowtype)

        # If no further output is possible: raise exception
        else:
            logging.critical(
                f"ERROR: Cannot create output connection {connection.name}, because {self.name} doesn't accept any more outputs"
            )
            raise Exception

    def update_flowtype(self, flowtype: str):
        # FLOWTYPE DETERMINATION
        logging.debug(
            f"            (UPDATE) The flowtype of Component {self.name} is now defined as {flowtype.name}"
        )
        self.flowtype = flowtype
        if self.max_inputs > 0:
            for i in self.inputs:
                i.update_flowtype(flowtype)
        if self.max_outputs > 0:
            for i in self.outputs:
                i.update_flowtype(flowtype)

    def set_parameter(self, timesteps: int, parameter: str, parameters: dict) -> bool:
        """
        This function is mostly an input validation, that checks, if the parameters that the user wants to set are compatible to each other and fullfill the data requirements of the Simulation.
        # If all checks are passed the parameter given will be written to self
        :param: timesteps:  [int] number of timesteps of the current factory
        :param: parameter:  [str] Parameter out of the parameters-list that will be set during execution
        :param: parameters: [dict] List of all parameters that have to be configured + their given values
        :return: [True] -> Edits the configuration of the Component-object
        """

        # define lists of internal boolean variables, that are not up to be changed directly by the user
        internal_booleans = {
            "Pmin_limited": "Pmin",
            "Pmax_limited": "power_max",
            "chargeable": "cost",
            "soc_determined": "soc_start",
            "determined": "power",
            "Pramp_Limited": "Pmax_ramp_pos or Pmax_ramp_neg",
        }

        # define list of constants that have to remain untouched in general
        constants = {
            "type",
            "factory",
            "inputs",
            "max_inputs" "max_outputs" "outputs",
            "key",
            "fixed_ratio_output",
        }

        # define list of parameters, that have to be positive Floats
        pos_floats = {"Pmax_charge", "Pmax_discharge", "R", "C"}

        # define list of parameters that have to be floats between 0 and 1
        ratios = {"efficiency", "leakage_time", "leakage_SOC"}

        # HANDLE PARAMETERS FROM THE LISTS ABOVE:
        # handle attempts to change bool-constants
        if parameter in constants and hasattr(self, parameter):
            logging.critical(
                f"ERROR: Cannot change attribute {parameter} for {self.name} "
                f"as it is crucial for the datastructure of the factory"
            )
            raise Exception

        # handle attempts to directly change internal boolean variables
        if parameter in internal_booleans and hasattr(self, parameter):
            logging.critical(
                f"ERROR: Don't bother with configurating the attribute {parameter} for {self.name}! "
                f"Just hand over a value or timeseries for {internal_booleans[parameter]} and "
                f"the datastructure will take care of the rest"
            )
            raise Exception

        # handle positive Float variables
        if parameter in pos_floats and hasattr(self, parameter):
            setattr(
                self,
                parameter,
                iv.validate(parameters[parameter], "float", positive=True),
            )

        # handle ratio variables
        elif parameter in ratios and hasattr(self, parameter):
            setattr(self, parameter, iv.validate(parameters[parameter], "0..1"))

        # HANLDE GENERAL PARAMETERS:
        # handle descriptions
        elif parameter == "description":
            self.description = iv.validate(parameters[parameter], "string")
        elif parameter == "flowtype_description" and hasattr(self, parameter):
            self.flowtype_description = iv.validate(parameters[parameter], "string")
        elif parameter == "name":
            self.name = iv.validate(parameters[parameter], "string")

        # handle scenario_parameters
        elif parameter == "scenario_data":
            if not isinstance(parameters[parameter], dict):
                logging.critical(
                    f"ERROR while assigning scenario_data for {self.name}: scenario_data must be specified as a dictionary with attribute:value-combinations!"
                )
                raise Exception
            self.scenario_data = parameters[parameter]
            self.scenario_dependent = True

        elif parameter == "flowtype":
            logging.warning(
                f"Cannot set the flowtype of {self.name} during a set_configuration() prompt. Flows are a "
                f"structural part of the system architecture and therefore MUST be defined while "
                f"creating the components!"
            )

        # handle given availability timeseries
        elif parameter == "availability" and hasattr(self, parameter):
            # self.determined overrides the pmax_constraint in the optimization.
            # Setting both is useless und may lead to an unexpected behavior of the Simulation. check and warn the user:
            if self.determined:
                logging.warning(
                    f"the power of Component {self.name} is already defined as determined. Availability has "
                    f"been set, but will have no effect during the Simulation"
                )

            # Availability without power_max is useless:
            if not self.power_max_limited and "power_max" not in parameters:
                logging.warning(
                    f"{self.name} does not have a power_max set. Added timeseries for availability has no "
                    f"effekt until power_max is specified!"
                )

            # prepare the input for following validations:
            data = iv.validate(parameters[parameter], "%", timesteps=timesteps)

            # values for availability must be >=0:
            if min(data) < 0:
                logging.critical(
                    f"given timeseries for availability of {self.name} contains negative Values. "
                    f"Values for availability must be between 0 and 1!"
                )
                raise Exception
            # values for availability must be <=1:
            if max(data) > 1:
                data = data / max(data)
                logging.warning(
                    f"given data for availability of Component {self.name} containes values >1. The timeseries has been normalized. If this was not your intent, check the input data again!"
                )

            # setting an availability may interfere with the given Pmin...check this:
            # power_max/Pmin may already be set or already handed over but pending to be set...determine the actual constraints:
            if "power_max" in parameters:
                # input validation for power_max includes conflicts with .determined and .Pmin. Both is done here as well, so it should be fine this way
                power_max = iv.validate(
                    parameters[parameter], "float", timesteps=timesteps
                )
            else:
                power_max = self.power_max

            if "power_min" in parameters:
                # input validation for power_max includes conflicts with .determined and .Pmin. Both is done here as well, so it should be fine this way
                power_min = iv.validate(
                    parameters[parameter], "float", timesteps=timesteps
                )
            else:
                power_min = self.power_min

            # check, if power_min < power_max*availability
            if self.power_min_limited:

                if not self.power_max_limited:
                    logging.critical(
                        f"error while configuring availability of {self.name}: "
                        f"Cannot set an availability in combination with Pmin before defining power_max!"
                    )
                    raise Exception

                if any(power_max * data < power_min):
                    logging.critical(
                        f"error while configuring availability of {self.name}: "
                        f"combination of power_max and availability conflicts with Pmin! "
                        f"You're indirectly trying to set a power_max < Pmin for at least one timestep"
                    )
                    raise Exception

            # all checks passed? set the value!
            self.availability = data

        # handle visualisation parameters
        elif parameter == "visualize" and hasattr(self, parameter):
            self.visualize = iv.validate(parameters[parameter], "boolean")
        elif parameter == "flowtype_description" and hasattr(self, parameter):
            self.flowtype_description = iv.validate(parameters[parameter], "str")

        # HANDLE UNKNOWN PARAMETERS:
        # handle attributes that are existing and may be usefull to change, but are not considered yet
        elif hasattr(self, parameter):
            setattr(self, parameter, parameters[parameter])
            logging.warning(
                f"The attribute {parameter} was found in {self.name}, but is not part of the ordinary configuration routine. It has been set to the given value without input validation. This could lead to errors during the Simulation"
            )

        # if no option matched so far the parameter is unknown or invalid
        else:
            # warn the user
            logging.warning(
                f" The parameter {parameter} was ignored for Component {self.name}, because it is unknown"
            )
            return False

        return True


# INHERITED COMPONENT CLASSES
class Converter(Component):
    def __init__(self, key: str, factory, name: str = None):
        # STANDARD COMPONENT ATTRIBUTES
        super().__init__(key, factory, name=name)

        # STRUCTURAL ATTRIBUTES
        self.capacity_charge = 0  # cost per unit conversion capacity installed.

        self.description = (
            "Unspecified Converter"  # Description for better identification in UI
        )
        self.inputs_energy = (
            []
        )  # separate list to store information about energy inputs
        self.inputs_material = (
            []
        )  # separate list to store information about material inputs
        self.max_inputs = 20  # converters allow for multiple inputs
        self.max_outputs = 20  # converters allow for multiple outputs
        self.outputs_energy = (
            []
        )  # separate list to store information about energy outputs
        self.outputs_material = (
            []
        )  # Separate list to store information about ematerial outputs
        self.to_Mlosses = (
            []
        )  # Placeholder for pointer directing to the material losses destination
        self.to_ELosses = (
            []
        )  # Placeholder for pointer directing to the energy losses destination
        self.type = "converter"  # specify Component as converter

        # POWER CONSTRAINTS
        self.switchable = False  # Set "True" if the converte can be turned on/off in addition to the power-constraints
        self.power_max_limited = (
            False  # determines, whether the maximum Power of the converter is limited
        )
        self.power_max = (
            np.ones(factory.timesteps) * 1000000000
        )  # big M, just in case....
        self.power_min_limited = (
            False  # determines, whether the minimum Power of the converter is limited
        )
        self.power_min = np.zeros(
            factory.timesteps
        )  # doesn't do anything as long as it's zero
        self.availability = np.ones(
            factory.timesteps
        )  # used for all classes with power_max, to determine the maximum power timedependent. is initialized as all ones, so that it has no effect if not specificly adressed
        self.rampup_cost = (
            0  # cost for ramping up the utilization by one conversion unit
        )
        self.ramp_power_limited = (
            False  # Set "True, if the power gradient of the Component is limited
        )
        self.power_ramp_max_pos = 10000000  # maximum absolute positive power gradient per timestep, initialized as big M
        self.power_ramp_max_neg = 10000000  # maximum absolute negative power gradient per timestep, initialized as big M

        # EFFICIENCY PARAMETERS
        self.delta_eta_high = 0  # efficiency drop when leaving the nominal operation point towards higher values. standard value of zero -> does nothing unless changed
        self.delta_eta_low = 0  # efficiency drop when leaving the nominal operation point towards lower values. standard value of zero -> does nothing unless changed
        self.eta_max = (
            1  # standard value of 1 as efficiency -> does nothing unless changed
        )
        self.eta_base = 1  # helping variable for visualisation: expresses, how much losses occur independent of variable eta because of the in- and outputweights, is calculated during .check_validity
        self.power_nominal = 0  # just a value to initialize it, no neutral initialization possible here...should be overwritten when used.
        self.eta_variable = (
            False  # standard value is False -> does nothing unless changed
        )
        logging.debug(
            f"        - New converter {self.name} created with Component-key{self.key}"
        )

    def set_input(self, connection: co.Connection):
        """
        This function sets the given connection as an input for the deadtime-component. The weight is either taken from weight or weight destination. Input limit of parent component is being ignored
        :param connection: [fm.Connection-object]
        """

        self.inputs.append(connection)
        if connection.flowtype.is_energy():
            self.inputs_energy.append(connection)
        elif connection.flowtype.is_material():
            self.inputs_material.append(connection)
            # converters do not have a material losses connection by default.check if one is required
            if self.to_Mlosses == []:
                self.factory.add_connection(
                    self.key,
                    "losses_material",
                    key=f"{self.key}_to_Mlosses",
                    name=f"{self.name}_to_Mlosses",
                    weight=0.01,
                    type="losses",
                )  # auto generate a connection to losses
        else:
            logging.critical(
                f"Invalid flowtype handed over to {self.name}.set_input(): {connection.flowtype.name}"
            )
            raise Exception

    def set_output(self, connection: co.Connection):
        """
        This function sets the given connection as an output for the component. Output limit of parent component is being ignored
        :param connection: [fm.Connection-object]
        """
        # handle connections to losses if specified:
        if connection.type == "losses":
            if connection.flowtype.is_energy():
                self.to_Elosses = connection
            elif connection.flowtype.is_material():
                self.to_Mlosses = connection
            else:
                logging.critical(
                    "invalid flowtype handed over to converter.set_output()!"
                )
                raise Exception
        else:
            self.outputs.append(connection)
            if connection.flowtype.is_energy():
                self.outputs_energy.append(connection)
            elif connection.flowtype.is_material():
                self.outputs_material.append(connection)
            else:
                logging.critical(
                    f"connection with invalid flowtype connected via {self.name}.set_output(): {connection.flowtype.name}"
                )
                raise Exception

    def update_flowtype(self, flowtype: str):
        """
        This function acts as a broadcast through the factory to determine regions with common flows.
        If any flow within the factory is being defined it is called to make sure, that
        """
        # break the recursive broadcast # FLOWTYPE DETERMINATION

    def validate_eta(self) -> bool:
        """
        This function validates, if the current definition of pmin/pmax and efficiency behaviour is consistent.
        :return: [boolean] True, if the current configuration is valid.
        """

        if self.power_nominal < min(self.power_min) or self.power_nominal > max(
            self.power_max
        ):
            logging.warning(
                f"The nominal operation Point of {self.name} is outside its Power limits. Is this on purpose?"
            )

        if (
            self.eta_max
            - self.delta_eta_low * (self.power_nominal - min(self.power_min))
            <= 0
        ):
            logging.critical(
                f"Error during configuration of the efficiency parameters of {self.name}: "
                f"Efficiency reaches 0% at operation points between Pnominal and Pmin. "
                f"To avoid this set power_min to at least {self.power_nominal - self.eta_max / self.delta_eta_low} "
                f"or set Delta_Eta_low to a maximum of {self.eta_max / (self.power_nominal - max(self.power_min))}"
            )
            raise Exception

        if (
            self.eta_max
            - self.delta_eta_high * (max(self.power_max) - self.power_nominal)
            <= 0
        ):
            logging.critical(
                f"Error during configuration of the efficiency parameters of {self.name}: "
                f"Efficiency reaches 0% at operation points between Pnominal and power_max. "
                f"To avoid this set power_max to less than {self.power_nominal + self.eta_max / self.delta_eta_high} "
                f"or set Delta_Eta_high to a maximum of {self.eta_max / (max(self.power_max) - self.power_nominal)}"
            )
            raise Exception
        return True

    def set_configuration(self, timesteps: int, parameters: dict) -> bool:
        """
        This function sets the configuration for the component. All parameters to be defined can be handed over as key-value-pairs within a single dictionary.
        :param timesteps: [int] The number of timesteps that stationary values are scaled to and user given timeseries need to have at minimum
        :param parameters: [dict] dictionary with key-value-combinations that specify all the parameters to be configured.
        :return: [boolean] True, if the configuration war successfull
        """
        # iterate over all given parameters and figure out how to handle them...
        for parameter in parameters:
            # HANDLE CONVERTER-SPECIFIC PARAMETERS
            # handle power_max/Pmin constraints
            if parameter == "power_max":
                self.power_max_limited = True
                self.power_max = iv.validate(
                    parameters["power_max"], "float", timesteps=timesteps
                )

            elif parameter == "power_min":
                self.power_min_limited = True
                self.power_min = iv.validate(
                    parameters["power_min"], "float", timesteps=timesteps
                )

            # handle Ramping constraints
            elif parameter == "power_ramp_max_pos":
                self.power_ramp_max_pos = iv.validate(
                    parameters["power_ramp_max_pos"], "float", positive=True
                )
                self.ramp_power_limited = True
                if self.switchable:
                    logging.critical(
                        f"ERROR: cannot set ramping constraints for Component {self.name}, because it is already defined as switchable"
                    )
                    raise Exception
            elif parameter == "power_ramp_max_neg":
                self.power_ramp_max_neg = iv.validate(
                    parameters["power_ramp_max_neg"], "float", positive=True
                )
                self.ramp_power_limited = True
                if self.switchable:
                    logging.critical(
                        f"ERROR: cannot set ramping constraints for Component {self.name}, because it is already defined as switchable"
                    )
                    raise Exception
            elif parameter == "switchable":
                self.switchable = iv.validate(parameters["switchable"], "boolean")
                if self.ramp_power_limited:
                    logging.critical(
                        f"ERROR: cannot set Component {self.name} as switchable, because it already has ramping constraints defined"
                    )
                    raise Exception
            # handle efficiency parameters
            elif parameter == "delta_eta":
                # delta_eta is split into two values within the Simulation and the converter-object. The user can specify it symmetrically by just giving a value for "delta_eta".
                # the given value will be used for both segments of the operation range
                self.delta_eta_low = iv.validate(parameters["delta_eta"], "0..1")
                self.delta_eta_high = iv.validate(parameters["delta_eta"], "0..1")
                self.eta_variable = True
            elif parameter == "delta_eta_high":
                self.delta_eta_high = iv.validate(parameters["delta_eta_high"], "0..1")
                self.eta_variable = True
            elif parameter == "delta_eta_low":
                self.delta_eta_low = iv.validate(parameters["delta_eta_low"], "0..1")
                self.eta_variable = True
            elif parameter == "eta_max":
                self.eta_max = iv.validate(parameters["eta_max"], "0..1")
                self.eta_variable = True
            elif parameter == "power_nominal":
                self.power_nominal = iv.validate(parameters["power_nominal"], "float")

            # HANDLE GENERAL PARAMETERS
            else:
                if not super().set_parameter(timesteps, parameter, parameters):
                    # in case the function failed to set the parameter it returns false
                    continue

            logging.debug(f"        - {parameter} set for {self.type} {self.name}")
        if self.eta_variable:
            # make sure, that the efficiency is still valid for every possible operation point
            self.validate_eta()


class Deadtime(Component):
    def __init__(self, key: str, factory, name: str = None):
        # STANDARD COMPONENT ATTRIBUTES
        super().__init__(key, factory, name=name)

        self.delay = (
            0  # how many timesteps does the deadtime delay the flow? Iniutialized as 0
        )

        self.type = "deadtime"  # specify Component as deadtime

        logging.debug(
            f"        - New deadtime {self.name} created with Component-key {self.key}"
        )

    def set_configuration(self, timesteps: int, parameters: dict) -> bool:
        """
        This function sets the configuration for the component. All parameters to be defined can be handed over as key-value-pairs within a single dictionary.
        :param timesteps: [int] The number of timesteps that stationary values are scaled to and user given timeseries need to have at minimum
        :param parameters: [dict] dictionary with key-value-combinations that specify all the parameters to be configured.
        :return: [boolean] True, if the configuration war successfull
        """
        # iterate over all given parameters and figure out how to handle them...
        for parameter in parameters:
            # HANDLE DEADTIME-SPECIFIC PARAMETERS
            if parameter == "delay":
                self.delay = iv.validate(parameters["delay"], "integer")
                if (
                    not self.delay == "$parameter$"
                    and self.factory.timesteps <= self.delay
                ):
                    logging.critical(
                        f"ERROR: Cannot set the delay of Component {self.name} to {self.delay}, "
                        f"because the factory only allows for {self.factory.timesteps} timesteps"
                    )
                    raise Exception
            # HANDLE GENERAL PARAMETERS
            else:
                self.set_parameter(timesteps, parameter, parameters)

            logging.debug(f"        - {parameter} set for {self.type} {self.name}")


class Heatpump(Component):
    def __init__(self, key: str, factory, name: str = None):
        # STANDARD COMPONENT ATTRIBUTES
        super().__init__(key, factory, name=name)

        # STRUCTURAL ATTRIBUTES
        self.description = (
            "Unspecified Heatpump"  # Description for better identification in UI
        )
        self.input_main = []  # input from energy supply
        self.input_gains = []  # input from heatsource
        self.max_inputs = 2  # heatpumps allow for an electricity and a heatsource input
        self.max_outputs = 1  # heatpumps allow for an useenergy and losses output
        self.type = "heatpump"  # specify Component as heatpump

        # POWER CONSTRAINTS
        self.power_max_limited = (
            False  # determines, whether the maximum Power of the converter is limited
        )
        self.power_max = (
            np.ones(factory.timesteps) * 1000000000
        )  # big M, just in case....

        # EFFICIENCY PARAMETERS
        self.temperature_source = (
            np.ones(factory.timesteps) * 20
        )  # temperature level of the heat source; Standard value of 20°C
        self.cop_profile = np.ones(
            500
        )  # profile determining the cop of the heatpump. Array with values for temperatures ranging from 0 to 500 Kelvin
        self.cop = np.ones(
            factory.timesteps
        )  # timeseries of operating cop, based on cop profile and source temperature. Is being calculated when one of both attributes is set

        logging.debug(
            f"        - New heatpump {self.name} created with Component-key{self.key}"
        )

    def calculate_cop_timeseries(self):
        """
        This function calculates the realizable cop for every timestep based on the source temperature profile and the cop profile. The function simply performs a lookup of the cop at the source temperature of every timestep.
        :return: None; recalculates self.cop
        """
        # iterate over all timesteps
        for t in range(len(self.temperature_source)):
            # lookup the correct COP value in the cop profile that corresponds to the source temperature in timestep t
            self.cop[t] = self.cop_profile[
                int(self.temperature_source[t]) + 273
            ]  # 273 bc the cop profile is based on celvin and the source temperature is in °C

    def set_input(self, connection: co.Connection):
        """
        This function sets the given connection as an input for the heatpump-component.
        :param connection: [fm.Connection-object]
        """

        self.inputs.append(connection)
        if connection.flowtype.is_energy():
            if connection.type == "gains" or connection.flowtype.key == "heat":
                if self.input_gains != []:
                    logging.critical(
                        f"Cannot set {connection.name} as input for Heatpump {self.name}, because it already has a heat source input."
                    )
                    raise Exception
                else:
                    self.input_gains = connection
            else:
                if self.input_main != []:
                    logging.critical(
                        f"Cannot set {connection.name} as input for Heatpump {self.name}, because it already has a main energy input."
                    )
                    raise Exception
                else:
                    self.input_main = connection
        elif connection.flowtype.is_material():
            logging.critical(
                f"Heatpump {self.name} is not allowed to have any material inputs!"
            )
            raise Exception
        else:
            logging.critical(
                f"Invalid flowtype handed over to {self.name}.set_input(): {connection.flowtype.name}"
            )
            raise Exception

    def set_output(self, connection: co.Connection):
        """
        This function sets the given connection as an output for the component. Output limit of parent component is being ignored
        :param connection: [fm.Connection-object]
        """
        # Make sure, that no already defined output is being overwritten
        if self.outputs != []:
            logging.critical(
                f"Cannot set another output for heatpump {self.name}, because it already has its output defined!"
            )
            raise Exception

        if not connection.flowtype.key in ["heat", "unknown"]:
            logging.critical(
                f"Invalid flowtype {connection.flowtype.name} connected to heatpump {self.name}. The flowtype has to be heat."
            )
            raise Exception

        # handle connections to losses if specified:
        if connection.type == "losses":
            logging.warning(
                f"Heatpumps do not support loss outputs. The connection {connection.name} is therefore used as the regular output for {self.name}"
            )

        self.outputs.append(connection)

    def update_flowtype(self, flowtype: str):
        """
        The flowtypes at heatpumps are predefined. Therefore this function just interrupts the browadcast.
        """
        # break the recursive broadcast # FLOWTYPE DETERMINATION

    def set_configuration(self, timesteps: int, parameters: dict) -> bool:
        """
        This function sets the configuration for the component. All parameters to be defined can be handed over as key-value-pairs within a single dictionary.
        :param timesteps: [int] The number of timesteps that stationary values are scaled to and user given timeseries need to have at minimum
        :param parameters: [dict] dictionary with key-value-combinations that specify all the parameters to be configured.
        :return: [boolean] True, if the configuration war successfull
        """
        # iterate over all given parameters and figure out how to handle them...
        for parameter in parameters:
            # HANDLE HEATPUMP-SPECIFIC PARAMETERS
            if parameter == "power_max":
                self.power_max_limited = True
                self.power_max = iv.validate(
                    parameters["power_max"], "float", timesteps=timesteps
                )

            elif parameter == "temperature_source":
                self.temperature_source = iv.validate(
                    parameters["temperature_source"], "float", timesteps=timesteps
                )
                self.calculate_cop_timeseries()  # recalculate the timeseries of relevant COP based on the new source temperature profile

            elif parameter == "cop_profile":
                self.cop_profile = iv.validate(
                    parameters["cop_profile"], "float", timesteps=500
                )
                self.calculate_cop_timeseries()  # recalculate the timerseries of relevant COP based on the new cop profile

            # HANDLE GENERAL PARAMETERS
            else:
                if not super().set_parameter(timesteps, parameter, parameters):
                    # in case the function failed to set the parameter it returns false
                    continue

            logging.debug(f"        - {parameter} set for {self.type} {self.name}")


class Pool(Component):
    def __init__(self, key, factory, *, flowtype=None, name: str = None):
        super().__init__(key, factory, flowtype=flowtype, name=name)
        self.max_inputs = 20
        self.max_outputs = 20
        self.type = "pool"  # identify Component as pool
        self.description = "Unspecified Pool"  # Description for identification in UI
        self.flowtype_description = (
            "Unspecified flowtype"  # Description for identification in UI
        )

        logging.debug(
            f"        - New pool {self.name} created with Component-key {self.key}"
        )

    def set_configuration(self, timesteps: str, parameters: dict):
        """
        This function sets the configuration for the component. All parameters to be defined can be handed over as key-value-pairs within a single dictionary.
        :param timesteps: [int] The number of timesteps that stationary values are scaled to and user given timeseries need to have at minimum
        :param parameters: [dict] dictionary with key-value-combinations that specify all the parameters to be configured.
        :return: [boolean] True, if the configuration war successfull
        """
        # iterate over all given parameters and figure out how to handle them...
        for parameter in parameters:
            # HANDLE GENERAL PARAMETERS
            super().set_parameter(timesteps, parameter, parameters)
            logging.debug(f"        - {parameter} set for {self.type} {self.name}")


class Sink(Component):
    def __init__(self, key: str, factory, *, flowtype: str = None, name: str = None):
        super().__init__(key, factory, flowtype=flowtype, name=name)
        self.availability = np.ones(
            factory.timesteps
        )  # used for all classes with power_max, to determine the maximum power timedependent. is initialized as all ones, so that it has no effect if not specificly adressed
        self.causes_emissions = (
            False  # Does the usage of this destination cause any CO2-Emissions?
        )
        self.chargeable = False  # Must be changed to "true", if the utilization of the source is connected with costs
        self.cost = []  # must be specified by set_configuration
        self.co2_emissions_per_unit = (
            0  # How many kg CO2 are emitted by giving one unit to this destination?
        )
        self.demand = []  # must be specified by set_configuration
        self.description = (
            "Unspecified Sink"  # Description for better identification in UI
        )
        self.determined = False  # True -> Output is determined by timeseries; False -> Output is result of optimization
        self.flowtype_description = ""  # A clearer description of the flowtype (e.g. "Room Heating for Main Office"), just for the visualisation
        self.is_onsite = True  # Set to False if the flowtype is leaving the factory without being consumed
        self.max_total_input_limited = (
            False  # specify if maximum cummulative input is limited
        )
        self.max_total_input = None  # maximum cummulative input over all timesteps
        self.power_max_limited = False  # specify if maximum output is limited
        self.power_max = []  # must be specified by set_configuration
        self.power_min_limited = False  # specify if the minimum output power is limited
        self.power_min = []  # must be specified by set_configuration
        self.refundable = False  # Must be changed to True, if reccources/energy flowing into the destination are creating a revenue
        self.revenue = (
            []
        )  # must be set by set_configuration, specifies the revenue in €/unit
        self.type = "sink"  # specify Component as a global destination

        logging.debug(
            f"        - New sink {self.name} of flowtype {self.flowtype.unit.quantity_type} "
            f"created with Component-key {self.key}"
        )

    def set_configuration(self, timesteps: int, parameters: dict):
        """
        This function sets the configuration for the component. All parameters to be defined can be handed over as key-value-pairs within a single dictionary.
        :param timesteps: [int] The number of timesteps that stationary values are scaled to and user given timeseries need to have at minimum
        :param parameters: [dict] dictionary with key-value-combinations that specify all the parameters to be configured.
        :return: [boolean] True, if the configuration war successfull
        """
        # iterate over all given parameters and figure out how to handle them...
        for parameter in parameters:
            # HANDLE SINK-SPECIFIC PARAMETERS
            # handle power_max/Pmin and demand constraints
            if parameter == "power_max":
                self.power_max_limited = True
                self.power_max = iv.validate(
                    parameters["power_max"], "float", timesteps=timesteps
                )
                # check, if power_min and power_max constraints are compatible
                if self.power_min_limited:
                    if any(self.power_min > self.power_max * self.availability):
                        logging.critical(
                            f"ERROR: given timeseries Pmin and power_max for Component {self.name} are not compatible"
                        )
                        raise Exception
                # check, if power_max constraints is compatible with determined power
                if self.determined:
                    if sum(self.demand <= self.power_max) < timesteps:
                        logging.critical(
                            f"ERROR: Already determined Power is incompatible with the power_max you're trying to set for Component {self.name}"
                        )
                        raise Exception

            elif parameter == "power_min":
                self.power_min_limited = True
                self.power_min = iv.validate(
                    parameters["power_min"], "float", timesteps=timesteps
                )

                # check, if Pmin and power_max constraints are compatible
                if self.power_max_limited:
                    if any(self.power_min > self.power_max * self.availability):
                        logging.critical(
                            f"ERROR: given timeseries power_min and power_max "
                            f"for Component {self.name} are not compatible"
                        )
                        raise Exception

                # check, if power_min constraints is compatible with determined power
                if self.determined:
                    if sum(self.power >= self.power_min) < timesteps:
                        logging.critical(
                            f"ERROR: Already determined Power is incompatible with the Pmin you're trying to set for Component {self.name}"
                        )
                        raise Exception

                # check, if power_min constraint is compatible with availability and power_max
                if self.power_max_limited:
                    if min(self.power_max * self.availability) < self.power_min:
                        logging.critical(
                            f"The given combination of power_max and availability for the source {self.name} is incompatible with the specified Pmin"
                        )
                        raise Exception

            elif parameter == "demand":
                if self.chargeable or self.refundable:
                    logging.critical(
                        f"Error: cannot set the power of {self.name} "
                        f"as determined, because it is set as chargeable or refundable!"
                    )
                    raise Exception

                self.determined = True
                self.demand = iv.validate(
                    parameters["demand"], "float", timesteps=timesteps
                )

                # determined overrides Pmin and power_max...warn the user if he tries to use both
                if self.power_max_limited or self.power_min_limited:
                    logging.warning(
                        f"Setting the Power of {self.name} "
                        f"as determined overrides the already given Pmin/power_max constraints!"
                    )

                # check, if determined power interferes with existing power_max constraint
                if self.power_max_limited:
                    if (
                        sum(self.demand / self.factory.timefactor <= self.power_max)
                        < timesteps
                    ):
                        logging.critical(
                            f"ERROR: given timeseries Power is incompatible with "
                            f"existing constraint power_max for Component {self.name}"
                        )
                        raise Exception

                # check, if determined power interferes with existing Pmin constraint
                if self.power_min_limited:
                    if (
                        sum(self.demand / self.factory.timefactor >= self.power_min)
                        < timesteps
                    ):
                        logging.critical(
                            f"ERROR: given timeseries Power is incompatible "
                            f"with existing constraint Pmin for Component {self.name}"
                        )
                        raise Exception

            # handle given price/revenue timeseries
            elif parameter == "cost":
                if self.determined:
                    logging.critical(
                        f"Error: cannot usefully set a cost for{self.name}, "
                        f"because the output power is determined"
                    )
                    raise Exception

                if self.refundable:
                    logging.critical(
                        f"ERROR: {self.name} cannot set to be chargeable, "
                        f"because it is already defined to create revenue!"
                    )
                    raise Exception

                self.chargeable = True
                self.cost = iv.validate(
                    parameters["cost"], "float", timesteps=timesteps
                )

            elif parameter == "max_total_input":
                self.max_total_input_limited = True
                self.max_total_input = iv.validate(
                    parameters["max_total_input"], "float"
                )

            elif parameter == "revenue":
                if self.determined:
                    logging.info(
                        f"Warning: Revenue set for {self.name}, "
                        f"even though the output power is determined"
                    )

                if self.chargeable:
                    logging.critical(
                        f"ERROR: {self.name} cannot be set to create revenue, "
                        f"because it is already defined as chargeable!"
                    )
                    raise Exception

                self.refundable = True
                self.revenue = iv.validate(
                    parameters["revenue"], "float", timesteps=timesteps
                )

            elif parameter == "co2_emissions_per_unit":
                # set the emission factor as timeseries:
                self.co2_emissions_per_unit = iv.validate(
                    parameters["co2_emissions_per_unit"], "float", timesteps=timesteps
                )

                # set the sink to avoid emissions:
                self.causes_emissions = True

            # handle is_onsite definition
            elif parameter == "is_onsite":
                self.is_onsite = iv.validate(parameters["is_onsite"], "boolean")

            # handle keys with no relevance for Simulation
            elif parameter in [
                "icon",
                "position_x",
                "position_y",
                "scenario_determined",
            ]:
                pass

            # HANDLE GENERAL PARAMETERS
            else:
                if not super().set_parameter(timesteps, parameter, parameters):
                    # in case the function failed to set the parameter it returns false
                    continue

            logging.debug(f"        - {parameter} set for {self.type} {self.name}")

    def set_input(self, connection: co.Connection):
        """
        This function sets the given connection as the input for the triggerdemand-component.
        The parent class method is overridden because triggerdemands have to distinct between material and energy inputs.
        :param connection: [fm.Connecntion-object]
        """
        # check, that there is no more than one energy and material input each
        if connection.type == "losses":
            self.inputs.append(connection)
        else:
            super().set_input(connection)


class Source(Component):
    def __init__(self, key: str, factory, *, flowtype: str = None, name: str = None):
        super().__init__(key, factory, flowtype=flowtype, name=name)
        self.availability = np.ones(
            factory.timesteps
        )  # used for all classes with power_max, to determine the maximum power timedependent. is initialized as all ones, so that it has no effect if not specificly adressed
        self.causes_emissions = False  # Does the usage of the source create internal or external CO2-Emissions?
        self.chargeable = False  # Must be changed to "true", if the utilization of the source is connected with costs
        self.cost = np.zeros(
            factory.timesteps
        )  # must be specified by set_configuration
        self.capacity_charge = 0  # Set a fixed capacity charge (Leistungspreis) that is being charged once per year.
        self.co2_emissions_per_unit = 0  # specifies, how much CO² is emitted for every unit consumed from the source
        self.description = (
            "Unspecified Source"  # Description for better identification in UI
        )
        self.determined = (
            False  # specify if the output power is predetermined by a timeseries
        )
        self.determined_power = []  # must be specified by set_configuration
        self.flowtype_description = ""
        self.is_onsite = False  # determines wether the input is generated within the factory or comes from outside. This is used to calculate the self sufficiency in the end
        self.power_max_limited = False  # specify if maximum output is limited
        self.power_max = []  # must be specified by set_configuration
        self.power_min_limited = False  # specify if the minimum output power is limited
        self.power_min = []  # must be specified by set_configuration
        self.refundable = False  # Just a dummy to shorten the code at later points
        self.type = "source"  # specify component as global source

        logging.debug(
            f"        - New source {self.name} created with Component-key {self.key}"
        )

    def set_configuration(self, timesteps: int, parameters: dict) -> bool:
        """
        This function sets the configuration for the component. All parameters to be defined can be handed over as key-value-pairs within a single dictionary.
        :param timesteps: [int] The number of timesteps that stationary values are scaled to and user given timeseries need to have at minimum
        :param parameters: [dict] dictionary with key-value-combinations that specify all the parameters to be configured.
        :return: [boolean] True, if the configuration war successfull
        """
        # iterate over all given parameters and figure out how to handle them...
        for parameter in parameters:
            # handle power_max/power_min/determined_power constraints
            if parameter == "power_max":
                self.power_max_limited = True
                self.power_max = iv.validate(
                    parameters["power_max"], "float", timesteps=timesteps
                )
                # check, if Pmin and power_max constraints are compatible
                if self.power_min_limited:
                    if any(self.power_min > self.power_max * self.availability):
                        logging.critical(
                            f"ERROR: given timeseries Pmin and power_max for Component {self.name} are not compatible"
                        )
                        raise Exception
                # check, if power_max constraints is compatible with determined power
                if self.determined:
                    if sum(self.determined_power <= self.power_max) < timesteps:
                        logging.critical(
                            f"ERROR: Already determined Power is incompatible with the power_max you're trying to set for Component {self.name}"
                        )
                        raise Exception
                # check, if power_max constraint is compatible with availability and Pmin
                if self.power_min_limited:
                    if any(self.power_max * self.availability < self.power_min):
                        logging.critical(
                            f"The given combination of power_max and availability for the source {self.name} is incompatible with the specified Pmin"
                        )
                        raise Exception
            elif parameter == "power_min":
                self.power_min_limited = True
                self.power_min = iv.validate(
                    parameters["power_min"], "float", timesteps=timesteps
                )
                # check, if Pmin and power_max constraints are compatible
                if self.power_max_limited:
                    if any(self.power_min > self.power_max * self.availability):
                        logging.critical(
                            f"ERROR: given timeseries Pmin and power_max for Component {self.name} are not compatible"
                        )
                        raise Exception
                # check, if Pmin constraints is compatible with determined power
                if self.determined:
                    if sum(self.determined_power >= self.power_min) < timesteps:
                        logging.critical(
                            f"ERROR: Already determined Power is incompatible with the Pmin you're trying to set for Component {self.name}"
                        )
                        raise Exception
                # check, if Pmin constraint is compatible with availability and power_max
                if self.type == "source" and self.power_max_limited:
                    if (min(self.power_max * self.availability) < self.power_min).any():
                        logging.critical(
                            f"The given combination of power_max and availability for the source {self.name} is incompatible with the specified Pmin"
                        )
                        raise Exception
            elif parameter == "determined_power":
                if self.chargeable or self.refundable:
                    logging.critical(
                        f"Error: cannot set the power of {self.name} as determined, because it is set as chargeable or refundable!"
                    )
                    raise Exception

                self.determined = True
                self.determined_power = iv.validate(
                    parameters["determined_power"], "float", timesteps=timesteps
                )

                # determined overrides Pmin and power_max...warn the user if he tries to use both
                if self.power_max_limited or self.power_min_limited:
                    logging.warning(
                        f"Setting the Power of {self.name} as determined overrides the already given Pmin/power_max constraints!"
                    )

                # check, if determined power interferes with existing power_max constraint
                if self.power_max_limited:
                    if (
                        sum(
                            self.determined_power / self.factory.timefactor
                            <= self.power_max
                        )
                        < timesteps
                    ):
                        logging.critical(
                            f"ERROR: given timeseries Power is incompatible with existing constraint power_max for Component {self.name}"
                        )
                        raise Exception
                # check, if determined power interferes with existing Pmin constraint
                if self.power_min_limited:
                    if (
                        sum(
                            self.determined_power / self.factory.timefactor
                            >= self.power_min
                        )
                        < timesteps
                    ):
                        logging.critical(
                            f"ERROR: given timeseries Power is incompatible with existing constraint Pmin for Component {self.name}"
                        )
                        raise Exception

            # handle given price/revenue timeseries
            elif parameter == "cost":
                if self.determined:
                    logging.critical(
                        f"ERROR: cannot usefully set a cost for{self.name}, because the output power is determined"
                    )
                    raise Exception

                if self.refundable:
                    logging.critical(
                        f"ERROR: {self.name} cannot set to be chargeable, because it is already defined to create revenue!"
                    )
                    raise Exception

                self.chargeable = True
                self.cost = iv.validate(
                    parameters["cost"], "float", timesteps=timesteps
                )

            elif parameter == "capacity_charge":
                self.capacity_charge = iv.validate(
                    parameters["capacity_charge"], "float"
                )

            # handle is_onsite definition
            elif parameter == "is_onsite":
                self.is_onsite = iv.validate(parameters["is_onsite"], "boolean")

            elif parameter == "co2_emissions_per_unit":
                # set the emission factors as a timeseries
                self.co2_emissions_per_unit = iv.validate(
                    parameters["co2_emissions_per_unit"], "float", timesteps=timesteps
                )
                # define the source to cause emissions:
                self.causes_emissions = True

            # HANDLE GENERAL PARAMETERS
            else:
                if not super().set_parameter(timesteps, parameter, parameters):
                    # in case the function failed to set the parameter it returns false
                    continue

            logging.debug(f"        - {parameter} set for {self.type} {self.name}")


class Storage(Component):
    def __init__(self, key: str, factory, *, flowtype: str = None, name: str = None):
        super().__init__(key, factory, flowtype=flowtype, name=name)
        self.capacity = 0  # Storage capacity, initialized as zero, so that the component has no effect if not explicitly specified
        self.capacity_charge = 0  # yearly capital costs for storage capacity provision
        self.direct_throughput = False  # Set to true if charging and discharging in the same timestep is allowed
        self.efficiency = (
            1  # ratio of discharged vs charged power, initialized as 1 -> no losses
        )
        self.flowtype_description = ""  # Optional string shown as explanation in GUI
        self.leakage_time = 0  # fixed % of capacity that leaks per timestep
        self.leakage_SOC = 0  # % of the stored ressource that leaks per timestep
        self.power_max_charge = (
            0  # maximum charging / unloading speed, initialized as almost unlimited
        )
        self.power_max_discharge = (
            0  # maximum discharging / unloading speed, initialized as almost unlimited
        )
        self.soc_start = 0.5  # State of charge at the beginning of the Simulation, initialized as 50%; NO EFFECT IF soc_start_determined=False
        self.soc_start_determined = True  # Determines, wether the SOC at the start/end of the Simulation has to be the given value or wether it it up to the solver
        self.sustainable = True  # Determines, wether the SOC has to be the same at the start and end of the Simulation or not.
        self.to_losses = None  # placeholder for a pointer directing to the correct losses destination
        self.type = "storage"  # specify Component as storage

        logging.debug(
            f"        - New storage {self.name} created with Component-key{self.key}"
        )

    def set_configuration(self, timesteps: int, parameters: dict) -> bool:
        """
        This function sets the configuration for the component. All parameters to be defined can be handed over as key-value-pairs within a single dictionary.
        :param timesteps: [int] The number of timesteps that stationary values are scaled to and user given timeseries need to have at minimum
        :param parameters: [dict] dictionary with key-value-combinations that specify all the parameters to be configured.
        :return: [boolean] True, if the configuration war successfull
        """
        # iterate over all given parameters and figure out how to handle them...
        for parameter in parameters:
            # HANDLE STORAGE-SPECIFIC PARAMETERS
            if parameter == "capacity":
                self.capacity = iv.validate(
                    parameters["capacity"], "float", positive=True
                )
            elif parameter == "direct_throughput":
                self.direct_throughput = iv.validate(
                    parameters["direct_throughput"], "boolean"
                )
            elif parameter == "soc_start":
                self.soc_start = iv.validate(parameters["soc_start"], "0..1")
            elif parameter == "sustainable":
                self.sustainable = iv.validate(parameters["sustainable"], "boolean")
            elif parameter == "soc_start_determined":
                self.soc_start_determined = iv.validate(
                    parameters["soc_start_determined"], "boolean"
                )
            elif parameter == "power_max_charge":
                self.power_max_charge = iv.validate(
                    parameters["power_max_charge"], "float"
                )
            elif parameter == "power_max_discharge":
                self.power_max_discharge = iv.validate(
                    parameters["power_max_discharge"], "float"
                )

            # HANDLE GENERAL PARAMETERS
            else:
                if not super().set_parameter(timesteps, parameter, parameters):
                    # in case the function failed to set the parameter it returns false
                    continue

            logging.debug(f"        - {parameter} set for {self.type} {self.name}")

    def set_output(self, connection: co.Connection):
        """
        This function sets the given connection as an output for the storage. Overriding function is required because losses exist as an additional special output.
        :param connection: [fm.Connection-object]
        """

        # handle connections to losses if specified:
        if connection.type == "losses":
            self.to_losses = connection
        else:
            # call parent function to add connection
            super().set_output(connection)


class Thermalsystem(Component):
    def __init__(self, key: str, factory, name: str = None):
        super().__init__(key, factory, name=name)
        self.C = 10  # Storage inertia
        self.description = (
            "Unspecified Thermalsystem"  # Description for better identification in UI
        )
        self.flowtype = factory.flowtypes[
            "heat"
        ]  # flowtype of thermal pool must be heat
        self.from_gains = (
            []
        )  # placeholder for a pointer directing to the source of thermal gains from outside
        self.max_inputs = 10  # thermal systems may have multiple inputs
        self.max_outputs = 10  # thermal systems may have multiple outputs
        self.R = 10  # Thermal loss factor
        self.sustainable = True  # Does the thermal system have to retain to it's starting temperature at the end of the Simulation?
        self.temperature_ambient = (
            np.ones(factory.timesteps) * 293.15
        )  # set a standard value for the ambient temperature
        self.temperature_max = (
            np.ones(factory.timesteps) * 5000
        )  # set maximum temperature to 5000 degrees for every timestep-> should be equal to "infinite"
        self.temperature_min = np.zeros(
            factory.timesteps
        )  # set minimum temperature to zero degrees as a standard value
        self.temperature_start = None
        self.to_losses = (
            []
        )  # placeholder for a pointer directing to the correct losses destination
        self.type = "thermalsystem"  # specify Component as a thermal system
        logging.debug(
            f"        - New thermal system {self.name} created with Component-id {self.key}"
        )

    def update_flowtype(self, flowtype: str):
        pass  # break the recursive broadcast

    def set_input(self, connection: co.Connection):
        """
        This function sets the given connection as the input for the thermalsystem-component. Overriding function is required because gains exists as an additional special input.
        :param connection: [fm.Connection-object]
        """

        # handle connections from external gains:
        if connection.type == "gains":
            if not self.from_gains == []:
                logging.warning(
                    f"{self.name} already had a connection with attribute 'from_gains' (coming from {self.from_gains.origin.name}) which has been overwritten now!"
                )
            self.from_gains = connection

        # handle normal connections
        else:
            # call parent function to add connection
            super().set_input(connection)

    def set_output(self, connection: co.Connection):
        """
        This function sets the given connection as an output for the thermal system. Overriding function is required because losses exist as an additional special output.
        :param connection: [fm.Connection-object]
        """
        # prohibit direct connections between two thermalsystems:
        if connection.destination.type == "thermalsystem":
            logging.critical(
                f" Error during factory setup: Connecting two thermalsystems ({self.name} -> {connection.destination.name}) is not possible. Integrate at least one component between them!"
            )
            raise Exception

        # handle connections to losses if specified:
        if connection.type == "losses":
            self.to_losses = connection
        else:
            # call parent function to add connection
            super().set_output(connection)

    def set_configuration(self, timesteps: int, parameters: dict) -> bool:
        """
        This function sets the configuration for the component. All parameters to be defined can be handed over as key-value-pairs within a single dictionary.
        :param timesteps: [int] The number of timesteps that stationary values are scaled to and user given timeseries need to have at minimum
        :param parameters: [dict] dictionary with key-value-combinations that specify all the parameters to be configured.
        :return: [boolean] True, if the configuration war successfull
        """
        # iterate over all given parameters and figure out how to handle them...
        for parameter in parameters:
            # HANLDE THERMALSYSTEM-SPECIFIC PARAMETERS
            if parameter == "temperature_max":
                self.temperature_max = (
                    iv.validate(
                        parameters["temperature_max"], "float", timesteps=timesteps
                    )
                    + 273.15
                )  # correction term, because internal calculations are performed in Kelvin

            elif parameter == "temperature_min":
                self.temperature_min = (
                    iv.validate(
                        parameters["temperature_min"], "float", timesteps=timesteps
                    )
                    + 273.15
                )

            elif parameter == "temperature_ambient":
                self.temperature_ambient = (
                    iv.validate(
                        parameters["temperature_ambient"], "float", timesteps=timesteps
                    )
                    + 273.15
                )

            elif parameter == "sustainable":
                self.sustainable = iv.validate(parameters["sustainable"], "boolean")

            elif parameter == "temperature_start":
                self.temperature_start = (
                    iv.validate(parameters["temperature_start"], "float") + 273.15
                )

            # HANDLE GENERAL PARAMETERS
            else:
                if not super().set_parameter(timesteps, parameter, parameters):
                    # in case the function failed to set the parameter it returns false
                    continue
            logging.debug(f"        - {parameter} set for {self.type} {self.name}")

        # Validation of given inputs:
        if (self.temperature_min > self.temperature_max).any():
            logging.critical(
                f"ERROR during configuration of {self.name}: Given Tmax and Tmin are incompatible. Tmax is smaller than Tmin for at least one timestep!"
            )
            raise Exception

        if self.temperature_min[0] > self.temperature_start:
            logging.critical(
                f"ERROR during configuration of {self.name}: Tmin for t=0 is greater than Tstart. Tmin(t=0)={self.temperature_min[0]}, Tstart={self.temperature_start}"
            )
            raise Exception

        if self.temperature_max[0] < self.temperature_start:
            logging.critical(
                f"ERROR during configuration of {self.name}: Tmax for t=0 is smaller than Tstart. Tmax(t=0)={self.temperature_max[0]}, Tstart={self.temperature_start}"
            )
            raise Exception


class Triggerdemand(Component):
    def __init__(self, key: str, factory, name: str = None):
        super().__init__(key, factory, name=name)
        self.executions = (
            0  # total number of required executions, Initialized as 0 = no restrictions
        )
        self.input_energy = None  # energy input
        self.input_material = None  # material input
        self.load_profile_energy = (
            []
        )  # profiles of the energy load that has to be fulfilled on execution
        self.load_profile_material = (
            []
        )  # profiles of the energy load that has to be fulfilled on execution
        self.max_parallel = 0  # maximum number of parallel executions. Initialized as 0 = no restrictions
        self.max_inputs = 2  # triggerdemands are allowed to have each one material and one energy input
        self.max_outputs = 2  # triggerdemands are allowed to have each one material and one energy output
        self.output_energy = []  # output energy
        self.output_material = []  # output material
        self.profile_length = []  # length of the given load profile
        self.Tend = (
            factory.timesteps
        )  # last timestep of the allowed fullfillment interval. Initialized as the last timestep
        self.Tstart = 1  # first timestep of the allowed fulfilment interval. Initialized as the first timestep
        self.type = "triggerdemand"  # specify Component as a thermal system
        logging.debug(
            f"        - New triggerdemand {self.name} created with Component-key {self.key}"
        )

    def set_configuration(self, timesteps: int, parameters: dict):
        """
        This function sets the configuration for the component. All parameters to be defined can be handed over as key-value-pairs within a single dictionary.
        :param timesteps: [int] The number of timesteps that stationary values are scaled to and user given timeseries need to have at minimum
        :param parameters: [dict] dictionary with key-value-combinations that specify all the parameters to be configured.
        :return: [boolean] True, if the configuration war successfull
        """
        # iterate over all given parameters and figure out how to handle them...
        for parameter in parameters:
            # HANLDE TRIGGERDEMAND-SPECIFIC PARAMETERS
            if parameter == "load_profile_energy":
                self.load_profile_energy = parameters["load_profile_energy"]
                # set profile length for the Component + check compatibility with material profile
                if self.load_profile_material == []:
                    self.profile_length = len(self.load_profile_energy)
                elif not len(self.load_profile_energy) == self.profile_length:
                    logging.critical(
                        f"ERROR: Length of energy and material load profiles for triggerdemand {self.name} do not match! (Energy profile: {len(self.load_profile_energy)}; Material profile: {len(self.load_profile_material)} "
                    )
                    raise Exception

            elif parameter == "load_profile_material":
                self.load_profile_material = parameters["load_profile_material"]
                # set profile length for the Component + check compatibility with energyprofile
                if self.load_profile_energy == []:

                    self.profile_length = len(self.load_profile_material)
                elif not len(self.load_profile_energy) == self.profile_length:
                    logging.critical(
                        f"ERROR: Length of energy and material load profiles for triggerdemand {self.name} do not match! (Energy profile: {len(self.load_profile_energy)}; Material profile: {len(self.load_profile_material)}) "
                    )
                    raise Exception

            elif parameter == "Tstart":
                self.Tstart = iv.validate(parameters["Tstart"], "int")

            elif parameter == "Tend":
                self.Tend = iv.validate(parameters["Tend"], "int")

            elif parameter == "max_parallel":
                self.max_parallel = iv.validate(parameters["max_parallel"], "int")

            # HANDLE GENERAL PARAMETERS
            else:
                if not super().set_parameter(timesteps, parameter, parameters):
                    # in case the function failed to set the parameter it returns false
                    continue

            logging.debug(f"        - {parameter} set for {self.type} {self.name}")

    def set_input(self, connection: co.Connection):
        """
        This function sets the given connection as the input for the triggerdemand-component.
        The parent class method is overridden because triggerdemands have to distinct between material and energy inputs.
        :param connection: [fm.Connecntion-object]
        """

        # check, that there is no more than one energy and material input each
        if connection.flowtype.is_energy():
            if self.input_energy is not None:
                logging.critical(
                    f"ERROR: Cannot add {connection.name} to {self.name}, since triggerdemand-components are only allowed to have one energy input and {self.name} already has {self.input_energy.name} as input!"
                )
                raise Exception
            # if this was the first energy input -> confirm and save it
            self.input_energy = connection
        else:
            if self.input_material is not None:
                logging.critical(
                    f"ERROR: Cannot add {connection.name} to {self.name}, since triggerdemand-components are only allowed to have one material input and {self.name} already has {self.input_material.name} as input!"
                )
                raise Exception
            # if this was the first material input -> confirm and save it
            self.input_material = connection
        # fill the global input list of the Component as well
        self.inputs.append(
            connection
        )  # sets the connection-object "connection" as an input for self.

    def set_output(self, connection: co.Connection):
        """
        This function sets the given connection as an output for the component.
        The parent class method is overridden because triggerdemands have to distinct between material and energy outputs.
        :param connection: [fm.Connection-object]
        """
        # check, that there is no more than one energy and material output each
        if connection.flowtype.is_energy():
            if self.output_energy:
                logging.critical(
                    f"ERROR: Cannot add {connection.name} to {self.name}, since triggerdemand-components are only allowed to have one energy output and {self.name} already has {self.output_energy.name} as output!"
                )
                raise Exception
            # if this was the first energy output -> confirm and save it
            self.output_energy = connection
        else:
            if self.output_material:
                logging.critical(
                    f"ERROR: Cannot add {connection.name} to {self.name}, since triggerdemand-components are only allowed to have one material output and {self.name} already has {self.output_material.name} as output!"
                )
                raise Exception
            # if this was the first material output -> confirm and save it
            self.output_material = connection
        # fill the global output list of the Component as well
        self.outputs.append(connection)

    def update_flowtype(self, flowtype: str):
        # break the recursive broadcast # FLOWTYPE DETERMINATION
        # TODO: The flowdetermination does not have to stop here...theoretically it could be passed on individually for energy and material flows.
        pass


class Slack(Component):
    def __init__(self, key: str, factory, name: str = None):
        super().__init__(key, factory, name=name)
        self.type = "slack"  # identify Component as slack
        self.cost = (
            np.ones(factory.timesteps) * 1000000000
        )  # Cost of utilization is set to a big M -> 1.000.000€/Unit
        logging.debug(
            f"        - New Slack {self.name} created with Component-key {self.key}"
        )


class Schedule(Component):
    def __init__(self, key: str, factory, name: str = None):
        super().__init__(key, factory, name=name)
        self.demands = np.array(
            [[0, 0, 0, 0]]
        )  # Initialize Demand as a single partdemand with a volume of zero
        self.power_max_limited = (
            False  # define, if the maximum total power of all part demands is limited
        )
        self.power_max = 1000000000  # maximum total power of all part demands aggregated at one timestep
        self.type = "schedule"  # identify Component as slack

        logging.debug(
            f"        - New schedule Component {self.name} created with Component-id {self.key}"
        )

    def set_configuration(self, timesteps: int, parameters: dict) -> bool:
        """
        This function sets the configuration for the component. All parameters to be defined can be handed over as key-value-pairs within a single dictionary.
        :param timesteps: [int] The number of timesteps that stationary values are scaled to and user given timeseries need to have at minimum
        :param parameters: [dict] dictionary with key-value-combinations that specify all the parameters to be configured.
        :return: [boolean] True, if the configuration war successfull
        """
        # iterate over all given parameters and figure out how to handle them...
        for parameter in parameters:
            # HANDLE SCHEDULE-SPECIFIC PARAMETERS
            if parameter == "power_max" and hasattr(self, parameter):
                self.power_max_limited = True
                self.power_max = iv.validate(
                    parameters["power_max"], "float", timesteps=timesteps
                )

            elif parameter == "demands" and hasattr(self, parameter):
                # store the given demands in self.demands as numpy array
                self.demands = iv.validate(parameters["demands"], "np.ndarray")

                check = (self.demands[:, 0] - self.demands[:, 1]) > 0
                if check.any():
                    logging.critical(
                        f"ERROR in demand input data for {self.name}: Data contains demands with Tend ahead of Tstart."
                    )
                    raise Exception
                if not np.equal(np.mod(self.demands[:, 0:1], 1), 0).all():
                    logging.critical(
                        f"ERROR in demand input data for {self.name}: Time information needs to be integer!"
                    )
                    raise Exception
                if max(self.demands[:, 1]) > timesteps:
                    logging.critical(
                        f"ERROR in demand input data for {self.name}: Endpoint of at least one demand interval is after maximum Simulation length."
                    )
                    raise Exception
                if min(self.demands[:, 0]) <= 0:
                    logging.critical(
                        f"ERROR in demand input data for {self.name}: The earliest starting Point for demands is interval 1. Earlier starts are invalid."
                    )
                    raise Exception
                if any(
                    np.divide(self.demands[:, 2], self.demands[:, 3])
                    > self.demands[:, 1] - self.demands[:, 0]
                ):
                    logging.critical(
                        f"ERROR in demand input data for {self.name}: At least one demand is not fulfillable with its given volume and power_max and time combination."
                    )
                    raise Exception
                if len(self.demands[:, 1]) == 0:
                    logging.critical(
                        f"ERROR in demand input data for {self.name}: Diven demand list is empty"
                    )
                    raise Exception
                if len(self.demands[:, 1]) == 0:
                    logging.critical(
                        f"ERROR in demand input data for {self.name}: Diven demand list is empty"
                    )
                    raise Exception
                if min(self.demands[:, 2]) == 0:
                    logging.critical(
                        f"ERROR in demand input data for {self.name}: List contains demands with zero volume"
                    )
                    raise Exception

            # HANDLE GENERAL PARAMETERS
            else:
                if not super().set_parameter(timesteps, parameter, parameters):
                    # in case the function failed to set the parameter it returns false
                    continue

            logging.debug(f"        - {parameter} set for {self.type} {self.name}")
