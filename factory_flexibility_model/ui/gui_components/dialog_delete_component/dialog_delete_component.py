# IMPORTS
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

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
    close_dialog(app)

    # check, which connections need to be removed along with the component
    delete_list = []
    for connection in app.blueprint.connections:
        if (
            app.blueprint.connections[connection]["from"] == app.selected_asset["key"]
        ) or (app.blueprint.connections[connection]["to"] == app.selected_asset["key"]):
            delete_list.append(connection)

    # delete all parameters saved for the component
    del app.session_data["parameters"][app.selected_asset["key"]]

    # make sure that no connection to the component is set as a primary flow at any converter
    for component in app.blueprint.components.values():
        if component["type"] == "converter":
            if component["GUI"]["primary_flow"] == app.selected_asset["key"]:
                component["GUI"]["primary_flow"] = None

    # delete the component
    for connection in delete_list:
        Snackbar(
            text=f"Connection {app.blueprint.connections[connection]['name']} has been deleted!"
        ).open()
        del app.blueprint.connections[connection]

    # inform the user
    Snackbar(text=f"{app.selected_asset['name']} has been deleted!").open()

    # delete the component out of the blueprint
    del app.blueprint.components[app.selected_asset["key"]]

    # now there is no more selected component
    app.selected_asset = None
    app.root.ids.asset_config_screens.current = "flowtype_list"

    # redraw the visualisation without the selected component
    initialize_visualization(app)


def show_component_deletion_dialog(app):
    """
    This function is being called when the user clicks on the bin-icon in the bottom right or drags a component onto it.
    It creates and shows a dialog, that asks the user for confirmation to delete the selected component.
    If the user clicks on "CANCEL" the dialog closes without further action. Clicking on "DELETE COMPONENT" calls the function delete_selected_component(app)

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # abort if there is no asses selected
    if app.selected_asset is None:
        return

    # create dialog
    btn_false = MDFlatButton(text="CANCEL")
    btn_true = MDRaisedButton(text="DELETE COMPONENT")
    app.dialog = MDDialog(
        title="Delete Component",
        buttons=[btn_false, btn_true],
        text="Do you really want to delete the component with all its adherent connections?",
    )
    btn_false.bind(on_release=app.dialog.dismiss)
    btn_true.bind(on_release=lambda x: delete_selected_component(app))
    app.dialog.open()
