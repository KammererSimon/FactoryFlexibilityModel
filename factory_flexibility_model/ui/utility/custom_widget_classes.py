# This file contains class definitions for all custom widget classes used within the GUI. They are required to take existing widgets and enhance them with custom layouts or behaviours

# IMPORTS
from kivy.graphics import Color
from kivy.properties import StringProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import (
    IRightBodyTouch,
    OneLineAvatarListItem,
    TwoLineAvatarListItem,
)
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.textfield import MDTextField


# CLASS DEFINITIONS
class DragLabel(DragBehavior, Image):
    id = StringProperty("")
    key = StringProperty("")


class ValidatedTextField(MDTextField):
    validation_type = ""  # specifies which input validation routine is performed when the user changes the text
    value_valid = True  # Is set to false when the user gave an invalid input


class dialog_connection_config(BoxLayout):
    pass


class dialog_flowtype_definition(BoxLayout):
    pass


class dialog_image_selection(BoxLayout):
    pass


class dialog_magnitude_definition(BoxLayout):
    pass


class dialog_new_component(BoxLayout):
    pass


class dialog_timeseries_selection(BoxLayout):
    pass


class dialog_unit_definition(BoxLayout):
    pass


class IconListItem(TwoLineAvatarListItem):
    icon = StringProperty()


class ImageDropDownItem(OneLineAvatarListItem):
    source = StringProperty()
    text = StringProperty()


class RightButton(IRightBodyTouch, MDRaisedButton):
    """Custom right container."""


class Tab(BoxLayout, MDTabsBase):
    pass


class CanvasWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            Color("#1D4276")
            Color(0.5, 0.3, 0.8, 1)

    def on_touch_up(self, touch):
        """
        This function identifies when the user clicken on the canvas without touching any objects. This is interpreted as thw wish to deselect any component and to return to the basis screen
        """
        if self.collide_point(*touch.pos):
            if not any(child.collide_point(*touch.pos) for child in self.children):
                app = MDApp.get_running_app()
                app.initiate_asset_selection(None)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
