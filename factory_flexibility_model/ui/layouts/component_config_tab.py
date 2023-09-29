# IMPORTS
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

# LAYOUTS
Builder.load_file(r"factory_flexibility_model\ui\layouts\component_config_tab.kv")

# CLASSES
class layout_component_definition(BoxLayout):
    pass


class layout_component_configuration(BoxLayout):
    pass


class layout_converter_ratios(BoxLayout):
    pass


class layout_scheduler_demands(BoxLayout):
    pass
