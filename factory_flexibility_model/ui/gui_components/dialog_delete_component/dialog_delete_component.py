# IMPORTS
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

from factory_flexibility_model.ui.utility.delete_component import (
    delete_selected_component,
)

# FUNCTIONS


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
