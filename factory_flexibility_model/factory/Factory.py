# FACTORY MODEL
# This Package contains everything that is needed to specify the structure of a factory for the simulation:
#        -> "factory" is the main class and the only one meant to be called by the user.
#               It collects all given Information and organizes the setup process


# IMPORTS
import logging
import pickle
from pathlib import Path

import factory_flexibility_model.input_validations as iv
from factory_flexibility_model.factory import Components as factory_components
from factory_flexibility_model.factory import Connection as factory_connection
from factory_flexibility_model.factory import Flowtype as ft
from factory_flexibility_model.factory import Unit


# CODE START
class Factory:
    def __init__(
        self,
        *,
        name: str = "New Factory",
        max_timesteps: int = 8760,
        description: str = "Unspecified Factory",
        enable_slacks: bool = False,
        timefactor: float = 1,
    ):

        # Initialize structure variables
        self.connections = {}
        self.components = {}
        self.component_keys = []
        self.flowtypes = {}
        self.flowtype_keys = []
        self.next_ids = {
            "connection": 0,
            "Component": 0,
        }  # Internal counter. Everytime a Component or connection is added it gets the next value and the counter is incremented
        self.units = {}
        self.version = 20221201

        # Initialize user configurable variables
        self.max_timesteps = iv.validate(max_timesteps, "int")
        self.name = iv.validate(name, "string")
        self.description = iv.validate(description, "string")
        self.enable_slacks = iv.validate(enable_slacks, "boolean")
        self.timefactor = iv.validate(timefactor, "float")

        # create the set of standard flowtypes
        self.initialize_flowtypes()

        logging.debug("        - New factory created")

    def add_component(self, key: str, component_type: str, *, flowtype: str = None):
        # validate the given inputs as strings
        key = iv.validate(key, "str")
        component_type = iv.validate(component_type, "str")

        # make sure that the specified name is not already taken by a Component or flowtype
        if key in self.component_keys or key in self.flowtype_keys:
            logging.critical(
                f"Cannot create Component {key} because the namekey is already assigned"
            )
            raise Exception

        # Add name of the new Component to the namelist
        self.component_keys.append(key)

        # create new object of desired Component
        if component_type == "pool":
            # call pool constructor
            self.components[key] = factory_components.Pool(key, self, flowtype=flowtype)

        elif component_type == "sink":
            # call sink constructor
            self.components[key] = factory_components.Sink(key, self, flowtype=flowtype)

        elif component_type == "source":
            # call source constructor
            self.components[key] = factory_components.Source(
                key, self, flowtype=flowtype
            )

        elif component_type == "storage":
            # call storage constructor
            self.components[key] = factory_components.Storage(
                key, self, flowtype=flowtype
            )

            # auto generate a connection to losses: determine, whether storage refers to energy or material and connect it to the corresponding loss sink
            if self.components[key].flowtype.is_energy():

                # create connection to losses_energy if flowtype is a type of energy
                self.add_connection(
                    key,
                    "losses_energy",
                    name=f"{key}_to_Elosses",
                    flowtype="energy_losses",
                    weight=0.01,
                    to_losses=True,
                )

            elif self.components[key].flowtype.is_material():

                # create a connection to losses_material if flowtype is a type of material
                self.add_connection(
                    key,
                    "losses_material",
                    name=f"{key}_to_Mlosses",
                    flowtype="material_losses",
                    weight=0.01,
                    to_losses=True,
                )

            # raise an error if the flowtype of the storage is unspecified
            else:
                logging.critical(
                    f"Losses-connection for {key} could not be created because the flowtype isn't specified!"
                )
                raise Exception

        elif component_type == "converter":
            # call converter constructor
            self.components[key] = factory_components.Converter(key, self)

            # connect the new converter to losses_energy
            self.add_connection(
                key,
                "losses_energy",
                name=f"{key}_to_Elosses",
                weight=0.01,
                to_losses=True,
            )  # auto generate a connection to losses

        elif component_type == "deadtime":
            # call deadtime constructor
            self.components[key] = factory_components.Deadtime(key, self)

        elif component_type == "thermalsystem":
            # call thermalsystem constructor
            self.components[key] = factory_components.Thermalsystem(
                key, self, flowtype=flowtype
            )

            # connect the new thermalsystem to losses_energy
            self.add_connection(
                key,
                "losses_energy",
                name=f"{key}_to_Elosses",
                flowtype="energy_losses",
                weight=0.01,
                to_losses=True,
            )

            # connect the new thermalsystem to ambient_gains
            self.add_connection(
                "ambient_gains",
                key,
                name=f"ambient_gains_to_{key}",
                weight=0.01,
                from_gains=True,
            )

        elif component_type == "triggerdemand":
            # call triggerdemand constructor
            self.components[key] = factory_components.Triggerdemand(key, self)

        elif component_type == "slack":
            # call slack constructor
            self.components[key] = factory_components.Slack(
                key, self, flowtype=flowtype
            )

        elif component_type == "schedule":
            # call schedule constructor
            self.components[key] = factory_components.Schedule(
                key, self, flowtype=flowtype
            )
        else:
            # if we end here the given type must have been invalid! -> Throw an error
            logging.critical(
                f"Cannot create new Component: {component_type} is an invalid type"
            )
            raise Exception

        # are slacks required?
        if self.enable_slacks:
            # create a slack for the new Component
            self.__slack_component(component_type, key)

    def add_connection(
        self,
        origin: factory_components.Component,
        destination: factory_components.Component,
        *,
        to_losses: bool = False,
        name: str = None,
        flowtype: str = None,
        weight: float = None,
        weight_sink: float = None,
        weight_source: float = None,
    ):
        """
        This function ads a new connection between two components to the factory
        :param origin: name-string of the source Component
        :param destination: name-string of the sink
        :param to_losses: Set to true if the new connection is meant to deduct losses from its source
        :param flowtype: Name of a flowtype object that determines the flowtype transported n the connection
        :param name: String that is used as a name for the connection
        :param weight_sink: [float] Specifies the weighting factor of the connection at the sink
        :param weight_source: [float] Specifies the weighting factor of the connection at the source
        :param weight: [float] Specifies the weighting factors of the connection both at the sink and source
        """
        # check, if specified sink and source components exist
        self.check_existence(origin)
        self.check_existence(destination)

        # if a flowtype is specified...
        if flowtype is not None:
            # ...make sure, that flowtype refers to the actual flowtype and does not only contain the string key
            flowtype = self.__get_flowtype_object(flowtype)

        # create new connection as object
        new_connection = factory_connection.Connection(
            self.components[origin],
            self.components[destination],
            self.next_ids["connection"],
            to_losses=to_losses,
            flowtype=flowtype,
            weight=weight,
            weight_sink=weight_sink,
            weight_source=weight_source,
            name=name,
        )

        # set new connection as output for the source Component
        self.components[origin].set_output(new_connection)

        # set connection as input for the sink Component
        self.components[destination].set_input(new_connection)

        # insert the new connection into the connection_list of the factory
        self.connections[self.next_ids["connection"]] = new_connection

        # increment the connection-id counter of the factory
        self.next_ids["connection"] += 1

        # writelog
        logging.debug(
            f"        - New connection {new_connection.name} of flowtype {new_connection.flowtype.name} added between {self.components[origin].name} and {self.components[destination].name} with connection_id {self.next_ids['connection']}"
        )

    def save(self, file_path: str, *, overwrite: bool = False):
        """
        This function saves a factory-object under the specified filepath as a single file.
        :param file_path: Path to the file to be created
        :param overwrite: Set True to allow the method to overwrite existing files.
        Otherwise an error will occur when trying to overwrite a file
        :return: True/False depending on the success of saving
        """

        # check, if file already exists
        file = Path(file_path)
        if file.is_file():
            if overwrite:
                logging.warning(
                    f"WARNING: The specified file already exists and will be overwritten"
                )
            else:
                logging.critical(
                    f"ERROR: The specified file already exists! Saving Factory aborted!"
                )
                raise Exception

        # save the factory at the given path
        with open(file_path, "wb") as f:
            pickle.dump(self, f)

        logging.info(f"FACTORY SAVED under {file_path}")

        return True

    def set_configuration(self, component: str, parameters: dict):
        """
        This function takes a string-identifier of a Component in a factory and a dict of configuration parameters.
        It hands the configuration parameters over to the set_configuration method of the Component.
        :param component: string-identifier of a Component in the factory
        :param parameters: dict with name-value-combinations for configuring the Component
        """
        # make sure that the specified Component exists
        self.check_existence(component)

        # call the set_configuration - methodof the factory
        self.components[component].set_configuration(self.max_timesteps, parameters)

    def check_existence(self, key: str):
        """
        This function checks, if a Component with the specified key exists within the factory
        :param key: [string] name/key of a Component in the factory
        :return: [Boolean]
        """
        # check, if the name exists in self.component_keys
        if key not in self.component_keys:
            logging.critical(f"Component {key} does not exist")
            raise Exception

    def create_essentials(self):
        # create standard assets
        self.add_component(
            "losses_energy", "sink", flowtype=self.flowtypes["energy_losses"]
        )
        self.add_component(
            "losses_material", "sink", flowtype=self.flowtypes["material_losses"]
        )
        self.add_component("ambient_gains", "source", flowtype=self.flowtypes["heat"])
        self.set_configuration(
            "ambient_gains", parameters={"is_onsite": True, "cost": 0.0001}
        )  # Ambient gain gets a tiny cost related to it to avoid a direct feed of energy from ambient gains to thermal losses!

    def initialize_flowtypes(self):
        """
        This creates a basic set of the most important units and flowtypes that might be used in a typical simulation setup:
        Units:
            - [key: "kW"]    Basic energy unit in kWh | kW
            - [key: "kg"]   Basic material unit in kg | kg/h
            - [key: "unit"] Basic quantity unit in units | units/h
        Flowtypes:
            - Heat in ["kW"]
            - material_losses in ["kg"]
            - energy_losses in ["kW"]
            - unknown in ["unit"]
        """

        # initialize basic units
        self.units["kW"] = Unit.Unit(key="kW")
        self.units["kg"] = Unit.Unit(key="kg")
        self.units["units"] = Unit.Unit(key="units")

        # initialize basic flowtypes
        self.flowtypes["heat"] = ft.Flowtype(
            "heat", color="#41719C", unit=self.units["kW"]
        )

        self.flowtypes["material_losses"] = ft.Flowtype(
            "material_losses",
            unit=self.units["kg"],
            color="#444444",
            suffix="",
            represents_losses=True,
        )
        self.flowtypes["energy_losses"] = ft.Flowtype(
            "energy_losses",
            unit=self.units["kW"],
            color="#444444",
            suffix="",
            represents_losses=True,
        )

        self.flowtypes["unknown"] = ft.Flowtype(
            "unknown",
            suffix="",
            unit=self.units["units"],
            color="#999999",
        )

    def add_flowtype(
        self,
        key: str,
        *,
        unit: str | Unit.Unit = "unit",
        to_losses: bool = None,
        description: str = None,
        color: str | list[float] = None,
        name: str = None,
    ):
        """
        This function creates a new flowtype-object and adds it to the factory
        :param name: [String] name identifier for the new flowtype (string)
        :param to_losses: [Boolean] Specifies if the connection is deducting losses
        :param description: [String] Description of the flow, just for GUI and labeling purposes
        :param color: [String; #XXXXXX] Color code for displaying the flow in GUI and Figures
        """

        # make sure, that the name is still unused
        if key in self.component_keys or key in self.flowtype_keys:
            # if not: throw an error
            logging.critical(
                f"Cannot create Flowtype {key} because the key is already assigned"
            )
            raise Exception

        # create a new flowtype with specified parameters and store it in the factory.flows - dictionary
        self.flowtypes[key] = ft.Flowtype(
            key,
            unit=unit,
            represents_losses=to_losses,
            description=description,
            color=color,
            name=name,
        )

        # add the new flowtype to the list of flowtype-keys
        self.flowtype_keys.append(key)

        logging.debug(f"        - New flowtype added: {self.flowtypes[key].name}")

    def check_validity(self):
        """
        this function does a variety of checks to make sure that the factory is consistent in itself and doesn't
        allow for any glitches or bugs unfortunately this is necessary, because some interactions between components
        can only be checked after everything has been set up
        :return: True/False
        """

        logging.info(f"Validating factory architecture...")
        # iterate over all components
        for component in self.components.values():

            # conducted validations depend on the Component type...
            if component.type == "converter":
                # if Component is a converter: ratio of inputs and outputs at converters must be valid

                # I) calculate sums of input weights
                # initialize summing variables
                weightsum_input_energy = 0
                weightsum_input_material = 0

                # iterate over all input connections
                for input_i in component.inputs:

                    # check if the input refers to energy or material
                    if input_i.flowtype.unit.quantity_type == "energy":
                        # if energy: add the weight of the incoming connection to the sum of energy input weights
                        weightsum_input_energy += input_i.weight_sink

                    elif input_i.flowtype.unit.quantity_type == "material":

                        # if material: add the weight of the incoming connection to the sum of material input weights
                        weightsum_input_material += input_i.weight_sink

                    else:
                        # otherwise the type of the flowtype remained unspecified during factory setup und therefore is invalid
                        logging.critical(
                            f"Flowtype of connection {input_i.name} is still unknown! The flowtype needs to be specified in order to correctly bilance it at {component.name}"
                        )
                        raise Exception

                # II) calculate sum of output weights
                # initialize summing variables
                weightsum_output_energy = 0
                weightsum_output_material = 0

                # iterate over all output connections
                for output_i in component.outputs:

                    # if energy: add the weight of the outgoing connection to the sum of energy input weights
                    if output_i.flowtype.unit.quantity_type == "energy":

                        # if energy:
                        weightsum_output_energy += output_i.weight_source
                    elif output_i.flowtype.unit.quantity_type == "material":

                        # if material: add the weight of the outgoing connection to the sum of material input weights
                        weightsum_output_material += output_i.weight_source

                    else:
                        # otherwise the type of the flowtype remained unspecified during factory setup und therefore is invalid
                        logging.critical(
                            f"Flowtype of connection {output_i.name} is still unknown! The flowtype needs to be specified in order to correctly bilance it at {component.name}"
                        )
                        raise Exception

                # check, if there are any inputs
                if weightsum_input_energy == 0 and weightsum_input_material == 0:
                    logging.critical(
                        f"ERROR: converter {component.name} does not have any inputs connected!"
                    )
                    raise Exception

                # if there is energy involved: calculate the base energy efficiency (used for visualisations later)
                if weightsum_input_energy > 0:
                    component.eta_base = (
                        weightsum_output_energy / weightsum_input_energy
                    )
                    return False

                # check, if the combination of input and output weight sums is valid
                if weightsum_output_energy > weightsum_input_energy:
                    logging.critical(
                        f"Error in the factory architecture: The sum of weights at the energy output of converter '{component.name}' ({weightsum_output_energy}) is greater that the sum of input weights {weightsum_input_energy}!"
                    )
                    raise Exception

                if weightsum_output_material > weightsum_input_material:
                    logging.critical(
                        f"Error in the factory architecture: The sum of weights at the material output of converter '{component.name}' ({weightsum_output_material}) is greater that the sum of input weights {weightsum_input_material}!"
                    )
                    raise Exception

            elif component.type == "deadtime":
                # if Component is a deadtime: make sure that there is at least one input
                if len(component.inputs) == 0:
                    logging.critical(
                        f"ERROR: Deadtime-Component '{component.name}' does not have an input!"
                    )
                    raise Exception

                # makesure that there is at least one output
                if len(component.outputs) == 0:
                    logging.critical(
                        f"ERROR: Deadtime-Component '{component.name}' does not have an output!"
                    )
                    raise Exception

                # make sure, that the delay is realizable within the length of allowed simulations
                if component.delay > self.max_timesteps:
                    logging.critical(
                        f"ERROR: Delay of Component '{component.name}' is to large for the maximum simulation length of the factory ({self.max_timesteps}!"
                    )
                    raise Exception

            elif component.type == "triggerdemand":
                # check, that the combinations of input and outputs connected is valid
                if not (component.input_energy or component.output_energy):
                    logging.critical(
                        f"Triggerdemand {component.name} has no inputs connected!"
                    )
                    raise Exception
                if component.input_energy and not component.output_energy:
                    logging.critical(
                        f"Triggerdemand {component.name} has an energy input but no energy output!"
                    )
                    raise Exception
                if component.output_energy and not component.input_energy:
                    logging.critical(
                        f"Triggerdemand {component.name} has an energy output but no energy input!"
                    )
                    raise Exception
                if component.input_material and not component.output_material:
                    logging.critical(
                        f"Triggerdemand {component.name} has a material input but no material output!"
                    )
                    raise Exception
                if component.output_material and not component.input_material:
                    logging.critical(
                        f"Triggerdemand {component.name} has a material output but no material input!"
                    )
                    raise Exception

        logging.info(f"Factory architecture validation successful")
        return True

    def __get_flowtype_object(self, flowtype_name: str):
        """
        This function takes the user input for "flowtype" and returns the corresponding flowtype-object from the factorys flowtype-list
        :param flow_name: name identifier (string) or flowtype object
        :return: flowtype object
        """

        # has the flowtype already been handed over as a flowtype-object? If yes: just return it
        if isinstance(flowtype_name, ft.Flowtype):
            return flowtype_name

        # if no: check if the flowtype-identifier has been handed over as a string
        if not isinstance(flowtype_name, str):
            logging.critical(
                "Flowtypes must be specified with their name identifiers (string) when creating components!"
            )
            raise Exception

        # check if the given flowtype actually exists
        if flowtype_name not in self.flowtypes:
            logging.critical(
                f"The specified flowtype {flowtype_name} does not exist in the flowtype list of the current factory. Add it first via .add_flow(). "
                f"\n Existing flowtypes at this point are: {[i for i in self.flowtypes]}"
            )
            raise Exception

        # converters must not have a flowtype specified. Throw an error if this is what's happening...
        if type == "converter":
            logging.critical(
                f"Error while creating Converter {self.name}: Converters must not have a flowtype assigned!"
            )
            raise Exception

        # all checks passed? -> return the pointer to the actual flowtype object
        return self.flowtypes[flowtype_name]

    def __slack_component(self, component_type: str, name: str):
        """
        This function creates a slack for the given Component if necessary and connects it to the corresponding in- and outputs
        :param component_type: converter, pool, etc...
        :param name: identifier of the Component to be slacked
        """

        # deadtimes, pools and thermalsystems get slacked in both directions
        if component_type in ["deadtime", "pool", "thermalsystem"]:

            # create new slack Component
            self.add_component(f"{name}_slack", "slack")

            # connect it to the input and output of the Component
            self.add_connection(
                f"{name}_slack",
                name,
                name=f"{name}_slack_neg",
                flowtype=self.components[name].flowtype,
                weight=0.01,
            )
            self.add_connection(
                name,
                f"{name}_slack",
                name=f"{name}_slack_pos",
                flowtype=self.components[name].flowtype,
                weight=0.01,
            )

        # sinks get slacked on the input side if they are not the losses sink
        elif component_type == "sink" and not (
            name == "losses_energy" or name == "losses_material"
        ):

            # create new slack Component
            self.add_component(f"{name}_slack", "slack")

            # connect it to the input of the sink
            self.add_connection(
                f"{name}_slack",
                name,
                name=f"{name}_slack_neg",
                flowtype=self.components[name].flowtype,
                weight=0.01,
            )
