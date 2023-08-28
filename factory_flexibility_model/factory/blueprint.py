# FACTORY-BLUEPRINT
# This file describes a class, which can be used to store all the information needed to create a factory-object.
# The class is used as an intermediate step for factory definition and imports

import logging

# IMPORT 3RD PARTY PACKAGES
from collections import defaultdict

import factory_flexibility_model.factory.factory as fm


class blueprint:
    def __init__(self):
        self.timefactor = 1  # timefactor of the factory. See documentation for details
        self.GUI_config = {
            "display_scaling_factor": 1
        }  # sets the size of displayed icons within the preview of the factory in the gui
        self.components = {}  # dict with all components of the factory
        self.connections = defaultdict(lambda: None)  # dict of connections
        self.flowtypes = defaultdict(lambda: None)  # list of flowtypes
        self.info = {
            "name": "Undefined",  # Standard Information, equivalent to factory-object initialization
            "description": "Undefined",
            "max_timesteps": 8760,
        }

    def to_factory(self):
        """
        This function creates the corresponding factory-object to the blueprint
        :return: [factory.factory] -> realization of the factory object described by the blueprint
        """

        # create a new factory with the parameters specified in the blueprint.
        # Input validation is happening within factory()-method
        logging.info("Creating factory object")
        factory = fm.factory(
            name=self.info["name"],
            max_timesteps=self.info["max_timesteps"],
            description=self.info["description"],
        )
        factory.create_essentials()

        # CREATE FLOWS
        logging.info("Creating flowtypes")
        for flowtype in self.flowtypes.values():

            # Add new flowtype to factory with given specifications
            factory.add_flowtype(
                name=flowtype["name"],
                resource_type=flowtype["type"],
                unit_flow=flowtype["unit_flow"],
                unit_flowrate=flowtype["unit_flowrate"],
                conversion_factor=flowtype["conversion_factor"],
                color=flowtype["color"],
            )

        # CREATE COMPONENTS
        logging.info("Creating factory components")
        # iterate over all component types
        for component in self.components.values():
            # Extract values that have to be directly specified:
            name = component["key"]
            type = component["type"]
            if "flowtype" in component:
                flowtype = component["flowtype"]
            else:
                flowtype = None

            # delete all values that are only relevant for the GUI or are already processed
            component.pop("flowtype")
            component.pop("name")
            component.pop("type")
            component.pop("position_x")
            component.pop("position_y")
            component.pop("icon")
            component.pop("key")

            # Add new component to factory
            factory.add_component(name, type, flowtype=flowtype)

            # Set configuration for remaining parameters of the component
            factory.set_configuration(name, parameters=component)

        # CREATE CONNECTIONS
        # iterate over all specified connections
        logging.info("Creating connection")
        for connection in self.connections.values():

            # add specified connection to the factory
            factory.add_connection(
                connection["from"],
                connection["to"],
                name=connection["name"],
                flowtype=connection["flowtype"],
                weight_source=connection["weight_source"],
                weight_sink=connection["weight_sink"],
                to_losses=connection["to_losses"],
            )

        factory.check_validity()

        return factory
