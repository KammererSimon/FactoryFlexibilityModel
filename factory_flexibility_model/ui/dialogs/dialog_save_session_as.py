# This file contains the function that creates and displays the dialog to specify a new name and path for an existing

# IMPORTS
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog


# CLASSES
class DialogSaveSessionAs(BoxLayout):
    pass


# FUNCTIONS
def show_dialog_save_session_as(app):
    """
    This function creates a new dialog within app.dialog. The Dialog layout is taken from ui.dialogs.dialog_save_session_as.
    It contains all the input fields required for the user to specify a new name, path and description for the session.
    If the user confirms the new session in the dialog, the function basic_session_functions.update_session_path()
    is being called.
    """

    from factory_flexibility_model.ui.utility.basic_session_functions import (
        save_session_as,
    )

    # close the previous dialog
    if hasattr(app, "dialog"):
        if app.dialog is not None:
            app.dialog.dismiss()

    # create dialog
    btn_false = MDFlatButton(text="Cancel")
    btn_true = MDRaisedButton(text="Create copy of the session")
    app.dialog = MDDialog(
        title="Save session as",
        buttons=[btn_false, btn_true],
        type="custom",
        content_cls=DialogSaveSessionAs(),
    )
    # bind callbacks to buttons
    btn_true.bind(on_release=lambda instance: save_session_as(app))
    btn_false.bind(on_release=app.dialog.dismiss)
    app.dialog.open()
