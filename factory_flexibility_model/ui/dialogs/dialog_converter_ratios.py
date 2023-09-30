# IMPORTS
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarIconListItem


# CLASSES
class dialog_converter_ratios(BoxLayout):
    bilance_valid = BooleanProperty()
    primary_flow = StringProperty()


class TextfieldIconListItem(TwoLineAvatarIconListItem):
    connection_key = StringProperty()


class TextfieldCheckboxIconListItem(TwoLineAvatarIconListItem):
    connection_key = StringProperty()


from factory_flexibility_model.ui.utility.converter_ratio_dialog_functions import (
    update_bilance_calculation,
    update_connection_lists,
)


# FUNCTIONS
def show_converter_ratio_dialog(app):
    """
    This function opens the dialog to specify converter input/output ratios.
    :param app: kivy-app-object that the dialog is being called from
    """

    app.dialog = MDDialog(
        title=f"{app.selected_asset['name']}: Input/Output Ratios",
        type="custom",
        content_cls=dialog_converter_ratios(),
        auto_dismiss=False,
    )

    app.dialog.size_hint = (None, None)
    app.dialog.width = dp(1050)
    app.dialog.height = dp(1000)
    app.dialog.primary_flow = app.selected_asset["GUI"]["primary_flow"]
    update_connection_lists(app)
    update_bilance_calculation(app)
    app.dialog.open()

def select_ratio_type(app, segmented_control, segmented_item):
    """
    This function is being called when the user uses the segmentedcontrol to switch between energy and materila rations.
    It switches the screen displayed in the bottom area of the dialog according to the users selection.
    :param app: pointer to the main GUI-object
    :param segmented_control: segmented control object -> unused
    :param segmented_item: item that the user clicked on -> is used to determine which screen to show
    """
    app.dialog.content_cls.ids.ratio_config_screens.current = segmented_item.text
