# FACTORY MODEL
# This Package contains everything that is needed to specify the structure of a factory for the simulation:
#        -> "factory" is the main class and the only one meant to be called by the user.
#               It collects all given Information and organizes the setup process
#        -> "flow" specifies a flow of energy/material

import pickle
import warnings
from pathlib import Path

# IMPORT 3RD PARTY PACKAGES
import numpy as np
import plotly.graph_objects as go

# IMPORT ENDOGENOUS COMPONENTS
import factory_flexibility_model.input_validations as iv
from factory_flexibility_model.factory import factory_components as factory_components
from factory_flexibility_model.factory import factory_connection as factory_connection
from factory_flexibility_model.factory import factory_flow as ff


# CODE START
class factory:
    def __init__(self, **kwargs):
        # Initialize structure variables
        self.connections = {}
        self.components = {}
        self.component_names = []
        self.flows = {}
        self.flow_names = []
        self.next_ids = {
            "connection": 0,
            "component": 0,
        }  # Internal counter. Everytime a component or connection is added it gets the next value and the counter is incremented
        self.version = 20221201

        # Initialize user configurable variables
        if (
            "max_timesteps" in kwargs
        ):  # maximum length of a single simulation run is set to one year
            self.max_timesteps = iv.input(kwargs["max_timesteps"], "int")
        else:
            self.max_timesteps = 8760

        if "name" in kwargs:  # Factory Name
            self.name = iv.input(kwargs["name"], "string")
        else:
            self.name = "Unspecified Factory"

        if "description" in kwargs:  # Factory Description
            self.description = iv.input(kwargs["description"], "string")
        else:
            self.description = "Unspecified Factory"

        # enable slacking if specified by the user
        if "enable_slacks" in kwargs:  # General setting
            self.enable_slacks = iv.input(kwargs["enable_slacks"], "boolean")
        else:
            self.enable_slacks = False

        # set the timefactor
        if (
            "timefactor" in kwargs
        ):  # how many hours does one timestep of the factory represent?
            self.timefactor = iv.input(kwargs["timefactor"], "float")
        else:
            self.timefactor = 1  # standard value: 1 Timestep = 1 hour

        # create the set of standard flows
        self.initialize_flows()

        # enable logging if specified by the user
        if (
            "enable_log" in kwargs
        ):  # set to true if the factory building shall be logged in the console
            self.log = iv.input(kwargs["enable_log"], "boolean")
        else:
            self.log = False

        # write log
        if self.log:
            print("        - New factory created")

    def add_component(self, name, component_type, **kwargs):
        # validate the given inputs as strings
        name = iv.input(name, "str")
        component_type = iv.input(component_type, "str")

        # did the user specify a flow?
        if "flow" in kwargs:
            # make sure that kwargs contains a valid flow-object. Exchange a user given string identifier with the flow if necessary
            kwargs["flow"] = self.__get_flow_object(kwargs["flow"])

        # make sure that the specified name is not already taken by a component or flow
        if name in self.component_names or name in self.flow_names:
            raise Exception(
                f"Cannot create Component {name} because the name is already assigned"
            )

        # Add name of the new component to the namelist
        self.component_names.append(name)

        # create new object of desired component
        if component_type == "pool":
            # call pool constructor
            self.components[name] = factory_components.pool(name, self, **kwargs)

        elif component_type == "sink":
            # call sink constructor
            self.components[name] = factory_components.sink(name, self, **kwargs)

        elif component_type == "source":
            # call source constructor
            self.components[name] = factory_components.source(name, self, **kwargs)

        elif component_type == "storage":
            # call storage constructor
            self.components[name] = factory_components.storage(name, self, **kwargs)

            # auto generate a connection to losses: determine, whether storage refers to energy or material and connect it to the corresponding loss sink
            if self.components[name].flow.is_energy():

                # create connection to losses_energy if flow is a type of energy
                self.add_connection(
                    name,
                    "losses_energy",
                    name=f"{name}_to_Elosses",
                    flow="energy_losses",
                    weight=0.01,
                    to_losses=True,
                )

            elif self.components[name].flow.is_material():

                # create a connection to losses_material if flow is a type of material
                self.add_connection(
                    name,
                    "losses_material",
                    name=f"{name}_to_Mlosses",
                    flow="material_losses",
                    weight=0.01,
                    to_losses=True,
                )

            # raise an error if the flowtype of the storage is unspecified
            else:
                raise Exception(
                    f"Losses-connection for {name} could not be created because the flowtype isn't specified!"
                )

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
                name, self, **kwargs
            )

            # connect the new thermalsystem to losses_energy
            self.add_connection(
                name,
                "losses_energy",
                name=f"{name}_to_Elosses",
                flow="energy_losses",
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
            self.components[name] = factory_components.triggerdemand(
                name, self, **kwargs
            )

        elif component_type == "slack":
            # call slack constructor
            self.components[name] = factory_components.slack(name, self, **kwargs)

        elif component_type == "schedule":
            # call schedule constructor
            self.components[name] = factory_components.schedule(name, self, **kwargs)
        else:
            # if we end here the given type must have been invalid! -> Throw an error
            raise Exception(
                f"Cannot create new component: {component_type} is an invalid type"
            )

        # if no flow has been assigned till now: set it as "unknown"
        if self.components[name].flow is None:
            self.components[name].flow = self.flows[kwargs["unknown"]]

        # are slacks required?
        if self.enable_slacks:
            # create a slack for the new component
            self.__slack_component(component_type, name)

    def add_connection(self, origin, destination, **kwargs):
        """
        This function ads a new connection between two components to the factory
        :param origin: name-string of the source component
        :param destination: name-string of the sink
        :param kwargs: weights, name, etc.
        """
        # check, if specified sink and source components exist
        self.check_existence(origin)
        self.check_existence(destination)

        # if a flow is specified...
        if "flow" in kwargs:
            # ...make sure, that kwargs refers to the actual flow and does not only contain the string key
            kwargs["flow"] = self.__get_flow_object(kwargs["flow"])

        # create new connection as object
        new_connection = factory_connection.connection(
            self.components[origin],
            self.components[destination],
            self.next_ids["connection"],
            **kwargs,
        )

        # set new connection as output for the source component
        self.components[origin].set_output(new_connection, **kwargs)

        # set connection as input for the sink component
        self.components[destination].set_input(new_connection, **kwargs)

        # insert the new connection into the connection_list of the factory
        self.connections[self.next_ids["connection"]] = new_connection

        # increment the connection-id counter of the factory
        self.next_ids["connection"] += 1

        # writelog
        if self.log:
            print(
                f"        - New connection {new_connection.name} of flowtype {new_connection.flow.name} added between {self.components[origin].name} and {self.components[destination].name} with connection_id {self.next_ids['connection']}"
            )

    def save(self, file_path, **kwargs):
        """
        This function saves a factory-object under the specified filepath as a single file.
        :param file_path: Path to the file to be created
        :param kwargs: Set "overwrite=True" to allow the method to overwrite existing files.
        Otherwise an error will occur when trying to overwrite a file
        :return: Nothing
        """

        # determine, if an existing file will be overwritten or not
        if "overwrite" in kwargs:
            overwrite_existing_file = kwargs["overwrite"]
        else:
            overwrite_existing_file = False

        # check, if file already exists
        file = Path(file_path)
        if file.is_file():
            if overwrite_existing_file:
                warnings.warn(
                    f"WARNING: The specified file already exists and will be overwritten"
                )
            else:
                raise Exception(
                    f"ERROR: The specified file already exists! Saving Factory aborted!"
                )

        # save the factory at the given path
        with open(file_path, "wb") as f:
            pickle.dump(self, f)

        # write log
        if self.log:
            print(f"FACTORY SAVED under {file_path}")

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
            connection_colorlist.append(self.connections[i].flow.connection_color)

        component_colorlist = []
        for i in self.components:
            component_colorlist.append(
                self.components[i].flow.component_color
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

    def set_configuration(self, component, **kwargs):
        """
        This function takes a string-identifier of a component in a factory and a set of kwargs with configurations.
        It hands the configuration parameters from kwargs over to the set_configuration method of the component.
        :param component: string-identifier of a component in the factory
        :param kwargs: name-value-combinations for configuring the component
        """
        # make sure that the specified component exists
        self.check_existence(component)

        # call the set_configuration - methodof the factory
        self.components[component].set_configuration(self.max_timesteps, **kwargs)

    def check_existence(self, name):
        """
        This function checks, if a component with the specified name exists within the factory
        :param name: name of a component in the factory (string)
        :return: True/ERROR
        """
        # check, if the name exists in self.component_names
        if name not in self.component_names:
            raise Exception(f"Component {name} does not exist")
        # return True

    def create_essentials(self):
        # create standard assets
        self.add_component("losses_energy", "sink", flow=self.flows["energy_losses"])
        self.add_component(
            "losses_material", "sink", flow=self.flows["material_losses"]
        )
        self.add_component("ambient_gains", "source", flow=self.flows["heat"])
        self.set_configuration(
            "ambient_gains", is_onsite=True, cost=0.0001
        )  # Ambient gain gets a tiny cost related to it to avoid a direct feed of energy from ambient gains to thermal losses!

    def initialize_flows(self):
        # this creates a basic set of the most important flows that might be used in a typical simualtion setup.
        # All conversion factors are chosen in a way, that one Optimization Unit (OU) represents one MJ
        self.flows["hydrogen"] = ff.flow(
            "hydrogen",
            "energy",
            unit_energy="kWh",
            unit_power="kW",
            conversion_factor=1,
            component_color="#41719C",
            connection_color="#819799",
        )
        self.flows["electricity"] = ff.flow(
            "electricity",
            "energy",
            unit_energy="kWh",
            unit_power="kW",
            conversion_factor=1,
            component_color="#41719C",
            connection_color="#6FAC47",
        )
        self.flows["water"] = ff.flow(
            "water",
            "material",
            unit_energy="l",
            unit_power="l/h",
            conversion_factor=1,
            component_color="#41719C",
            connection_color="#A9CACD",
        )
        self.flows["heat"] = ff.flow(
            "heat_low",
            "energy",
            unit_energy="MJ",
            conversion_factor=3.6,
            component_color="#41719C",
            connection_color="#ED7D31",
        )
        self.flows["material_losses"] = ff.flow(
            "material_losses",
            "material",
            unit_energy="unit",
            unit_power="units/h",
            conversion_factor=1,
            component_color="#444444",
            connection_color="#d0d0d0",
            to_losses=True,
        )
        self.flows["energy_losses"] = ff.flow(
            "energy_losses",
            "energy",
            unit_energy="kWh",
            unit_power="kW",
            conversion_factor=1,
            component_color="#444444",
            connection_color="#d0d0d0",
            to_losses=True,
        )
        self.flows["natural_gas"] = ff.flow(
            "natural_gas",
            "energy",
            unit_energy="MJ",
            conversion_factor=3.6,
            component_color="#41719C",
            connection_color="#FFC000",
        )
        self.flows["unknown"] = ff.flow(
            "unknown",
            "unspecified",
            unit_energy="unit",
            conversion_factor=1,
            component_color="#999999",
            connection_color="#777777",
        )
        self.flows["energy"] = ff.flow(
            "energy",
            "energy",
            unit_energy="kWh",
            unit_power="kW",
            conversion_factor=1,
            component_color="#41719C",
            connection_color="#BDD7EE",
        )
        self.flows["material"] = ff.flow(
            "material",
            "material",
            unit_energy="units",
            unit_power="units/h",
            conversion_factor=1,
            component_color="#999999",
            connection_color="#41719C",
        )

    def add_flow(self, name, flow_type, **kwargs):
        """
        This function ads a flow to the factory
        :param name: name identifier for the new flow (string)
        :param flow_type: energy/material/unspecified
        :param kwargs: additional kwargs for flow setup
        """

        # make sure, that the name is still unused
        if name in self.component_names or name in self.flow_names:
            # if not: throw an error
            raise Exception(
                f"Cannot create Flow {name} because the name is already assigned"
            )

        # create a new flow with specified parameters and store it in the factory.flows - dictionary
        self.flows[name] = ff.flow(name, flow_type, **kwargs)

        # add the new flow to the list of flows-keys
        self.flow_names.append(name)

        # write log
        if self.log:
            print(f"        - New flow added: {name}")

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

                # I) calculate sums of input weights
                # initialize summing variables
                weightsum_input_energy = 0
                weightsum_input_material = 0

                # iterate over all input connections
                for input_i in component.inputs:

                    # check if the input refers to energy or material
                    if input_i.flow.type == "energy":
                        # if energy: add the weight of the incoming connection to the sum of energy input weights
                        weightsum_input_energy += input_i.weight_sink

                    elif input_i.flow.type == "material":

                        # if material: add the weight of the incoming connection to the sum of material input weights
                        weightsum_input_material += input_i.weight_sink

                    else:
                        # otherwise the type of the flow remained unspecified during factory setup und therefore is invalid
                        raise Exception(
                            f"Flowtype of connection {input_i.name} is still unknown! The flowtype needs to be specified in order to correctly bilance it at {component.name}"
                        )

                # II) calculate sum of output weights
                # initialize summing variables
                weightsum_output_energy = 0
                weightsum_output_material = 0

                # iterate over all output connections
                for output_i in component.outputs:

                    # if energy: add the weight of the outgoing connection to the sum of energy input weights
                    if output_i.flow.type == "energy":

                        # if energy:
                        weightsum_output_energy += output_i.weight_source
                    elif output_i.flow.type == "material":

                        # if material: add the weight of the outgoing connection to the sum of material input weights
                        weightsum_output_material += output_i.weight_source

                    else:
                        # otherwise the type of the flow remained unspecified during factory setup und therefore is invalid
                        raise Exception(
                            f"Flowtype of connection {output_i.name} is still unknown! The flowtype needs to be specified in order to correctly bilance it at {component.name}"
                        )

                # check, if there are any inputs
                if weightsum_input_energy == 0 and weightsum_input_material == 0:
                    raise Exception(
                        f"ERROR: converter {component.name} does not have any inputs connected!"
                    )

                # if there is energy involved: calculate the base energy efficiency (used for visualisations later)
                if weightsum_input_energy > 0:
                    component.eta_base = (
                        weightsum_output_energy / weightsum_input_energy
                    )

                # check, if the combination of input and output weight sums is valid
                if weightsum_output_energy > weightsum_input_energy:
                    raise Exception(
                        f"Error in the factory architecture: The sum of weights at the energy output of converter '{component.name}' ({weightsum_output_energy}) is greater that the sum of input weights {weightsum_input_energy}!"
                    )

                if weightsum_output_material > weightsum_input_material:
                    raise Exception(
                        f"Error in the factory architecture: The sum of weights at the material output of converter '{component.name}' ({weightsum_output_material}) is greater that the sum of input weights {weightsum_input_material}!"
                    )

            elif component.type == "deadtime":
                # if component is a deadtime: make sure that there is at least one input
                if len(component.inputs) == 0:
                    raise Exception(
                        f"ERROR: Deadtime-component '{component.name}' does not have an input!"
                    )

                # makesure that there is at least one output
                if len(component.outputs) == 0:
                    raise Exception(
                        f"ERROR: Deadtime-component '{component.name}' does not have an output!"
                    )

                # make sure, that the delay is realizable within the length of allowed simulations
                if component.delay > self.max_timesteps:
                    raise Exception(
                        f"ERROR: Delay of component '{component.name}' is to large for the maximum simulation length of the factory ({self.max_timesteps}!"
                    )

            elif component.type == "triggerdemand":
                # check, that the combinations of input and outputs connected is valid
                if not (component.input_energy or component.output_energy):
                    raise Exception(
                        f"Triggerdemand {component.name} has no inputs connected!"
                    )
                if component.input_energy and not component.output_energy:
                    raise Exception(
                        f"Triggerdemand {component.name} has an energy input but no energy output!"
                    )
                if component.output_energy and not component.input_energy:
                    raise Exception(
                        f"Triggerdemand {component.name} has an energy output but no energy input!"
                    )
                if component.input_material and not component.output_material:
                    raise Exception(
                        f"Triggerdemand {component.name} has a material input but no material output!"
                    )
                if component.output_material and not component.input_material:
                    raise Exception(
                        f"Triggerdemand {component.name} has a material output but no material input!"
                    )

        return True

    def __get_flow_object(self, flow_name):
        """
        This function takes the user input for "flow" and returns the corresponding flow-object from the factorys flow-list
        :param flow_name: name identifier (string) or flow object
        :return: flow object
        """

        # has the flow already been handed over as a flow-object? If yes: just return it
        if isinstance(flow_name, ff.flow):
            return flow_name

        # if no: check if the flow-identifier has been handed over as a string
        if not isinstance(flow_name, str):
            raise Exception(
                "Flows must be specified with their name identifiers (string) when creating components!"
            )

        # check if the given flow actually exists
        if flow_name not in self.flows:
            raise Exception(
                f"The specified flowtype {flow_name} does not exist in the flowtype list of the current factory. Add it first via .add_flow(). "
                f"\n Existing flowtypes at this point are: {[i for i in self.flows]}"
            )

        # converters must not have a flow specified. Throw an error if this is what's happening...
        if type == "converter":
            raise Exception(
                f"Error while creating Converter {self.name}: Converters must not have a flowtype assigned!"
            )

        # all checks passed? -> return the pointer to the actual flow object
        return self.flows[flow_name]

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

            # connect it to the input and output of the component
            self.add_connection(
                f"{name}_slack",
                name,
                name=f"{name}_slack_neg",
                flow=self.components[name].flow,
                weight=0.01,
            )
            self.add_connection(
                name,
                f"{name}_slack",
                name=f"{name}_slack_pos",
                flow=self.components[name].flow,
                weight=0.01,
            )

        # sinks get slacked on the input side if they are not the losses sink
        elif component_type == "sink" and not (
            name == "losses_energy" or name == "losses_material"
        ):

            # create new slack component
            self.add_component(f"{name}_slack", "slack")

            # connect it to the input of the sink
            self.add_connection(
                f"{name}_slack",
                name,
                name=f"{name}_slack_neg",
                flow=self.components[name].flow,
                weight=0.01,
            )
