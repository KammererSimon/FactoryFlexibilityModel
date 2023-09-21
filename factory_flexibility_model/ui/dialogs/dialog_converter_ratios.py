# IMPORTS
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarIconListItem


# CLASSES
class dialog_converter_ratios(BoxLayout):
    bilance_valid = BooleanProperty()


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
    update_connection_lists(app)
    update_bilance_calculation(app)
    app.dialog.open()
