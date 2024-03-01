# This script provides the function "log_event" which is being used as a general logging function for the gui. It is being called by almost any user interface function that processes some user input

# IMPORTS
import logging
from datetime import datetime

from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar.snackbar import MDSnackbar


# CODE START
def log_event(
    app, message: str, type: str, event_info: str = "", icon: str = None
) -> None:
    """
    This is a logging function for the GUI application.
    It is used instead of the default logging function to create a session-specific log to be stored with the session and to provide user feedback during runtime.

    :param app: The current Kivy application
    :param message: [str]The text describing the ocurring event
    :param type: [str; "DEBUG", "INFO", "ERROR"] The type of the Event that occured.
    :param event_info: [str] Additional information on the context of the event that is being stored in the log but not shown to the user during runtime.
    """

    if not type in ["DEBUG", "ERROR", "INFO"]:
        log_event(
            app, f"'Error during logging: {type}' is not a valid logging type!", "ERROR"
        )
        return

    # append event type and time to message:
    log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \t {type} \t {event_info} \t {message}"

    # select correct icon
    if icon is not None:
        pass
    elif type == "ERROR":
        icon = "alert"
    elif type == "DEBUG":
        icon = "chevron-right"
    elif type == "INFO":
        icon = "information-outline"

    # append new message to the log within session data
    app.session_data["log"].append(
        {
            "time": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "message": message,
            "event_info": event_info,
            "icon": icon,
            "type": type,
        }
    )

    # handover message to python logger if specified in config
    if app.config["log_logger"]:
        if type == "DEBUG":
            logging.debug(message)
        elif type == "INFO":
            logging.info(message)
        elif type == "ERROR":
            logging.error(message)

    # print message in console if specified in config
    if app.config["log_console"]:
        print(log_message)

    # Show user snackbar for info messages if specified in config
    if app.config["log_snackbar"] and type == "INFO":
        MDSnackbar(MDLabel(text=message)).open()

    # Show popup error message to the user in case of an error:
    if type == "ERROR":
        # create popup for the user
        btn_ok = MDRaisedButton(text="OK")
        app.popup = MDDialog(title="Warning", buttons=[btn_ok], text=message)
        btn_ok.bind(on_release=app.popup.dismiss)
        app.popup.open()
