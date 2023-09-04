# FACTORY-BLUEPRINT
# This file describes a class, which can be used to store all the information needed to create a factory-object.
# The class is used as an intermediate step for factory definition and imports

import logging

import yaml

import factory_flexibility_model.factory.Factory as fm

# IMPORTS


class Blueprint:
    def __init__(self):
        self.GUI_config = {
            "display_scaling_factor": 1
        }  # sets the size of displayed icons within the preview of the factory in the gui
        self.components = {}  # dict with all components of the factory
        self.connections = {}  # dict of connections
        self.flowtypes = {}  # list of flowtypes
        self.info = {
            "name": "Undefined_Factory",  # Standard Information, equivalent to factory-object initialization
            "description": "Undefined",
            "max_timesteps": 8760,
        }
        self.units = {}  # list of units

    def to_factory(self) -> fm.Factory:
        """
        This function creates the corresponding factory-object to the blueprint
        :return: [factory.factory] -> realization of the factory object described by the blueprint
        """

        # Check, if the Blueprint already contains some objects
        if self.components == {} or self.connections == {} or self.flowtypes == {}:
            logging.error(
                "The Blueprint doesn't contain a valid factory architecture. No Factory was created"
            )
            raise Exception

        # create a new factory with the parameters specified in the blueprint.
        # Input validation is happening within factory()-method
        logging.info("Creating factory object")
        factory = fm.Factory(
            name=self.info["name"],
            timesteps=self.info["timesteps"],
            description=self.info["description"],
            enable_slacks=self.info["enable_slacks"],
        )
        factory.create_essentials()

        # CREATE UNITS
        for key, unit in self.units.items():
            try:
                factory.add_unit(
                    key=key,
                    quantity_type=unit["quantity_type"],
                    conversion_factor=unit["conversion_factor"],
                    magnitudes=unit["magnitudes"],
                    units_flow=unit["units_flow"],
                    units_flowrate=unit["units_flowrate"],
                )
            except:
                raise TypeError(f"Definition of unit {key} is incomplete or corrupted")

        # CREATE FLOWS
        logging.info("Creating Flowtypes")
        for key, flowtype in self.flowtypes.items():
            # check for optional parameters
            if "color" in flowtype:
                color = flowtype["color"]
            else:
                color = "#999999"  # grey

            if "description" in flowtype:
                description = flowtype["description"]
            else:
                description = None

            # Add new flowtype to factory with given specifications
            factory.add_flowtype(
                key,
                name=flowtype["name"],
                unit=flowtype["unit"],
                color=color,
                description=description,
            )

        # CREATE COMPONENTS
        logging.info("Creating factory components")
        # iterate over all Component types
        for component_key, component in self.components.items():
            # check for optional parameters:
            if "flowtype" in component:
                flowtype = component["flowtype"]
            else:
                flowtype = None
            if "name" in component:
                name = component["name"]
            else:
                name = None
            # Add new Component to factory
            factory.add_component(
                component_key, component["type"], flowtype=flowtype, name=name
            )

        # CREATE CONNECTIONS
        # iterate over all specified connections
        logging.info("Creating connections")
        for key, connection in self.connections.items():
            # check for optional parameters:
            if "flowtype" in connection:
                flowtype = connection["flowtype"]
            else:
                flowtype = None
            if "name" in connection:
                name = connection["name"]
            else:
                name = None
            if "to_losses" in connection:
                to_losses = connection["to_losses"]
            else:
                to_losses = False

            # add specified connection to the factory
            factory.add_connection(
                connection["from"],
                connection["to"],
                name=name,
                key=key,
                flowtype=flowtype,
                to_losses=to_losses,
            )

        factory.check_validity()

        return factory

    def import_from_file(self, folder: str, *, overwrite: bool = False) -> bool:
        """
        This function imports a  blueprint stored as .factory-file and sets all attributes of the blueprint according to the specified confidurations of the file
        :param folder: [string] path of the folder containing the Session
        :param overwrite: [boolean] determines, if the import is conducted even if some attributes of the blueprint have already been defined.
        :return: [true] if successfull
        """

        # Check, if some specifications will be overwritten
        if not overwrite:
            if not (
                self.components
                or self.connections
                or self.flowtypes
                or self.GUI_config
                or self.units
            ):
                logging.error(
                    f"Cannot import blueprint-file into blueprint {self.info['name']}, because it is not in its initialize-state anymore and overwriting is deactivated"
                )
                return False

        # Import Units
        self.__import_units(folder)

        # Import Flowtypes
        self.__import_flowtypes(folder)

        # open yaml-file given by the user
        try:
            with open(f"{folder}\\Layout.factory") as file:
                data = yaml.load(file, Loader=yaml.UnsafeLoader)
        except:
            logging.error(
                rf"The given file is not a valid .factory - blueprint file! ({folder}\Layout.factory"
            )
            raise Exception

        # store imported date into the object
        self.components.update(data["components"])
        self.connections.update(data["connections"])
        if hasattr(data, "GUI_config"):
            self.GUI_config.update(data["GUI_config"])
        self.info.update(data["info"])

        logging.info("Blueprint import successfull")

    def __import_flowtypes(self, session_folder: str) -> bool:
        """
        This function checks for the file 'flowtypes.txt' in the session folder and imports all the information regarding required flowtypes for the layout and stores it in blueprint format under self.flowtypes.
        :param session_folder: [str] Path to the root folder of the current session
        :return: True if successfull
        """
        # open yaml-file given by the user
        try:
            with open(f"{session_folder}\\flowtypes.txt") as file:
                data = yaml.load(file, Loader=yaml.UnsafeLoader)
        except:
            logging.error(
                f"Flowtype definition file is missing or corrupted! ({session_folder}/flowtypes.txt"
            )
            raise Exception
        self.flowtypes.update(data["flowtypes"])

    def __import_units(self, session_folder: str) -> bool:
        """
        This function checks for the file 'units.txt' in the session folder and imports all the information regarding required unit types for the layout and stores it in blueprint format under self.units.
        :param session_folder: [str] Path to the root folder of the current session
        :return: True if successfull
        """
        # open yaml-file given by the user
        try:
            with open(f"{session_folder}\\units.txt") as file:
                data = yaml.load(file, Loader=yaml.UnsafeLoader)
        except:
            logging.error(
                f"Unit definition file is missing or corrupted! ({session_folder}/units.txt"
            )
            raise Exception
        self.units.update(data)

    def save(self, *, path: str = None, filename: str = None) -> bool:
        """
        This function stores the blueprint as a .factory-file under the given path.
        :param path: [string] Filepath where the file shall be saved
        :param filename: [string] Name of the file. If no name is handed over the file will be named like the factoryname defined within the blueprint
        """
        # create a set of serializable data out of the blueprint
        # initialize a new dict
        data = {
            "components": self.components,
            "connections": self.connections,
            "flowtypes": self.flowtypes,
            "GUI_config": self.GUI_config,
            "info": self.info,
            "units": self.units,
        }

        if filename is None:
            filename = self.info["name"]

        # store the blueprint dictionary as json file
        if path is None:
            with open(f"{filename}.factory", "w") as file:
                yaml.dump(data, file)
            logging.info(f"Blueprint saved as {self.info['name']}.factory")
        else:
            try:
                with open(f"{path}\\{filename}.factory", "w") as file:
                    yaml.dump(data, file)
                logging.info(f"Blueprint saved under {path}\\{filename}.factory")
            except:
                logging.error(
                    f"Saving blueprint under '{path}\\{filename}.factory' failed!"
                )
