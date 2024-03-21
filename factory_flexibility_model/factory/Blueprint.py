"""
.. _Blueprint:
A Blueprint is a helper class that describes the architecture of a factory including all units, flowtypes, components and connections plus some additional info.

It is used as a common interface for different input methods to connect to the simulation pipeline.

Blueprints can be translated to `Factory`_ -objects using the `to_factory()`_ method to conduct simulations.

Blueprints can be serialized, stored to files, manually edited and reimported using the `save()`_ and `import_from_file()`_ methods
"""

import logging

import yaml

import factory_flexibility_model.factory.Factory as fm
import factory_flexibility_model.factory.Flowtype as ft
import factory_flexibility_model.factory.Unit as un


class Blueprint:
    """
    Represents a blueprint for a factory.

    This class defines the structure of a factory, including its components, connections,
    flowtypes, and various information.

    Attributes:
        +----------------+------------------------------------------------------------+
        | Attribute      | Description                                                |
        +================+============================================================+
        | components     | A dictionary of all components in the factory.             |
        +----------------+------------------------------------------------------------+
        | connections    | A dictionary of connections between components.            |
        +----------------+------------------------------------------------------------+
        | flowtypes      | A dictionary of available flowtypes.                       |
        +----------------+------------------------------------------------------------+
        | info           | Additional information about the factory, including:       |
        |                |   - 'name' (str): The name of the factory (default:        |
        |                |     "Undefined_Factory").                                  |
        |                |   - 'description' (str): A description of the factory      |
        |                |     (default: "Undefined").                                |
        |                |   - 'timesteps' (int): The number of timesteps (default:   |
        |                |     168).                                                  |
        |                |   - 'enable_slacks' (bool): Flag to enable or disable      |
        |                |     slack handling (default: False).                       |
        |                |   - 'timestep_length' (int): The length of each timestep   |
        |                |     (default: 1).                                          |
        |                |   - 'currency' (str): The currency used (default: "€").    |
        |                |   - 'emission_limit' (None or float): Emission limit for   |
        |                |     the factory (default: None).                           |
        |                |   - 'emission_cost' (None or float): Cost associated with  |
        |                |     emissions (default: None).                             |
        +----------------+------------------------------------------------------------+
        | units          | A dictionary of available units.                           |
        +----------------+------------------------------------------------------------+
    """

    def __init__(self):
        self.components = {}  # dict with all components of the factory
        self.connections = {}  # dict of connections
        self.flowtypes = {}  # list of flowtypes
        self.info = {
            "name": "Undefined_Factory",  # Standard Information, equivalent to factory-object initialization
            "description": "Undefined",
            "timesteps": 168,
            "enable_slacks": False,
            "timestep_length": 1,
            "currency": "€",
            "emission_limit": None,
            "emission_cost": None,
        }
        self.units = {}  # list of units

    def import_from_file(self, blueprint_file: str, *, overwrite: bool = False) -> bool:
        """
        .. _import_from_file():
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

        # open yaml-file given by the user
        try:
            with open(blueprint_file) as file:
                data = yaml.load(file, Loader=yaml.UnsafeLoader)
        except:
            logging.error(
                rf"The given file is not a valid .factory - blueprint file! ({file}"
            )
            raise Exception

        # recreate unit objects
        for unit_key, unit in data["units"].items():
            self.units[unit_key] = un.Unit(
                key=unit_key,
                quantity_type=unit["quantity_type"],
                conversion_factor=unit["conversion_factor"],
                magnitudes=unit["magnitudes"],
                units_flow=unit["units_flow"],
                units_flowrate=unit["units_flowrate"],
                name=unit["name"],
            )

        # recreate flowtype objects
        for flowtype_key, flowtype in data["flowtypes"].items():
            self.flowtypes[flowtype_key] = ft.Flowtype(
                key=flowtype_key,
                unit=self.units[flowtype["unit"]],
                description=flowtype["description"],
                represents_losses=flowtype["represents_losses"],
                name=flowtype["name"],
                color=flowtype["color"],
            )

        # exchange flowtype keys with their objects
        for component in data["components"].values():
            if "flowtype" in component.keys():
                component["flowtype"] = self.flowtypes[component["flowtype"]]
        for connection in data["connections"].values():
            connection["flowtype"] = self.flowtypes[connection["flowtype"]]

        # store imported data into the object
        self.components.update(data["components"])
        self.connections.update(data["connections"])
        self.info.update(data["info"])

        logging.info("Blueprint import successfull")

    def save(self, *, path: str = None) -> bool:
        """
        .. _save():
        This function stores the blueprint as a .factory-file under the given path.

        :param path: [string] Filepath where the file shall be saved

        :param filename: [string] Name of the file. If no name is handed over the file will be named like the factoryname defined within the blueprint
        """

        # Create Layout.factory-file
        data = {
            "components": {},
            "connections": {},
            "flowtypes": {},
            "units": {},
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

        # adding connections as dict
        for connection in self.connections.values():
            data["connections"][connection["key"]] = {
                "from": connection["from"],
                "to": connection["to"],
                "flowtype": connection["flowtype"].key,
                "key": connection["key"],
                "to_losses": connection["to_losses"],
                "type": connection["type"],
            }

        # adding units as dict
        # iteration is required because magnitudes are not serializable
        for unit_key, unit in self.units.items():
            data["units"][unit_key] = {
                "name": unit.name,
                "key": unit.key,
                "quantity_type": unit.quantity_type,
                "conversion_factor": unit.conversion_factor,
                "units_flow": unit.units_flow,
                "units_flowrate": unit.units_flowrate,
                "magnitudes": unit.magnitudes.tolist(),
            }

        # adding flowtypes as dict
        for flowtype_key, flowtype in self.flowtypes.items():
            data["flowtypes"][flowtype_key] = {
                "key": flowtype_key,
                "color": flowtype.color.hex,
                "unit": flowtype.unit.key,
                "description": flowtype.description,
                "name": flowtype.name,
                "represents_losses": flowtype.represents_losses,
            }

        try:
            with open(f"{path}\\Layout.factory", "w") as file:
                yaml.dump(data, file)
            logging.info(f"Blueprint saved under {path}")
            return True
        except:
            logging.error(f"Saving blueprint under '{path}' failed!")
            return False

    def to_factory(self) -> fm.Factory:
        """
        .. _to_factory():
        This function creates the corresponding factory-object to the blueprint

        :return: [factory.Factory] -> realization of the factory object described by the blueprint
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
            currency=self.info["currency"],
            description=self.info["description"],
            enable_slacks=self.info["enable_slacks"],
            emission_limit=self.info["emission_limit"],
            emission_cost=self.info["emission_cost"],
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
            if "type" in connection:
                type = connection["type"]
            else:
                type = "default"

            # add specified connection to the factory
            factory.add_connection(
                connection["from"],
                connection["to"],
                key=key,
                flowtype=flowtype,
                type=type,
            )

        factory.check_validity()

        return factory
