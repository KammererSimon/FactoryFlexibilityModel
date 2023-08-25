# FACTORY MODEL
# This Package contains everything that is needed to specify the structure of a factory for the simulation:
#        -> "factory" is the main class and the only one meant to be called by the user.
#               It collects all given Information and organizes the setup process


import logging
import pickle
from pathlib import Path

# IMPORT 3RD PARTY PACKAGES
import numpy as np
import plotly.graph_objects as go

# IMPORT ENDOGENOUS COMPONENTS
import factory_flexibility_model.input_validations as iv
from factory_flexibility_model.factory import components as factory_components
from factory_flexibility_model.factory import connection as factory_connection
from factory_flexibility_model.factory import flowtype as ft


# CODE START
class factory:
    def __init__(
        self,
        *,
        name="New Factory",
        max_timesteps=8760,
        description="Unspecified Factory",
        enable_slacks=False,
        timefactor=1,
    ):
        # Initialize structure variables
        self.connections = {}
        self.components = {}
        self.component_names = []
        self.flowtypes = {}
        self.flowtype_names = []
        self.next_ids = {
            "connection": 0,
            "component": 0,
        }  # Internal counter. Everytime a component or connection is added it gets the next value and the counter is incremented
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

    def add_component(self, name, component_type, *, flowtype=None):
        # validate the given inputs as strings
        name = iv.validate(name, "str")
        component_type = iv.validate(component_type, "str")

        # make sure that the specified name is not already taken by a component or flowtype
        if name in self.component_names or name in self.flowtype_names:
            logging.critical(
                f"Cannot create Component {name} because the name is already assigned"
            )
            raise Exception

        # Add name of the new component to the namelist
        self.component_names.append(name)

        # create new object of desired component
        if component_type == "pool":
            # call pool constructor
            self.components[name] = factory_components.pool(
                name, self, flowtype=flowtype
            )

        elif component_type == "sink":
            # call sink constructor
            self.components[name] = factory_components.sink(
                name, self, flowtype=flowtype
            )

        elif component_type == "source":
            # call source constructor
            self.components[name] = factory_components.source(
                name, self, flowtype=flowtype
            )

        elif component_type == "storage":
            # call storage constructor
            self.components[name] = factory_components.storage(
                name, self, flowtype=flowtype
            )

            # auto generate a connection to losses: determine, whether storage refers to energy or material and connect it to the corresponding loss sink
            if self.components[name].flowtype.is_energy():

                # create connection to losses_energy if flowtype is a type of energy
                self.add_connection(
                    name,
                    "losses_energy",
                    name=f"{name}_to_Elosses",
                    flowtype="energy_losses",
                    weight=0.01,
                    to_losses=True,
                )

            elif self.components[name].flowtype.is_material():

                # create a connection to losses_material if flowtype is a type of material
                self.add_connection(
                    name,
                    "losses_material",
                    name=f"{name}_to_Mlosses",
                    flowtype="material_losses",
                    weight=0.01,
                    to_losses=True,
                )

            # raise an error if the flowtype of the storage is unspecified
            else:
                logging.critical(
                    f"Losses-connection for {name} could not be created because the flowtype isn't specified!"
                )
                raise Exception

        elif component_type == "converter":
            # call converter constructor
            self.components[name] = factory_components.converter(name, self)

            # connect the new converter to losses_energy
            self.add_connection(
                name,
                "losses_energy",
                name=f"{name}_to_Elosses",
                weight=0.01,
                to_losses=True,
            )  # auto generate a connection to losses

        elif component_type == "deadtime":
            # call deadtime constructor
            self.components[name] = factory_components.deadtime(name, self)

        elif component_type == "thermalsystem":
            # call thermalsystem constructor
            self.components[name] = factory_components.thermalsystem(
                name, self, flowtype=flowtype
            )

            # connect the new thermalsystem to losses_energy
            self.add_connection(
                name,
                "losses_energy",
                name=f"{name}_to_Elosses",
                flowtype="energy_losses",
                weight=0.01,
                to_losses=True,
            )

            # connect the new thermalsystem to ambient_gains
            self.add_connection(
                "ambient_gains",
                name,
                name=f"ambient_gains_to_{name}",
                weight=0.01,
                from_gains=True,
            )

        elif component_type == "triggerdemand":
            # call triggerdemand constructor
            self.components[name] = factory_components.triggerdemand(name, self)

        elif component_type == "slack":
            # call slack constructor
            self.components[name] = factory_components.slack(
                name, self, flowtype=flowtype
            )

        elif component_type == "schedule":
            # call schedule constructor
            self.components[name] = factory_components.schedule(
                name, self, flowtype=flowtype
            )
        else:
            # if we end here the given type must have been invalid! -> Throw an error
            logging.critical(
                f"Cannot create new component: {component_type} is an invalid type"
            )
            raise Exception

        # are slacks required?
        if self.enable_slacks:
            # create a slack for the new component
            self.__slack_component(component_type, name)

    def add_connection(
        self,
        origin,
        destination,
        *,
        to_losses=False,
        name=None,
        flowtype=None,
        weight=None,
        weight_sink=None,
        weight_source=None,
    ):
        """
        This function ads a new connection between two components to the factory
        :param origin: name-string of the source component
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
        new_connection = factory_connection.connection(
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

        # set new connection as output for the source component
        self.components[origin].set_output(new_connection)

        # set connection as validate for the sink component
        self.components[destination].set_input(new_connection)

        # insert the new connection into the connection_list of the factory
        self.connections[self.next_ids["connection"]] = new_connection

        # increment the connection-id counter of the factory
        self.next_ids["connection"] += 1

        # writelog
        logging.debug(
            f"        - New connection {new_connection.name} of flowtype {new_connection.flowtype.name} added between {self.components[origin].name} and {self.components[destination].name} with connection_id {self.next_ids['connection']}"
        )

    def save(self, file_path, *, overwrite=False):
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

    def show_structure(self):
        # TODO:Remove this when we feel that the project doesnt need it anymore
        # check, if structure is already valid
        self.check_validity()

        # create a list of existing connections to be displayed
        connection_list = np.empty((0, 4), int)
        connection_colorlist = []
        for i in self.connections:
            connection_list = np.append(
                connection_list,
                np.array(
                    [
                        [
                            self.connections[i].source.component_id,
                            self.connections[i].sink.component_id,
                            self.connections[i].weight_source,
                            self.connections[i].connection_id,
                        ]
                    ]
                ),
                axis=0,
            )
            # add the color of the new connection to the colorlist
            connection_colorlist.append(self.connections[i].flowtype.connection_color)

        component_colorlist = []
        for i in self.components:
            component_colorlist.append(
                self.components[i].flowtype.component_color
            )  # add fitting color to the colorlist

        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=70,
                        thickness=10,
                        line=dict(color="black", width=0.8),
                        label=self.component_names,
                        color=component_colorlist,
                    ),
                    link=dict(
                        source=connection_list[
                            :, 0
                        ],  # indices correspond to labels, eg A1, A2, A1, B1, ...
                        target=connection_list[:, 1],
                        value=connection_list[:, 2],
                        color=connection_colorlist,
                    ),
                )
            ]
        )

        fig.update_layout(title_text=f"Factory Structure", font_size=15)
        fig.show()

    def set_configuration(self, component, parameters):
        """
        This function takes a string-identifier of a component in a factory and a dict of configuration parameters.
        It hands the configuration parameters over to the set_configuration method of the component.
        :param component: string-identifier of a component in the factory
        :param parameters: dict with name-value-combinations for configuring the component
        """
        # make sure that the specified component exists
        self.check_existence(component)

        # call the set_configuration - methodof the factory
        self.components[component].set_configuration(self.max_timesteps, parameters)

    def check_existence(self, name):
        """
        This function checks, if a component with the specified name exists within the factory
        :param name: name of a component in the factory (string)
        :return: True/ERROR
        """
        # check, if the name exists in self.component_names
        if name not in self.component_names:
            logging.critical(f"Component {name} does not exist")
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
            "ambient_gains", is_onsite=True, cost=0.0001
        )  # Ambient gain gets a tiny cost related to it to avoid a direct feed of energy from ambient gains to thermal losses!

    def initialize_flowtypes(self):
        # this creates a basic set of the most important flowtypes that might be used in a typical simualtion setup.
        # All conversion factors are chosen in a way, that one Optimization Unit (OU) represents one MJ
        self.flowtypes["hydrogen"] = ft.flowtype(
            "hydrogen",
            "energy",
            unit_flow="kWh",
            unit_flowrate="kW",
            conversion_factor=1,
            color="#41719C",
        )
        self.flowtypes["electricity"] = ft.flowtype(
            "electricity",
            "energy",
            unit_flow="kWh",
            unit_flowrate="kW",
            conversion_factor=1,
            color="#41719C",
        )
        self.flowtypes["water"] = ft.flowtype(
            "water",
            "material",
            unit_flow="l",
            unit_flowrate="l/h",
            conversion_factor=1,
            color="#41719C",
        )
        self.flowtypes["heat"] = ft.flowtype(
            "heat_low",
            "energy",
            unit_flow="MJ",
            conversion_factor=3.6,
            color="#41719C",
        )
        self.flowtypes["material_losses"] = ft.flowtype(
            "material_losses",
            "material",
            unit_flow="unit",
            unit_flowrate="units/h",
            conversion_factor=1,
            color="#444444",
            to_losses=True,
        )
        self.flowtypes["energy_losses"] = ft.flowtype(
            "energy_losses",
            "energy",
            unit_flow="kWh",
            unit_flowrate="kW",
            conversion_factor=1,
            color="#444444",
            to_losses=True,
        )
        self.flowtypes["natural_gas"] = ft.flowtype(
            "natural_gas",
            "energy",
            unit_flow="MJ",
            conversion_factor=3.6,
            color="#41719C",
        )
        self.flowtypes["unknown"] = ft.flowtype(
            "unknown",
            "unspecified",
            unit_flow="unit",
            conversion_factor=1,
            color="#999999",
        )
        self.flowtypes["energy"] = ft.flowtype(
            "energy",
            "energy",
            unit_flow="kWh",
            unit_flowrate="kW",
            conversion_factor=1,
            color="#41719C",
        )
        self.flowtypes["material"] = ft.flowtype(
            "material",
            "material",
            unit_flow="units",
            unit_flowrate="units/h",
            conversion_factor=1,
            color="#999999",
        )

    def add_flowtype(
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
        :param name: [String] name identifier for the new flowtype (string)
        :param resource_type: [string] "energy" / "material" / "unspecified"
        :param to_losses: [Boolean] Specifies if the connection is deducting losses
        :param unit_flow: [String] Unit description for labeling flows of the flowtype
        :param unit_flowrate: [String] Unit description for labeling the flowrate of the flowtype
        :param conversion_factor: [float] conversion factor between one unit of the flow and one baseunit of the flow ressource type
        :param description: [String] Description of the flow, just for GUI and labeling purposes
        :param color: [String; #XXXXXX] Color code for displaying the flow in GUI and Figures
        """

        # make sure, that the name is still unused
        if name in self.component_names or name in self.flowtype_names:
            # if not: throw an error
            logging.critical(
                f"Cannot create Flowtype {name} because the name is already assigned"
            )
            raise Exception

        # create a new flowtype with specified parameters and store it in the factory.flows - dictionary
        self.flowtypes[name] = ft.flowtype(
            name,
            resource_type,
            to_losses=to_losses,
            unit_flow=unit_flow,
            unit_flowrate=unit_flowrate,
            conversion_factor=conversion_factor,
            description=description,
            color=color,
        )

        # add the new flowtype to the list of flowtype-keys
        self.flowtype_names.append(name)

        logging.debug(f"        - New flowtype added: {name}")

    def check_validity(self):
        """
        this function does a variety of checks to make sure that the factory is consistent in itself and doesn't
        allow for any glitches or bugs unfortunately this is necessary, because some interactions between components
        can only be checked after everything has been set up
        :return: True/False
        """

        # iterate over all components
        for component in self.components.values():

            # conducted validations depend on the component type...
            if component.type == "converter":
                # if component is a converter: ratio of inputs and outputs at converters must be valid

                # I) calculate sums of validate weights
                # initialize summing variables
                weightsum_input_energy = 0
                weightsum_input_material = 0

                # iterate over all validate connections
                for input_i in component.inputs:

                    # check if the validate refers to energy or material
                    if input_i.flowtype.type == "energy":
                        # if energy: add the weight of the incoming connection to the sum of energy validate weights
                        weightsum_input_energy += input_i.weight_sink

                    elif input_i.flowtype.type == "material":

                        # if material: add the weight of the incoming connection to the sum of material validate weights
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

                    # if energy: add the weight of the outgoing connection to the sum of energy validate weights
                    if output_i.flowtype.type == "energy":

                        # if energy:
                        weightsum_output_energy += output_i.weight_source
                    elif output_i.flowtype.type == "material":

                        # if material: add the weight of the outgoing connection to the sum of material validate weights
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

                # check, if the combination of validate and output weight sums is valid
                if weightsum_output_energy > weightsum_input_energy:
                    logging.critical(
                        f"Error in the factory architecture: The sum of weights at the energy output of converter '{component.name}' ({weightsum_output_energy}) is greater that the sum of validate weights {weightsum_input_energy}!"
                    )
                    raise Exception

                if weightsum_output_material > weightsum_input_material:
                    logging.critical(
                        f"Error in the factory architecture: The sum of weights at the material output of converter '{component.name}' ({weightsum_output_material}) is greater that the sum of validate weights {weightsum_input_material}!"
                    )
                    raise Exception

            elif component.type == "deadtime":
                # if component is a deadtime: make sure that there is at least one validate
                if len(component.inputs) == 0:
                    logging.critical(
                        f"ERROR: Deadtime-component '{component.name}' does not have an validate!"
                    )
                    raise Exception

                # makesure that there is at least one output
                if len(component.outputs) == 0:
                    logging.critical(
                        f"ERROR: Deadtime-component '{component.name}' does not have an output!"
                    )
                    raise Exception

                # make sure, that the delay is realizable within the length of allowed simulations
                if component.delay > self.max_timesteps:
                    logging.critical(
                        f"ERROR: Delay of component '{component.name}' is to large for the maximum simulation length of the factory ({self.max_timesteps}!"
                    )
                    raise Exception

            elif component.type == "triggerdemand":
                # check, that the combinations of validate and outputs connected is valid
                if not (component.input_energy or component.output_energy):
                    logging.critical(
                        f"Triggerdemand {component.name} has no inputs connected!"
                    )
                    raise Exception
                if component.input_energy and not component.output_energy:
                    logging.critical(
                        f"Triggerdemand {component.name} has an energy validate but no energy output!"
                    )
                    raise Exception
                if component.output_energy and not component.input_energy:
                    logging.critical(
                        f"Triggerdemand {component.name} has an energy output but no energy validate!"
                    )
                    raise Exception
                if component.input_material and not component.output_material:
                    logging.critical(
                        f"Triggerdemand {component.name} has a material validate but no material output!"
                    )
                    raise Exception
                if component.output_material and not component.input_material:
                    logging.critical(
                        f"Triggerdemand {component.name} has a material output but no material validate!"
                    )
                    raise Exception

        logging.info(f"Factory architecture validation successful")
        return True

    def __get_flowtype_object(self, flowtype_name):
        """
        This function takes the user validate for "flowtype" and returns the corresponding flowtype-object from the factorys flowtype-list
        :param flow_name: name identifier (string) or flowtype object
        :return: flowtype object
        """

        # has the flowtype already been handed over as a flowtype-object? If yes: just return it
        if isinstance(flowtype_name, ft.flowtype):
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

    def __slack_component(self, component_type, name):
        """
        This function creates a slack for the given component if necessary and connects it to the corresponding in- and outputs
        :param component_type: converter, pool, etc...
        :param name: identifier of the component to be slacked
        """

        # deadtimes, pools and thermalsystems get slacked in both directions
        if component_type in ["deadtime", "pool", "thermalsystem"]:

            # create new slack component
            self.add_component(f"{name}_slack", "slack")

            # connect it to the validate and output of the component
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

        # sinks get slacked on the validate side if they are not the losses sink
        elif component_type == "sink" and not (
            name == "losses_energy" or name == "losses_material"
        ):

            # create new slack component
            self.add_component(f"{name}_slack", "slack")

            # connect it to the validate of the sink
            self.add_connection(
                f"{name}_slack",
                name,
                name=f"{name}_slack_neg",
                flowtype=self.components[name].flowtype,
                weight=0.01,
            )
