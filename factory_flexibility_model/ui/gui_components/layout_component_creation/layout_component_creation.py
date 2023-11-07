# IMPORTS
import ast
import yaml
from factory_flexibility_model.ui.gui_components.layout_canvas.drag_label.draglabel import DragLabel
from factory_flexibility_model.ui.utility.io.import_config_files import get_component_dummies

# FUNCTIONS
def show_component_creation_menu(app):
    """
    This function creates the draggable component dummys within the component creation menu that appears when the user clicks on the big + on the left of the main screen.
    The function reads in the file ui\\utility\\config_files\\component_dummies.txt, which contains all the required information on which components to offer to the user and with which icons to preview them.
    For every component type a DragLabel-Component is being created and configured with the corresponding information and asset.
    The script then divides the available space within the canvas of the menu equally to the rewuired number of rows, scales the DragLabels accordingly and places them on the canvas.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # import list with components to display. Every component contains a key, an id and a path to a preview icon
    component_dummies = get_component_dummies()

    # get available height of the component canvas
    canvas_height = app.root.ids.canvas_shelf.size[1]
    canvas_width = app.root.ids.canvas_shelf.size[0]

    # calculate height for components
    component_height = canvas_height / (len(component_dummies) + 3)
    component_pos_x = (canvas_width - component_height * 1.5) / 2

    # clear component dummy canvas
    app.root.ids.canvas_shelf.canvas.clear()

    # iterate over all specified dummys and create them
    i = 0
    for type in component_dummies:
        # create draglabel.kv for the icon of the component
        component_dummy = DragLabel(
            source=component_dummies[type]["source"],
            id=component_dummies[type]["id"],
            key=type,
            on_touch_up=lambda touch, instance: app.add_component(touch, instance),
        )
        component_dummy.pos = (
            component_pos_x + component_height * 0.25,
            canvas_height / len(component_dummies) * i + canvas_height * 0.15,
        )
        component_dummy.size = (component_height * 1.5, component_height)
        app.root.ids.canvas_shelf.add_widget(component_dummy)
        i += 1

    # show the component shelf
    app.root.ids.component_shelf.set_state("open")
