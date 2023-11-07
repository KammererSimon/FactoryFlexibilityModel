# IMPORTS
import yaml

# FUNCTIONS
def get_color_preset():
    """
    This function imports the file ui\\utility\\config_files\\color_preset.txt
    It contains a groups of shades per color, each predefined by a key and a hex-rgb value.
    The colorschemes are imported and returned as a dict in the following style: {"Amber": {"100": "FFECB3", "200": "FFE082",...}, "Blue": {"100":...

    :return: color_preset -> [dict]
    """

    # import colorscheme
    with open(f"factory_flexibility_model\\ui\\utility\\config_files\\color_preset.txt", "r", ) as file:
        color_preset = yaml.load(file, Loader=yaml.SafeLoader)
    return color_preset

def get_component_dummies():
    """
    This function imports a list of all existing component types plus an icon that is used as a preview for them when represented as a component in the flowchart graph.
    The information is imported as a dict in the following format: {"converter": {"id": "dummy_converter", "source": *filepath*}, "deadtime":{...

    :reaturn: component_dummies -> [dict]
    """
    with open(
        f"factory_flexibility_model\\ui\\utility\\config_files\\component_dummies.txt","r",) as file:
        component_dummies = yaml.load(file, Loader=yaml.SafeLoader)
    return component_dummies