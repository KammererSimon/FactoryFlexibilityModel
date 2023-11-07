# IMPORTS
import os

import yaml

import factory_flexibility_model.ui.utility.color as color


# FUNCTIONS
def get_files_in_directory(directory_path):
    """
    This is a helper function that scrapes through a folder and creates a dict with the names  and paths of all contained .png-assets
    """
    files_dict = {}
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            filename, extension = os.path.splitext(file)
            if extension == ".png":
                files_dict[filename] = os.path.join(root, file)
    return files_dict


def import_config():
    """
    This function imports the following config files:

    - ui\\utility\\config_files\\assets.txt
        -> This file contains a list of key/path combinations. The Keys are used to adress .png icons in the code without hardcoding their paths

    - ui\\utility\\config_files\\color_preset.txt
        -> This file contains a set of colors that are offered within the colorpicker and are used for some gui elements

    - ui\\utility\\config_files\\component_definitions.txt
        -> This file is a list with all the components of the factory flexibility model. For each component it contains the information, which parameters shall be configuratble in the gui, some standard icons and some standardised descriptions.

    - ui\\utility\\config_files\\config.txt
        -> This file contains a set of basic configuration parameters that are directly being copied to the output config file of the function.



    :return: [dict] with config parameters for the gui. It contains all parameters that define the style and some basic behaviour of the GUI, independent from the session that is being loaded. The dict cointains the following parameters:

        - "component_definitions": The set of component definitions from ui\\utility\\config_files\\component_definitions.txt

        - "display_grid_size": Defines the number of grid points that components can snap to underlying the visualisation

        - "main_color": `color`_ -object of the main color of the gui

        - "color_preset": color_preset from ui\\utility\\config_files\\color_preset.txt

        - "display_scaling_factor": A scaling factor that determines the size that icons appear on the screen. 1->200px width.

        - "assets": A dict containing all the information on how all required png assets are stored on the harddrive

        - "show_component_config_dialog_on_creation": [Boolean], determines if the user is asked to set a name for a new component directly on their creation
    """
    # import config.txt
    with open(
        f"factory_flexibility_model\\ui\\utility\\config_files\\config.txt",
    ) as file:
        config_file = yaml.load(file, Loader=yaml.SafeLoader)

    # import colorscheme
    with open(
        f"factory_flexibility_model\\ui\\utility\\config_files\\color_preset.txt",
    ) as file:
        color_preset = yaml.load(file, Loader=yaml.SafeLoader)

    # import component_definition.txt
    with open(
        f"factory_flexibility_model\\ui\\utility\\config_files\\component_definitions.txt",
    ) as file:
        component_definitions = yaml.load(file, Loader=yaml.SafeLoader)

    # import asset paths
    with open(
        f"factory_flexibility_model\\ui\\utility\\config_files\\assets.txt",
    ) as file:
        asset_paths = yaml.load(file, Loader=yaml.SafeLoader)

    asset_paths["component_icons"] = get_files_in_directory(
        rf"{config_file['asset_folder']}\\components"
    )
    asset_paths["source_icons"] = get_files_in_directory(
        rf"{config_file['asset_folder']}\\sources"
    )
    asset_paths["sink_icons"] = get_files_in_directory(
        rf"{config_file['asset_folder']}\\sinks"
    )
    asset_paths["default_icons"] = get_files_in_directory(
        rf"{config_file['asset_folder']}\\defaults"
    )

    config = {
        "component_definitions": component_definitions,
        "display_grid_size": [
            config_file["display_grid_points_x"],
            config_file["display_grid_points_y"],
        ],  # number of grid points underlying the visualisation
        "main_color": color.color(config_file["main_color"]),
        "color_preset": color_preset,
        "display_scaling_factor": config_file["display_scaling_factor"],
        "display_scaling_exponent": config_file["display_scaling_exponent"],
        "assets": asset_paths,
        "show_component_config_dialog_on_creation": config_file[
            "show_component_config_dialog_on_creation"
        ],
    }

    return config
