# This file contains the function that creates and displays the dialog to specify name and path for a new session

# IMPORTS
import os
from tkinter import filedialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog


# CLASSES
class DialogNewSession(BoxLayout):
    pass


# FUNCTIONS
def show_new_session_dialog(app):
    """
    This function creates a new dialog within app.dialog. The Dialog Layout is taken from ui.gui_components.dialog_new_session.
    It contains all the input fields required for the user to specify name, path and description for the new session.
    If the user confirms the new session in the dialog, the function basic_session_functions.create_new_session()
    is being called.
    """

    from factory_flexibility_model.ui.gui_components.main_menu.basic_session_functions import (
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
    # initialize filepath textfield
    app.dialog.content_cls.ids.label_session_folder.text = rf"{os.getcwd()}\sessions"

    # bind callbacks to buttons
    btn_true.bind(on_release=lambda instance: create_new_session(app))
    btn_false.bind(on_release=app.dialog.dismiss)
    app.dialog.content_cls.ids.button_session_folder.bind(
        on_release=lambda instance: get_session_path(app)
    )
    app.dialog.content_cls.ids.label_session_folder.bind(
        on_release=lambda instance: get_session_path(app)
    )
    app.dialog.open()


def get_session_path(app):
    folder = filedialog.askdirectory()
    if folder:
        app.dialog.content_cls.ids.label_session_folder.text = folder
    else:
        app.dialog.content_cls.ids.label_session_folder.text = os.getcwd()
