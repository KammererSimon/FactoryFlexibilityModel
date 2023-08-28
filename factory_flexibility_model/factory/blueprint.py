# FACTORY-BLUEPRINT
# This file describes a class, which can be used to store all the information needed to create a factory-object.
# The class is used as an intermediate step for factory definition and imports

# IMPORT 3RD PARTY PACKAGES
from collections import defaultdict


class blueprint:
    def __init__(self):
        self.version = 20221201  # script version
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
            "enable_slacks": False,
        }
