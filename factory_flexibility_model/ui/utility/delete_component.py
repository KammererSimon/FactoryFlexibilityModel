# IMPORTS
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar.snackbar import MDSnackbar

from factory_flexibility_model.ui.gui_components.layout_canvas.factory_visualisation import (
    initialize_visualization,
)
from factory_flexibility_model.ui.utility.window_handling import close_dialog


# FUNCTIONS
def delete_selected_component(app):
    """
    This function deletes the component that is currently selected within the app.
    The component to be deleted is defined through the current entry of app.selected_asset.
    Deleting the component consists of three steps:

    1) At first, the function goes through all connections within app.blueprint.connections and deletes all instances that involve the selected component as origion or destination.

    2) The selected component might already have some parameters defined within app.session_data["parameters"]. If there is a key for the component in this dict, the entry is being removed

    3) The component itself is being deleted from app.blueprint.components

    Finally the GUI is resettet by setting app.selected_asset to None, calling the welcome screen on the right side and calling app.initialize_visualization() to redraw the system layout without the deleted component

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # make sure that no dialog remains open
    close_dialog(app)

    # check, which connections need to be removed along with the component
    delete_list = []
    for connection in app.blueprint.connections:
        if (
            app.blueprint.connections[connection]["from"] == app.selected_asset["key"]
        ) or (app.blueprint.connections[connection]["to"] == app.selected_asset["key"]):
            delete_list.append(connection)

    # delete all parameters saved for the component
    for scenario in app.session_data["scenarios"].values():
        del scenario[app.selected_asset["key"]]

    # make sure that no connection to the component is set as a primary flow at any converter
    for component in app.blueprint.components.values():
        if component["type"] == "converter":
            if component["GUI"]["primary_flow"] == app.selected_asset["key"]:
                component["GUI"]["primary_flow"] = None

    # delete connections related to the component
    for connection in delete_list:
        # delete connection itself
        del app.blueprint.connections[connection]
        # delete scenario configurations concerning the connection
        for scenario in app.session_data["scenarios"].values():
            if connection in scenario:
                del scenario[connection]

    # inform the user
    MDSnackbar(MDLabel(text=f"{app.selected_asset['name']} has been deleted!")).open()
    # delete the component out of the blueprint
    del app.blueprint.components[app.selected_asset["key"]]

    # now there is no more selected component
    app.selected_asset = None
    app.root.ids.asset_config_screens.current = "flowtype_list"

    # redraw the visualisation without the selected component
    initialize_visualization(app)
