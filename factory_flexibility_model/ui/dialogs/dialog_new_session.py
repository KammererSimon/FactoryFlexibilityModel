# This file contains the function that creates and displays the dialog to specify name and path for a new session

# IMPORTS
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

# LAYOUTS
Builder.load_file(r"factory_flexibility_model\ui\dialogs\dialog_new_session.kv")


# CLASSES
class DialogNewSession(BoxLayout):
    pass


# FUNCTIONS
def show_new_session_dialog(app):
    """
    This function creates a new dialog within app.dialog. The Dialog Layout is taken from ui.dialogs.dialog_new_session.
    It contains all the input fields required for the user to specify name, path and description for the new session.
    If the user confirms the new session in the dialog, the function basic_session_functions.create_new_session()
    is being called.
    """

    from factory_flexibility_model.ui.utility.basic_session_functions import (
        create_new_session,
    )

    # close the previous dialog
    if hasattr(app, "dialog"):
        if app.dialog is not None:
            app.dialog.dismiss()

    # create dialog
    btn_false = MDFlatButton(text="Cancel")
    btn_true = MDRaisedButton(text="Create new Session")
    app.dialog = MDDialog(
        title="New Session",
        buttons=[btn_false, btn_true],
        type="custom",
        content_cls=DialogNewSession(),
    )
    # bind callbacks to buttons
    btn_true.bind(on_release=lambda instance: create_new_session(app))
    btn_false.bind(on_release=app.dialog.dismiss)
    app.dialog.open()
