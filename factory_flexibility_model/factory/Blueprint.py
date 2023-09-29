# FACTORY-BLUEPRINT
# This file describes a class, which can be used to store all the information needed to create a factory-object.
# The class is used as an intermediate step for factory definition and imports

import logging

import yaml

import factory_flexibility_model.factory.Factory as fm
import factory_flexibility_model.factory.Flowtype as ft
import factory_flexibility_model.factory.Unit as un

# IMPORTS


class Blueprint:
    def __init__(self):
        self.components = {}  # dict with all components of the factory
        self.connections = {}  # dict of connections
        self.flowtypes = {}  # list of flowtypes
        self.info = {
            "name": "Undefined_Factory",  # Standard Information, equivalent to factory-object initialization
            "description": "Undefined",
            "timesteps": 168,
            "enable_slacks": False,
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
            # skip the basic units
            if key in ["energy", "mass"]:
                continue

            factory.add_unit_object(unit, key)

        # CREATE FLOWS
        logging.info("Creating Flowtypes")
        for key, flowtype in self.flowtypes.items():
            # Add new flowtype to factory with given specifications
            factory.add_flowtype_object(flowtype)

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
                weight_source=connection["weight_source"],
                weight_sink=connection["weight_sink"],
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
            if self.components or self.connections or self.flowtypes or self.units:
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

        # exchange flowtype keys with their objects
        for component in data["components"].values():
            if "flowtype" in component.keys():
                component["flowtype"] = self.flowtypes[component["flowtype"]]
        for connection in data["connections"].values():
            connection["flowtype"] = self.flowtypes[connection["flowtype"]]

        # store imported date into the object
        self.components.update(data["components"])
        self.connections.update(data["connections"])
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

        # recreate flowtype objects
        for key, flowtype in data.items():
            self.flowtypes[key] = ft.Flowtype(
                key=key,
                unit=self.units[flowtype["unit"]],
                description=flowtype["description"],
                represents_losses=flowtype["represents_losses"],
                name=flowtype["name"],
                color=flowtype["color"],
            )

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

        # recreate unit objects
        try:
            for key, unit in data.items():
                self.units[key] = un.Unit(
                    key=key,
                    quantity_type=unit["quantity_type"],
                    conversion_factor=unit["conversion_factor"],
                    magnitudes=unit["magnitudes"],
                    units_flow=unit["units_flow"],
                    units_flowrate=unit["units_flowrate"],
                    name=unit["name"],
                )
        except:
            raise TypeError(f"Definition of unit {key} is incomplete or corrupted")

    def save(self, *, path: str = None) -> bool:
        """
        This function stores the blueprint as a .factory-file under the given path.
        :param path: [string] Filepath where the file shall be saved
        :param filename: [string] Name of the file. If no name is handed over the file will be named like the factoryname defined within the blueprint
        """

        # Create Layout.factory-file
        data = {
            "components": {},
            "connections": {},
            "info": self.info,
        }

        # exchange flowtype objects with their keys
        # copying the full dict while just taking the flowtype key instead of the flowtype object to avoid using deepcopy
        for component in self.components.values():
            data["components"][component["key"]] = {
                "GUI": component["GUI"],
                "name": component["name"],
                "key": component["key"],
                "description": component["description"],
                "type": component["type"],
                "flowtype": component["flowtype"].key,
            }

        for connection in self.connections.values():
            data["connections"][connection["key"]] = {
                "name": connection["name"],
                "from": connection["from"],
                "to": connection["to"],
                "flowtype": connection["flowtype"].key,
                "key": connection["key"],
                "weight_source": connection["weight_source"],
                "weight_sink": connection["weight_sink"],
                "to_losses": connection["to_losses"],
                "type": connection["type"],
            }

        # store the Layout as json file
        try:
            with open(f"{path}\\Layout.factory", "w") as file:
                yaml.dump(data, file)
            logging.info(f"Blueprint saved under {path}")
        except:
            logging.error(f"Saving blueprint under '{path}' failed!")

        # Create units.txt
        units_data = {}
        for key, unit in self.units.items():
            units_data[key] = {}
            units_data[key]["name"] = unit.name
            units_data[key]["quantity_type"] = unit.quantity_type
            units_data[key]["conversion_factor"] = unit.conversion_factor
            units_data[key]["units_flow"] = unit.units_flow
            units_data[key]["units_flowrate"] = unit.units_flowrate
            units_data[key]["magnitudes"] = unit.magnitudes.tolist()

        try:
            with open(f"{path}\\units.txt", "w") as file:
                yaml.dump(units_data, file)
            logging.info(f"units.txt saved under {path}")
        except:
            logging.error(f"Saving units.txt under '{path}' failed!")

        # Create flowtypes.txt
        flowtypes_data = {}
        for key, flowtype in self.flowtypes.items():
            flowtypes_data[key] = {}
            flowtypes_data[key]["color"] = flowtype.color.hex
            flowtypes_data[key]["unit"] = flowtype.unit.key
            flowtypes_data[key]["description"] = flowtype.description
            flowtypes_data[key]["name"] = flowtype.name
            flowtypes_data[key]["represents_losses"] = flowtype.represents_losses

        try:
            with open(f"{path}\\flowtypes.txt", "w") as file:
                yaml.dump(flowtypes_data, file)
            logging.info(f"flowtypes.txt saved under {path}")
        except:
            logging.error(f"Saving flowtypes.txt under '{path}' failed!")
