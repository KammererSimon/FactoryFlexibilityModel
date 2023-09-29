# IMPORTS
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

# LAYOUTS
Builder.load_file(r"factory_flexibility_model\ui\dialogs\dialog_session_config.kv")

# CLASSES
class DialogSessionConfig(BoxLayout):
    pass


def show_session_config_dialog(app):
    """
    This function opens the dialog to configure session name, decription and basic simulation parameters
    """

    # abort if there is no session yet
    if app.session_data["session_path"] is None:
        app.show_info_popup(
            "Cannot set session configuration before initializing or importing a session!"
        )
        # close the component selection menu
        app.root.ids.component_shelf.set_state("closed")
        return

    # create buttons for the dialog
    btn_false = MDFlatButton(text="Cancel")
    btn_true = MDRaisedButton(text="Save")

    app.dialog = MDDialog(
        buttons=[btn_false, btn_true],
        type="custom",
        content_cls=DialogSessionConfig(),
        auto_dismiss=False,
    )

    # read data from the blueprint and add it to the GUI
    app.dialog.content_cls.ids.textfield_session_name.text = app.blueprint.info["name"]
    app.dialog.content_cls.ids.textfield_session_description.text = app.blueprint.info[
        "description"
    ]
    app.dialog.content_cls.ids.textfield_session_timesteps.text = str(
        app.blueprint.info["timesteps"]
    )
    if app.blueprint.info["currency"] == "€":
        app.dialog.content_cls.ids.checkbox_euro.active = True
        app.dialog.content_cls.ids.checkbox_dollar.active = False
    else:
        app.dialog.content_cls.ids.checkbox_euro.active = False
        app.dialog.content_cls.ids.checkbox_dollar.active = True

    app.dialog.content_cls.ids.checkbox_slack.active = app.blueprint.info[
        "enable_slacks"
    ]

    # bind callbacks to buttons
    btn_true.bind(on_release=lambda instance: save_session_config(app))
    btn_false.bind(on_release=app.dialog.dismiss)
    app.dialog.open()


def save_session_config(app):
    """
    This function reads out the name, description, number of timesteps and slackcheckbox from the dialog_session config and writes into the blueprint.info of the session
    """

    try:
        # read inputs from GUI and write them into app.blueprint.
        if app.dialog.content_cls.ids.checkbox_dollar.active:
            currency = "$"
        else:
            currency = "€"

        app.blueprint.info = {
            "name": app.dialog.content_cls.ids.textfield_session_name.text,
            "description": app.dialog.content_cls.ids.textfield_session_description.text,
            "timesteps": int(
                app.dialog.content_cls.ids.textfield_session_timesteps.text
            ),
            "enable_slacks": app.dialog.content_cls.ids.checkbox_slack.active,
            "currency": currency,
        }
        # write the new name into the top app bar
        app.root.ids.label_session_name.text = app.blueprint.info["name"]
        # close the dialog
        app.close_dialog()

    except:
        # if saving failed it is because there is no integer within the timesteps textfield
        app.dialog.content_cls.ids.textfield_session_timesteps.error = True
