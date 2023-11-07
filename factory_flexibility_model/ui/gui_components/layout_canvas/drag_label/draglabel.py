# IMPORTS
from kivy.uix.behaviors import DragBehavior
from kivy.properties import StringProperty
from kivy.uix.image import Image

# CLASSES
class DragLabel(DragBehavior, Image):
    id = StringProperty("")
    key = StringProperty("")
