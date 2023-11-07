# IMPORTS
from kivymd.uix.menu import MDDropdownMenu

from factory_flexibility_model.ui.utility.window_handling import close_popup


# FUNCTIONS
def set_text(caller, text, app):
    """
    This is a helper function that is used to write a user selected string from the flowtype_selection_dropdown to the target component.text.
    After the text has been handed over the dropdown menu is being closed.

    :param app: Pointer to the main factory_GUIApp-Object
    :param caller: Pointer to the gui component that called the flowtype dropdown menu in the first place
    :param text: [String] Name of the flowtype that the user has selected
    """
    # set selected text to caller.text
    caller.text = text

    # dismiss the dropdowp popup
    close_popup(app)


def show_flowtype_selection_dropdown(app, caller):
    """
    This function creates a dropdown menu giving the user the option to select one of the existing flowtypes.
    The dropdown is being created as a popup, positioned centrally under the component that it is being called from.
    The name of the selected flowtype is being set as text to the component that this function is being called from.

    :param app: Pointer to the main factory_GUIApp-Object
    :param caller: Pointer to the gui component that called the flowtype dropdown menu
    """

    # create list of dropdown items
    dropdown_items = [
        {
            "text": flowtype.name,
            "viewclass": "OneLineListItem",
            "on_release": lambda x=flowtype.name, app=app: set_text(caller, x, app),
        }
        for flowtype in app.blueprint.flowtypes.values()
    ]

    app.popup = MDDropdownMenu(caller=caller, items=dropdown_items, width_mult=4)
    app.popup.open()
