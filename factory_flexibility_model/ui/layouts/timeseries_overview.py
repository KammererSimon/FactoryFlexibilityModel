# IMPORTS
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

# LAYOUTS
Builder.load_file(r"factory_flexibility_model\ui\layouts\timeseries_overview.kv")

# CLASSES
class LayoutTimeseriesOverview(BoxLayout):
    selected_timeseries = StringProperty()
