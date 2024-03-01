# IMPORTS
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

from factory_flexibility_model.ui.utility.GUI_logging import log_event
from factory_flexibility_model.ui.utility.window_handling import close_dialog


# CLASSES
class DialogSessionConfig(BoxLayout):
    pass


# FUNCTIONS
def save_session_config(app):
    """
    This function reads out the name, description, number of timesteps and slackcheckbox from the dialog_session
    config and writes into the blueprint.info of the session

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # read inputs from GUI and write them into app.blueprint.
    if app.dialog.content_cls.ids.checkbox_dollar.active:
        currency = "$"
    else:
        currency = "€"

    if app.dialog.content_cls.ids.checkbox_emission_limit.active:
        try:
            emission_limit = float(
                app.dialog.content_cls.ids.textfield_emission_limit.text
            )
        except:
            app.dialog.content_cls.ids.textfield_emission_limit.error = True
            return
    else:
        emission_limit = None

    if app.dialog.content_cls.ids.checkbox_emission_cost.active:
        try:
            emission_cost = float(
                app.dialog.content_cls.ids.textfield_emission_cost.text
            )
        except:
            app.dialog.content_cls.ids.textfield_emission_cost.error = True
            return
    else:
        emission_cost = None

    try:
        timesteps = int(app.dialog.content_cls.ids.textfield_session_timesteps.text)
    except:
        app.dialog.content_cls.ids.textfield_session_timesteps.error = True
        return

    try:
        timestep_length = float(
            app.dialog.content_cls.ids.textfield_session_timestep_length.text
        )
    except:
        app.dialog.content_cls.ids.textfield_session_timestep_length.error = True
        return

    app.blueprint.info = {
        "name": app.dialog.content_cls.ids.textfield_session_name.text,
        "description": app.dialog.content_cls.ids.textfield_session_description.text,
        "timesteps": timesteps,
        "timestep_length": timestep_length,
        "enable_slacks": app.dialog.content_cls.ids.checkbox_slack.active,
        "currency": currency,
        "emission_limit": emission_limit,
        "emission_cost": emission_cost,
    }

    # save the show component config dialog option
    app.session_data[
        "show_component_config_dialog_on_creation"
    ] = app.dialog.content_cls.ids.checkbox_config.active

    # write the new name into the top app bar
    app.root.ids.label_session_name.text = app.blueprint.info["name"]

    # close the dialog
    close_dialog(app)


def show_session_config_dialog(app):
    """
    This function opens the dialog to configure session name, decription and basic simulation parameters

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # abort if there is no session yet
    if app.session_data["session_path"] is None:
        # inform the user
        log_event(
            app,
            "Cannot set session configuration before initializing or importing a session!",
            "INFO",
            "User tried to open the session config menu without having a session loaded and got the following warning:",
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
    app.dialog.content_cls.ids.textfield_session_timestep_length.text = str(
        app.blueprint.info["timestep_length"]
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
    app.dialog.content_cls.ids.checkbox_config.active = app.session_data[
        "show_component_config_dialog_on_creation"
    ]

    # set emission cost gui element config
    if app.blueprint.info["emission_cost"] is None:
        app.dialog.content_cls.ids.checkbox_emission_cost.active = False
        app.dialog.content_cls.ids.textfield_emission_cost.disabled = True
    else:
        app.dialog.content_cls.ids.checkbox_emission_cost.active = True
        app.dialog.content_cls.ids.textfield_emission_cost.text = str(
            app.blueprint.info["emission_cost"]
        )
        app.dialog.content_cls.ids.textfield_emission_cost.disabled = False

    # set emission limit gui element config
    if app.blueprint.info["emission_limit"] is None:
        app.dialog.content_cls.ids.checkbox_emission_limit.active = False
        app.dialog.content_cls.ids.textfield_emission_limit.disabled = True
    else:
        app.dialog.content_cls.ids.checkbox_emission_limit.active = True
        app.dialog.content_cls.ids.textfield_emission_limit.text = str(
            app.blueprint.info["emission_limit"]
        )
        app.dialog.content_cls.ids.textfield_emission_limit.disabled = False

    # call toggle_currency method to display the correct hint text for the emission cost textfield
    toggle_currency(app)

    # bind callbacks to buttons
    btn_true.bind(on_release=lambda instance: save_session_config(app))
    btn_false.bind(on_release=lambda x: close_dialog(app))
    app.dialog.open()


def toggle_currency(app):
    """
    This function is activated when the user activates either the "€" or "$" checkbox within the session settings dialog. Everything the function does by now is to set the hint-text of the emission cost input textfield to correctly display the currency that the user selected.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """
    if app.dialog.content_cls.ids.checkbox_euro.active:
        app.dialog.content_cls.ids.textfield_emission_cost.hint_text = (
            "Set cost per kg of CO2 emitted [€/kgCO2]"
        )
    else:
        app.dialog.content_cls.ids.textfield_emission_cost.hint_text = (
            "Set cost per kg of CO2 emitted [$/kgCO2]"
        )


def toggle_emission_cost(app):
    """
    This function is activated when the user activated or deactivates the "set emission cost" checkbox within the session settings dialog. Everything the function does by now is to set the status of the corresponding input textfield to active/inactive in order to show the user if the current input value is being used for the somulation ore ignored.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """
    if app.dialog.content_cls.ids.checkbox_emission_cost.active:
        app.dialog.content_cls.ids.textfield_emission_cost.disabled = False
    else:
        app.dialog.content_cls.ids.textfield_emission_cost.disabled = True


def toggle_emission_limit(app):
    """
    This function is activated when the user activated or deactivates the "set emission limit" checkbox within the session settings dialog. Everything the function does by now is to set the status of the corresponding input textfield to active/inactive in order to show the user if the current input value is being used for the somulation ore ignored.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """
    if app.dialog.content_cls.ids.checkbox_emission_limit.active:
        app.dialog.content_cls.ids.textfield_emission_limit.disabled = False
    else:
        app.dialog.content_cls.ids.textfield_emission_limit.disabled = True
