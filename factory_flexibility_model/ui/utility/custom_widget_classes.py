# This file contains class definitions for all custom widget classes used within the GUI. They are required to take existing widgets and enhance them with custom layouts or behaviours

# IMPORTS
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import IRightBodyTouch, TwoLineAvatarListItem
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.textfield import MDTextField

# CLASS DEFINITIONS


class ValidatedTextField(MDTextField):
    validation_type = ""  # specifies which input validation routine is performed when the user changes the text
    value_valid = True  # Is set to false when the user gave an invalid input


# class dialog_connection_config(BoxLayout):
#     pass
#
# class dialog_magnitude_definition(BoxLayout):
#     pass
#
#
# class dialog_new_component(BoxLayout):
#     pass
#
#
# class dialog_timeseries_selection(BoxLayout):
#     pass
#
#
# class dialog_unit_definition(BoxLayout):
#     pass


class IconListItem(TwoLineAvatarListItem):
    icon = StringProperty()


class RightButton(IRightBodyTouch, MDRaisedButton):
    """Custom right container."""


class Tab(BoxLayout, MDTabsBase):
    pass
