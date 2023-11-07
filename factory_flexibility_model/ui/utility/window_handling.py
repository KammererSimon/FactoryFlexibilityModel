# IMPORTS
import ctypes
import platform

from kivymd.app import MDApp


# FUNCTIONS
def close_popup(app):
    """
    This function checks, if there is a popup window opened within app.popup.
    If yes, it calls the popup.dismiss() - command.

    :param app: Pointer to the current factory_GUIApp-instance
    :return: None
    """
    if app.popup is not None:
        app.popup.dismiss()


def close_dialog(app):
    """
    This function checks, if there is a dialog window opened within app.dialog.
    If yes, it calls the dialog.dismiss() - command.

    :param app: Pointer to the current factory_GUIApp-instance
    :return: None
    """
    if app.dialog is not None:
        app.dialog.dismiss()


def get_dpi():
    """
    This function uses the ctypes package to read out the dpi scaling that the user configured in his windows settings.
    This scaling is required to correctly adjust the flowgraphs created by the gui itself with the autoscaled UI elements from windows.

    :return: [int] DPI setting of windows. (100% size -> 96dpi; 125% size -> 120dpi; ...)
    """
    if platform.system() == "Windows":
        hdc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
        ctypes.windll.user32.ReleaseDC(0, hdc)
    else:
        dpi = 96

    return dpi


def resize_window(instance, width=0, height=0):
    """
    This function is called everytime that the user maximizes, minimizes, restores or resizes the window. It makes sure, that everything stays scaled in the correct way.

    :param instance: dummy parameter to make the function resiliant against bindings that hand over a varying number of positional standard parameters
    :param width: dummy parameter to make the function resiliant against bindings that hand over a varying number of positional standard parameters
    :param height: dummy parameter to make the function resiliant against bindings that hand over a varying number of positional standard parameters
    :return: None
    """

    from factory_flexibility_model.ui.gui_components.layout_canvas.factory_visualisation import (
        initialize_visualization,
    )

    app = MDApp.get_running_app()
    if app.session_data["session_active"]:
        initialize_visualization(app)
