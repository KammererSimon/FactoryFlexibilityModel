"""
.. _Factory:
This Package contains everything that is needed to specify the structure of a factory for the Simulation:
       -> "factory" is the main class and the only one meant to be called by the user.
              It collects all given Information and organizes the setup process
"""

# IMPORTS
import logging
import pickle
from pathlib import Path

import factory_flexibility_model.io.input_validations as iv
from factory_flexibility_model.factory import Components as factory_components
from factory_flexibility_model.factory import Connection as factory_connection
from factory_flexibility_model.factory import Flowtype as ft
from factory_flexibility_model.factory import Unit


# CODE START
class Factory:
    """
    This class defines the structure and configuration of a factory.

    Attributes:
        +--------------------+-----------------------------------------------------+
        | Attribute          | Description                                         |
        +====================+=====================================================+
        | name               | The name of the factory (default: "New Factory").   |
        +--------------------+-----------------------------------------------------+
        | timesteps          | The number of timesteps in the simulation           |
        |                    | (default: 168).                                     |
        +--------------------+-----------------------------------------------------+
        | description        | A description of the factory (default:              |
        |                    | "Unspecified Factory").                             |
        +--------------------+-----------------------------------------------------+
        | enable_slacks      | A flag to enable or disable slack handling in the   |
        |                    | simulation (default: False).                        |
        +--------------------+-----------------------------------------------------+
        | timefactor         | A float representing the time factor for the        |
        |                    | simulation (default: 1).                            |
        +--------------------+-----------------------------------------------------+
        | emission_limit     | The emission limit for the factory (default: None). |
        +--------------------+-----------------------------------------------------+
        | emission_cost      | The cost associated with emissions (default: None). |
        +--------------------+-----------------------------------------------------+
        | connections        | A dictionary of connections between components.     |
        +--------------------+-----------------------------------------------------+
        | components         | A dictionary of all components in the factory.      |
        +--------------------+-----------------------------------------------------+
        | flowtypes          | A dictionary of available flowtypes.                |
        +--------------------+-----------------------------------------------------+
        | units              | A dictionary of available units.                    |
        +--------------------+-----------------------------------------------------+
        | emission_accounting| A boolean flag that indicates if emission           |
        |                    | accounting is enabled (default: False).             |
        +--------------------+-----------------------------------------------------+
    """

    def __init__(
        self,
        *,
        currency: str = "€",
        description: str = "Unspecified Factory",
        emission_limit: float = None,
        emission_cost: float = None,
        enable_slacks: bool = False,
        name: str = "New Factory",
        timesteps: int = 168,
        timefactor: float = 1,
    ):

        # Initialize structure variables
        self.connections = {}
        self.components = {}
        self.flowtypes = {}
        self.units = {}

        # Initialize emission accounting variables
        self.emission_accounting = False  # is set to true during set_configuration() when any component gets an emission factor assigned
        self.emission_limit = emission_limit
        self.emission_cost = emission_cost

        # Initialize user configurable variables
        self.timesteps = timesteps
        self.name = iv.validate(name, "string")
        self.currency = currency
        self.description = iv.validate(description, "string")
        self.enable_slacks = iv.validate(enable_slacks, "boolean")
        self.timefactor = iv.validate(timefactor, "float")

        # create the set of standard flowtypes
        self.initialize_flowtypes()

        logging.debug("        - New factory created")

    def add_component(
        self, key: str, component_type: str, *, flowtype: str = None, name: str = None
    ):

        # make sure, that the key is still unused
        self.validate_key(key)

        # create new object of desired Component
        if component_type == "pool":
            # call pool constructor
            self.components[key] = factory_components.Pool(
                key, self, flowtype=flowtype, name=name
            )

        elif component_type == "sink":
            # call destination constructor
            self.components[key] = factory_components.Sink(
                key, self, flowtype=flowtype, name=name
            )

        elif component_type == "source":
            # call source constructor
            self.components[key] = factory_components.Source(
                key, self, flowtype=flowtype, name=name
            )

        elif component_type == "storage":
            # call storage constructor
            self.components[key] = factory_components.Storage(
                key, self, flowtype=flowtype, name=name
            )

            # auto generate a connection to losses: determine, whether storage refers to energy or material and connect it to the corresponding loss destination
            if self.components[key].flowtype.unit.is_energy():

                # create connection to losses_energy if flowtype is a type of energy
                self.add_connection(
                    key,
                    "losses_energy",
                    key=f"{key}_to_Elosses",
                    name=f"{key}_to_Elosses",
                    flowtype="energy_losses",
                    type="losses",
                )

            elif self.components[key].flowtype.unit.is_mass():

                # create a connection to losses_material if flowtype is a type of material
                self.add_connection(
                    key,
                    "losses_material",
                    key=f"{key}_to_Mlosses",
                    name=f"{key}_to_Mlosses",
                    flowtype="material_losses",
                    type="losses",
                )

            # raise an error if the flowtype of the storage is unspecified
            else:
                logging.critical(
                    f"Losses-connection for {key} could not be created because the flowtype isn't specified!"
                )
                raise Exception

        elif component_type == "converter":
            # call converter constructor
            self.components[key] = factory_components.Converter(key, self, name=name)

            # connect the new converter to losses_energy
            self.add_connection(
                key,
                "losses_energy",
                key=f"{key}_to_Elosses",
                name=f"{key}_to_Elosses",
                weight=0.01,
                type="losses",
            )  # auto generate a connection to losses

        elif component_type == "deadtime":
            # call deadtime constructor
            self.components[key] = factory_components.Deadtime(key, self, name=name)

        elif component_type == "thermalsystem":
            # call thermalsystem constructor
            self.components[key] = factory_components.Thermalsystem(
                key, self, name=name
            )

            # connect the new thermalsystem to losses_energy
            self.add_connection(
                key,
                "losses_energy",
                key=f"{key}_to_Elosses",
                name=f"{self.name}_to_Elosses",
                flowtype="energy_losses",
                type="losses",
            )

            # connect the new thermalsystem to ambient_gains
            self.add_connection(
                "ambient_gains",
                key,
                key=f"ambient_gains_to_{key}",
                type="gains",
            )

        elif component_type == "triggerdemand":
            # call triggerdemand constructor
            self.components[key] = factory_components.Triggerdemand(
                key, self, name=name
            )

        elif component_type == "slack":
            # call slack constructor
            self.components[key] = factory_components.Slack(key, self, name=name)

        elif component_type == "schedule":
            # call schedule constructor
            self.components[key] = factory_components.Schedule(key, self, name=name)
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
        key: str,
        *,
        type: str = "default",
        name: str = None,
        flowtype: str = None,
        weight: float = None,
        weight_destination: float = None,
        weight_origin: float = None,
    ):
        """
        This function ads a new connection between two components to the factory
        :param origin: name-string of the source Component
        :param destination: name-string of the destination
        :param to_losses: Set to true if the new connection is meant to deduct losses from its source
        :param flowtype: Name of a flowtype object that determines the flowtype transported n the connection
        :param name: String that is used as a name for the connection
        :param weight_destination: [float] Specifies the weighting factor of the connection at the destination
        :param weight_origin: [float] Specifies the weighting factor of the connection at the source
        :param weight: [float] Specifies the weighting factors of the connection both at the destination and source
        """

        # make sure, that the key is still unused
        self.validate_key(key)

        # check, if specified destination and source components exist
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
            key,
            type=type,
            flowtype=flowtype,
            weight=weight,
            weight_destination=weight_destination,
            weight_origin=weight_origin,
            name=name,
        )

        # set new connection as output for the source Component
        self.components[origin].set_output(new_connection)

        # set connection as input for the destination Component
        self.components[destination].set_input(new_connection)

        # insert the new connection into the connection_list of the factory
        self.connections[key] = new_connection

        # writelog
        logging.debug(
            f"        - New connection {new_connection.name} of flowtype {new_connection.flowtype.name} added between {self.components[origin].name} and {self.components[destination].name} with connection_key {key}"
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

        # make sure, that the key is still unused
        self.validate_key(key)

        # make sure, that "unit" contains an actual unit object
        if isinstance(unit, str):
            unit = self.units[unit]

        # create a new flowtype with specified parameters and store it in the factory.flows - dictionary
        self.flowtypes[key] = ft.Flowtype(
            key,
            unit=unit,
            represents_losses=to_losses,
            description=description,
            color=color,
            name=name,
        )

        logging.debug(f"        - New flowtype added: {self.flowtypes[key].name}")

    def add_flowtype_object(self, flowtype, *, overwrite: bool = False):
        """
        Adds a new flowtype object to the factory's collection of flowtype objects.
        Initially checks if a flowtype object with the same key already exists in the factory. If it does, depending on the value of the `overwrite` parameter, it either logs a warning and exits the method or overwrites the existing object.
        :param flowtype: flowtype-object
        :param overwrite: A boolean indicating whether to overwrite an existing flowtype object with the same key.
        Defaults to False, meaning flowtype objects will not be overwritten and a warning will be issued if a flowtype with the same key already exists.
        :return: None
        """

        # make sure, that the key is not used for anything else but a flowtype
        if (
            flowtype.key in self.components.keys()
            or flowtype.key in self.connections.keys()
            or flowtype.key in self.units.keys()
        ):
            raise AttributeError(
                f"Redundant key detected! '{flowtype.key}' is already assigned to an existing instance!"
            )

        # check, if the factory already has a flowtype of the given key
        if flowtype.key in self.flowtypes.keys():
            # if yes: check if overwriting is allowed
            if not overwrite:
                # warn the user if the given flowtype could not be used
                logging.warning(
                    f"The factory already contains a flowtype with key {flowtype.key}"
                )
            return
        else:
            # add flowtype to the list of the factory
            self.flowtypes[flowtype.key] = flowtype

    def add_unit(
        self,
        key: str,
        quantity_type: str = "energy",
        conversion_factor: float = 1,
        magnitudes=1,
        units_flow="kWh",
        units_flowrate="kW",
    ):
        """
        This function adds a unit specification to the factory by adding it to the self.units-dict as a unit.Unit-object under the given key.
        Handing over "energy", "mass" or "unit" will result in the initialization in the three base unittypes that are hardcoded within this package.

        :param key: [str] identifier for the new unit
        :param quantity_type: [str] "mass", "energy" or "unknown"
        :param conversion_factor: The factor that transforms one unit of the given quantity to one unit of the base quantity of the quantity type
        :param magnitudes: [float list] A list of magnitudes that different prefixes for the unit are resembling. f.E. [1, 10, 100, 1000]
        :param units_flow: [str list] A list of units-descriptors that correspond to the given magnitudes when considering a flow f.e. [g, kg, t]
        :param units_flowrate: [str list] A list of units-descriptors that correspond to the given magnitudes when considering a flowrate f.e. [g/h, kg/h, t/h]
        :return: [bool] True if successfull
        """

        # make sure, that the key is still unused
        self.validate_key(key)

        if key == "energy":
            self.units["energy"] = Unit.Unit(
                key="energy",
                quantity_type="energy",
                conversion_factor=1,
                magnitudes=[1, 1000, 1000000, 1000000000, 1000000000000],
                units_flow=["kWh", "MWh", "GWh", "TWh", "PWh"],
                units_flowrate=["kW", "MW", "GW", "TW", "PW"],
            )
        elif key == "mass":
            self.units["mass"] = Unit.Unit(
                key="mass",
                quantity_type="mass",
                conversion_factor=1,
                magnitudes=[1, 1000, 1000000, 1000000000, 1000000000000],
                units_flow=["kg", "t", "kt", "mt", "gt"],
                units_flowrate=["kg/h", "t/h", "kt/h", "mt/h", "gt/h"],
            )
        elif key == "unit":
            self.units["unit"] = Unit.Unit(
                key="unit",
                quantity_type="unknown",
                conversion_factor=1,
                magnitudes=[1, 1000, 1000000, 1000000000, 1000000000000],
                units_flow=["Units", "k Units", "m. Units", "bn. Units", "T. Units"],
                units_flowrate=[
                    "Units/h",
                    "k Units/h",
                    "m. Units/h",
                    "bn. Units/h",
                    "trillion Units/h",
                ],
            )
        else:
            self.units[key] = Unit.Unit(
                key=key,
                quantity_type=quantity_type,
                conversion_factor=conversion_factor,
                magnitudes=magnitudes,
                units_flow=units_flow,
                units_flowrate=units_flowrate,
            )

        logging.debug(f"        - New unit added: {key}")

    def add_unit_object(self, unit, key, *, overwrite: bool = False):
        """
        Adds a new unit object to the factory's collection of unit objects.

        Initially, it checks if the unit's key is already assigned to any component, connection, or flowtype. If it is, it raises an AttributeError. Then it checks if a unit with the same key exists in the factory's unit collection. Depending on the `overwrite` parameter, it either logs a warning and exits the method or adds the unit to the factory's unit collection.

        Parameters:
        unit: object
            The unit object to be added. This object must have a `key` attribute, which is used to identify it in the collection.

        overwrite: bool, optional
            A boolean indicating whether to overwrite an existing unit object with the same key.
            Defaults to False, meaning unit objects will not be overwritten and a warning will be logged if a unit with the same key already exists.

        Returns:
        None

        Raises:
        AttributeError
            If the unit object's key is already assigned to an existing component, connection, or flowtype.
        """

        # make sure, that the key is not used for anything else but a flowtype
        if (
            unit.key in self.components.keys()
            or unit.key in self.connections.keys()
            or unit.key in self.flowtypes.keys()
        ):
            raise AttributeError(
                f"Redundant key detected! '{unit.key}' is already assigned to an existing instance!"
            )

        # check, if the factory already has a flowtype of the given key
        if unit.key in self.units.keys():
            # if yes: check if overwriting is allowed
            if not overwrite:
                # warn the user if the given flowtype could not be used
                logging.warning(
                    f"The factory already contains a flowtype with key {unit.key}"
                )
            return
        else:
            # add flowtype to the list of the factory
            self.units[unit.key] = unit

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

        # call the set_configuration - method of the component
        self.components[component].set_configuration(self.timesteps, parameters)

        # enable emission accounting if any component gets an emission factor assigned
        if "co2_emissions_per_unit" in parameters.keys():
            self.emission_accounting = True

    def check_existence(self, key: str):
        """
        This function checks, if a Component with the specified key exists within the factory
        :param key: [string] name/key of a Component in the factory
        :return: [Boolean]
        """
        # check, if the name exists in self.component_s
        if key not in self.components.keys():
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

    def get_name(self, key):
        """
        This function takes a key of a component or connection and returns the corresponding component name.
        In case of an invalid key it returns None.

        :param key: [str] -> Key of a component or connection within the factory
        :return: [str]/[None] -> Component name or none
        """
        try:
            name = self.components[key].name
        except:
            try:
                name = self.connections[key].name
            except:
                name = None
        return name

    def get_key(self, name):
        """
        This method takes an asset name and returns the corresponding key that the component or connection can be adressed with
        """

        # search name in component dict
        for component in self.components.values():
            if component.name == name:
                return component.key

        # search name in connection dict
        for connection in self.connections.values():
            if connection.name == name:
                return connection.key
        return None

    def initialize_flowtypes(self):
        """
        This creates a basic set of the most important units and flowtypes that might be used in a typical Simulation setup:
        Units:
            - [key: "energy"]    Basic energy unit in kWh | kW
            - [key: "mass"]   Basic material unit in kg | kg/h
            - [key: "unit"] Basic quantity unit in units | units/h
        Flowtypes:
            - material_losses in ["mass"]
            - energy_losses in ["energy"]
            - heat in ["energy"]
            - unknown in ["unit"]
        """

        # initialize basic units
        self.add_unit("energy")
        self.add_unit("mass")
        self.add_unit("unit")

        # initialize basic flowtypes
        self.flowtypes["material_losses"] = ft.Flowtype(
            "material_losses",
            unit=self.units["mass"],
            color="#666666",
            represents_losses=True,
        )
        self.flowtypes["energy_losses"] = ft.Flowtype(
            "energy_losses",
            unit=self.units["energy"],
            color="#666666",
            represents_losses=True,
        )

        self.flowtypes["heat"] = ft.Flowtype(
            "heat",
            unit=self.units["energy"],
            color="#996666",
        )

        self.flowtypes["unknown"] = ft.Flowtype(
            "unknown",
            unit=self.units["unit"],
            color="#999999",
        )

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
                    if input_i.flowtype.unit.is_energy():
                        # if energy: add the weight of the incoming connection to the sum of energy input weights
                        weightsum_input_energy += input_i.weight_destination

                    elif input_i.flowtype.unit.is_mass():

                        # if material: add the weight of the incoming connection to the sum of material input weights
                        weightsum_input_material += input_i.weight_destination

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
                    if output_i.flowtype.unit.is_energy():
                        # if energy:
                        weightsum_output_energy += output_i.weight_origin

                    elif output_i.flowtype.unit.is_mass():
                        # if material: add the weight of the outgoing connection to the sum of material input weights
                        weightsum_output_material += output_i.weight_origin

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
                if component.delay > self.timesteps:
                    logging.critical(
                        f"ERROR: Delay of Component '{component.name}' is to large for the maximum Simulation length of the factory ({self.timesteps}!"
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

    def __slack_component(self, component_type: str, key: str):
        """
        This function creates a slack for the given Component if necessary and connects it to the corresponding in- and outputs
        :param component_type: converter, pool, etc...
        :param key: identifier of the Component to be slacked
        """

        # deadtimes, pools and thermalsystems get slacked in both directions
        if component_type in ["deadtime", "pool", "thermalsystem"]:

            # create new slack Component
            self.add_component(f"{key}_slack", "slack")

            # connect it to the input and output of the Component
            self.add_connection(
                f"{key}_slack",
                key,
                key=f"{key}_slack_neg",
                type="slack",
                flowtype=self.components[key].flowtype,
                weight=0.01,
            )
            self.add_connection(
                key,
                f"{key}_slack",
                key=f"{key}_slack_pos",
                type="slack",
                flowtype=self.components[key].flowtype,
                weight=0.01,
            )

        # sinks get slacked on the input side if they are not the losses destination
        elif component_type == "sink" and not (
            key == "losses_energy" or key == "losses_material"
        ):

            # create new slack Component
            self.add_component(f"{key}_slack", "slack")

            # connect it to the input of the destination
            self.add_connection(
                f"{key}_slack",
                key,
                key=f"{key}_slack_neg",
                type="slack",
                flowtype=self.components[key].flowtype,
                weight=0.01,
            )

        # sources get slacked on the output side:
        elif component_type == "source":
            # create new slack Component
            self.add_component(f"{key}_slack", "slack")

            # connect it to the input of the destination
            self.add_connection(
                key,
                f"{key}_slack",
                key=f"{key}_slack",
                type="slack",
                flowtype=self.components[key].flowtype,
                weight=0.01,
            )

    def validate_key(self, key):
        if (
            key in self.components.keys()
            or key in self.connections.keys()
            or key in self.flowtypes.keys()
            or key in self.units.keys()
        ):
            raise AttributeError(
                f"Redundant key detected! '{key}' is already assigned to an existing instance!"
            )
        return True
