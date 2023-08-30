# FACTORY-BLUEPRINT
# This file describes a class, which can be used to store all the information needed to create a factory-object.
# The class is used as an intermediate step for factory definition and imports

import logging

# IMPORTS
from collections import defaultdict

import yaml

import factory_flexibility_model.factory.Factory as fm


class Blueprint:
    def __init__(self):
        self.timefactor = 1  # timefactor of the factory. See documentation for details
        self.GUI_config = {
            "display_scaling_factor": 1
        }  # sets the size of displayed icons within the preview of the factory in the gui
        self.components = {}  # dict with all components of the factory
        self.connections = defaultdict(lambda: None)  # dict of connections
        self.flowtypes = defaultdict(lambda: None)  # list of flowtypes
        self.info = {
            "name": "Undefined_Factory",  # Standard Information, equivalent to factory-object initialization
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
        factory = fm.Factory(
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
                name=flowtype["key"],
                unit=flowtype["unit"],
                color=flowtype["color"],
            )

        # CREATE COMPONENTS
        logging.info("Creating factory components")
        # iterate over all Component types
        for component in self.components.values():
            # Extract values that have to be directly specified:
            name = component["key"]
            type = component["type"]
            if "flowtype" in component:
                flowtype = component["flowtype"]
            else:
                flowtype = None

            # create a copy of the Component with GUI specific keys removed
            component_copy = component.copy()
            component_copy.pop("flowtype")
            component_copy.pop("type")
            component_copy.pop("position_x")
            component_copy.pop("position_y")
            component_copy.pop("icon")
            component_copy.pop("key")

            # Add new Component to factory
            factory.add_component(name, type, flowtype=flowtype)

            # Set configuration for remaining parameters of the Component
            factory.set_configuration(name, parameters=component_copy)

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

    def save(self, *, path: str = None):

        # create a set of serializable data out of the blueprint
        # initialize a new dict
        data = {}

        # store only the defined values per asset. Data doesnt contain defaultdicts anymore now
        data["components"] = {}
        for component in self.components.values():
            data["components"][component["key"]] = {}
            for value in component:
                if not value == "key":
                    data["components"][component["key"]][value] = component[value]

        data["connections"] = {}
        for connection in self.connections.values():
            data["connections"][connection["key"]] = {}
            for value in connection:
                if not value == "key":
                    data["connections"][connection["key"]][value] = connection[value]

        data["flowtypes"] = {}
        for flowtype in self.flowtypes.values():
            data["flowtypes"][flowtype["key"]] = {}
            for value in flowtype:
                if not value == "key":
                    data["flowtypes"][flowtype["key"]][value] = flowtype[value]

        data["info"] = self.info

        # store the blueprint dictionary as json file
        if path is None:
            with open(f"{self.info['name']}.factory", "w") as file:
                yaml.dump(data, file)
            logging.info(f"Blueprint saved as {self.info['name']}.factory")
        else:
            try:
                with open(f"{path}.factory", "w") as file:
                    yaml.dump(data, file)
                logging.info(f"Blueprint saved as {path}.factory")
            except:
                logging.error(f"Saving blueprint under '{path}.factory' failed!")
