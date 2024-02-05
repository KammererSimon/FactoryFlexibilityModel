# IMPORTS
from collections import defaultdict

from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Triangle
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel

from factory_flexibility_model.ui.gui_components.layout_canvas.drag_label.draglabel import (
    DragLabel,
)
from factory_flexibility_model.ui.utility.window_handling import get_dpi


# CLASSES
class CanvasWidget(Widget):
    """
    This class defines the basic canvas widget
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # with self.canvas:
        #    Color("#1D4276")
        #    Color(0.5, 0.3, 0.8, 1)
        # TODO: delete this if it causes no harm to comment it ;)

    def on_touch_up(self, touch):
        """
        This function identifies when the user clicked on the canvas without touching any objects.
        This is interpreted as the wish to deselect any component and to return to the basic screen.

        When a click on the backgroudn of the canvas is being detected the initiate_asset_selection - function is called with None as parameter.


        :param touch: Touch event triggered when the user clicked on the canvas
        :return: None
        """
        if self.collide_point(*touch.pos):
            if not any(child.collide_point(*touch.pos) for child in self.children):
                app = MDApp.get_running_app()
                app.initiate_asset_selection(None)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# FUNCTIONS
def decrease_scaling_factor(app):
    """
    When called, this function decreses the size of all components within the layout visualisation by 5%.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # adjust scaling
    app.session_data["display_scaling_factor"] *= 0.95

    # redraw the visualisation with new scaling
    initialize_visualization(app)


def increase_scaling_factor(app):
    """
    When called, this function increases the size of all components within the layout visualisation by 5%.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # adjust scaling
    app.session_data["display_scaling_factor"] *= 1.05

    # redraw visualisation with new scaling
    initialize_visualization(app)


def initialize_visualization(app, *args):
    """
    This script builds the basic energy system visualisation out of the given blueprint on the Canvas within the system layout tab of the GUI

    :param app: Pointer to the main factory_GUIApp-Object
    :param args: Just a dummy to catch some additional parameters that might be handed over by lambda functions
    :return: None
    """

    # calculate the final scaling factor based on the user defined component size, window size and number of components
    scaling_factor = (
        app.session_data["display_scaling_factor"]
        * app.root.ids.canvas_layout.size[0]
        / 1000
        / (len(app.blueprint.components) + 1) ** app.config["display_scaling_exponent"]
    )

    # specify height of components in px. Standard is 100px, the blueprint provides an additional scaling factor
    component_height = 100 * scaling_factor

    # specify display widths of components in px depending on their type
    component_width = {
        "source": component_height,
        "sink": component_height,
        "pool": component_height,
        "storage": component_height * 1.5,
        "converter": component_height * 1.5,
        "deadtime": component_height * 1.5,
        "thermalsystem": component_height * 1.5,
        "triggerdemand": component_height * 1.5,
        "schedule": component_height * 1.5,
    }

    # specify canvas dimensions
    app.root.ids.canvas_layout.pos = app.root.ids.layout_area.pos
    app.root.ids.canvas_layout.size = app.root.ids.layout_area.size

    # store pointer to canvas to make following code better readable
    canvas = app.root.ids.canvas_layout.canvas

    # clear the canvas
    canvas.clear()

    # predefine lines for connections
    # TODO: This step is needed to have them at the background under the component labels
    #  ...change this if there is a better way to get this behaviour
    for connection in app.blueprint.connections.values():
        # get connection color from blueprint
        connection_color = connection["flowtype"].color.rgba

        # set line color
        canvas.add(
            Color(
                connection_color[0],
                connection_color[1],
                connection_color[2],
                connection_color[3],
            )
        )

        # create a new line object (with random points - they will be defined correctly later)
        new_line = Line(
            points=(0, 0, 1000, 1000),
            width=8 * app.session_data["display_scaling_factor"],
        )

        # place it on the canvas
        canvas.add(new_line)

        # inititalize small rectangles to display the directions of the flows
        # make them a little darker than the flow itself
        canvas.add(
            Color(
                connection_color[0] * 0.6,
                connection_color[1] * 0.6,
                connection_color[2] * 0.6,
                connection_color[3],
            )
        )
        pointer_start = Triangle(points=(0, 0, 0, 0, 0, 0))
        pointer_end = Triangle(points=(0, 0, 0, 0, 0, 0))
        canvas.add(pointer_start)
        canvas.add(pointer_end)

        # store pointer to line and rectangles in the app to make it adressable later
        app.root.ids[f"line_{connection['key']}"] = new_line
        app.root.ids[f"pointer_start_{connection['key']}"] = pointer_start
        app.root.ids[f"pointer_end_{connection['key']}"] = pointer_end

    # add a line to be used for connection preview while creating new connections
    canvas.add(Color(0.5, 0.5, 0.5, 1))
    new_line = Line(
        points=(-10, -10, -10, -10),
        width=8 * app.session_data["display_scaling_factor"],
    )
    canvas.add(new_line)
    app.root.ids[f"line_preview"] = new_line

    # add the new-connection-button
    new_connection_button = MDFillRoundFlatIconButton(
        icon="plus",
        text="Add connection",
        icon_size=20,
        pos=(800, 800),
        on_release=app.initiate_new_connection,
    )
    app.root.ids.canvas_layout.add_widget(new_connection_button)
    app.root.ids["new_connection"] = new_connection_button

    # add a label to highlight components
    highlight_label = Image()
    app.root.ids.canvas_layout.add_widget(highlight_label)
    app.root.ids["highlight"] = highlight_label
    app.root.ids["highlight"].pos = [
        -1000,
        -1000,
    ]  # move the highlight out of sight on startup

    # create assets according to the blueprint:
    for component in app.blueprint.components.values():
        # create draglabel.kv for the icon of the component
        component_framelabel = DragLabel(
            source=component["GUI"]["icon"],
            size=(component_width[component["type"]], component_height),
            id=component["key"],
        )
        # place it on the canvas and add it to the id-list of the application
        app.root.ids.canvas_layout.add_widget(component_framelabel)
        app.root.ids[f"frame_{component['key']}"] = component_framelabel

        # create a textlabel and place it on the canvas + add it to the id list
        component_textlabel = MDLabel(text=component["name"].upper(), halign="center")
        app.root.ids.canvas_layout.add_widget(component_textlabel)
        app.root.ids[f"text_{component['key']}"] = component_textlabel

        # assign the correct position to the new asset
        component_framelabel.pos = (
            app.root.ids.canvas_layout.pos[0]
            - component_width[component["type"]] / 2
            + (app.root.ids.canvas_layout.width - 100)
            * component["GUI"]["position_x"]
            / app.config["display_grid_size"][0]
            + 50,
            app.root.ids.canvas_layout.pos[1]
            - component_height / 2
            + (app.root.ids.canvas_layout.height - 100)
            * component["GUI"]["position_y"]
            / app.config["display_grid_size"][1]
            + 50,
        )

        # if the component is a pool: create a circle in the correct color
        if component["type"] == "pool":
            # exchange the icon with an empty one
            component_framelabel.source = app.config["assets"]["dummy"]
            # determine of the color of the pool
            if component["flowtype"].key == "unknown":
                canvas.add(Color(0.1137, 0.2588, 0.463, 1))
            else:
                pool_color = component["flowtype"].color.rgba
                canvas.add(
                    Color(pool_color[0], pool_color[1], pool_color[2], pool_color[3])
                )
            outer_circle = Ellipse(
                pos=(800, 800), size=(component_height, component_height)
            )
            canvas.add(outer_circle)

            # create a second circle to fill the middle
            canvas.add(Color(0.98, 0.98, 0.98, 1))
            inner_circle = Ellipse(
                pos=(820, 820),
                size=(
                    component_height - 32 * app.session_data["display_scaling_factor"],
                    component_height - 32 * app.session_data["display_scaling_factor"],
                ),
            )
            canvas.add(inner_circle)

            # give them IDs
            app.root.ids[f"outer_circle_{component['key']}"] = outer_circle
            app.root.ids[f"inner_circle_{component['key']}"] = inner_circle

            # place them correctly
            app.root.ids[
                f"outer_circle_{component['key']}"
            ].pos = component_framelabel.pos
            app.root.ids[f"inner_circle_{component['key']}"].pos = (
                component_framelabel.pos[0]
                + 16 * app.session_data["display_scaling_factor"],
                component_framelabel.pos[1]
                + 16 * app.session_data["display_scaling_factor"],
            )

    # assign callback to all icons to automatically refresh the visualisation once something was moved
    for component in app.blueprint.components.values():
        app.root.ids[f"frame_{component['key']}"].bind(
            on_touch_move=lambda x, y: update_visualization(app)
        )
        app.root.ids[f"frame_{component['key']}"].bind(
            on_touch_up=lambda touch, instance: app.click_on_component(touch, instance)
        )

    update_visualization(app)


def save_component_positions(app):
    """
    This function is called everytime when a component has been moven by the user within the layout visualisation.
    It checks the current positions of all components for deviations from their last known location.
    If a position deviates more than the expected rounding error the new position is stored in the blueprint
    """

    from factory_flexibility_model.ui.gui_components.dialog_delete_component.dialog_delete_component import (
        show_component_deletion_dialog,
    )

    # create a factor that determines the size of displayed components depending on the canvas size and the number
    # of elements to be displayed. The concrete function is try and error and my be changed during development
    scaling_factor = (
        app.session_data["display_scaling_factor"]
        * app.root.ids.canvas_layout.size[0]
        / 1000
        / (len(app.blueprint.components) + 1)
        ** (app.config["display_scaling_exponent"])
    )

    # specify size of the components depending on the determined scaling factor
    component_height = 100 * scaling_factor  # height in px

    # specify display widths of components in px depending on their type and the scaling factor
    component_width = {
        "source": component_height,
        "sink": component_height,
        "pool": component_height,
        "storage": component_height * 1.5,
        "converter": component_height * 1.5,
        "deadtime": component_height * 1.5,
        "thermalsystem": component_height * 1.5,
        "triggerdemand": component_height * 1.5,
        "schedule": component_height * 1.5,
    }

    # keep track if there had been any changes
    changes_done = False

    # iterate over all components
    for component in app.blueprint.components.values():
        # calculate the current relative position on the canvas for the component
        current_pos_x = round(
            (
                app.root.ids[f"frame_{component['key']}"].pos[0]
                - 50
                - app.root.ids.canvas_layout.pos[0]
                + component_width[component["type"]] / 2
            )
            / (app.root.ids.canvas_layout.width - 100)
            * app.config["display_grid_size"][0],
            0,
        )
        current_pos_y = round(
            (
                app.root.ids[f"frame_{component['key']}"].pos[1]
                - 50
                - app.root.ids.canvas_layout.pos[1]
                + component_height / 2
            )
            / (app.root.ids.canvas_layout.height - 100)
            * app.config["display_grid_size"][1],
            0,
        )

        # make sure that the new position is within the grid. If not: move tho component to the closest border
        if current_pos_x < 0:
            current_pos_x = 0
        if current_pos_x > app.config["display_grid_size"][0]:
            current_pos_x = app.config["display_grid_size"][0]
        if current_pos_y < 0:
            current_pos_y = 0
        if current_pos_y > app.config["display_grid_size"][1]:
            current_pos_y = app.config["display_grid_size"][1]

        # check, if window size is big enough to avoid rounding errors
        if (
            app.root.ids.canvas_layout.width > 800
            and app.root.ids.canvas_layout.height > 500
        ):

            # Check, if the component has been dragged on top of the recycle bin to delete it.
            if (
                app.root.ids[f"frame_{component['key']}"].pos[0]
                < app.root.ids.icon_delete_component.pos[0]
                + app.root.ids.icon_delete_component.size[0]
            ) and (
                app.root.ids[f"frame_{component['key']}"].pos[1]
                < app.root.ids.icon_delete_component.pos[1]
                + app.root.ids.icon_delete_component.size[1]
            ):
                # if yes: select the asset
                app.selected_asset = app.blueprint.components[component["key"]]

                # call deletion method
                show_component_deletion_dialog(app)

                update_visualization(app)

            else:
                # if x coordinate of the component has changed more than expected rounding error:
                if not current_pos_x - component["GUI"]["position_x"] == 0:
                    component["GUI"]["position_x"] = current_pos_x
                    changes_done = True

                # if y coordinate of the component has changed more than expected rounding error: store it
                if not current_pos_y - component["GUI"]["position_y"] == 0:
                    component["GUI"]["position_y"] = current_pos_y
                    changes_done = True

    # mark session as changed if changes have been done:
    if changes_done:
        app.unsaved_changes_on_session = True
        initialize_visualization(app)


def update_visualization(app, *args, **kwargs):
    """
    This function updates the position of connections and labels of the factory layout visualization.
    It is being called on startup once and everytime a component gets moved by the user.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # Specify a scaling factor depending on the size of the canvas and the number of components to be displayed
    # scaling factor = width_of_canvas / sqrt(number_of_components+1) / adjustment_factor
    scaling_factor = (
        app.session_data["display_scaling_factor"]
        * app.root.ids.canvas_layout.size[0]
        / 1000
        / (len(app.blueprint.components) + 1) ** app.config["display_scaling_exponent"]
    )

    # specify size of the components depending on the size of the canvas
    line_width = 7 * scaling_factor  # line width in px
    component_height = 100 * scaling_factor  # height in px

    # specify display widths of components in px depending on their type
    component_width = {
        "source": component_height,
        "sink": component_height,
        "pool": component_height,
        "storage": component_height * 1.5,
        "converter": component_height * 1.5,
        "deadtime": component_height * 1.5,
        "thermalsystem": component_height * 1.5,
        "triggerdemand": component_height * 1.5,
        "schedule": component_height * 1.5,
    }

    # specify canvas dimensions
    app.root.ids.canvas_layout.pos = app.root.ids.layout_area.pos
    app.root.ids.canvas_layout.size = app.root.ids.layout_area.size

    # store pointer to canvas to make following code better readable

    # create dataset with the incoming and outgoing connections per component, sorted by the direction
    # initialize a dict to store the information per direction
    connection_data = defaultdict(lambda: None)
    for component in app.blueprint.components:
        connection_data[component] = {
            "top": [],
            "bottom": [],
            "left": [],
            "right": [],
        }

    # iterate over all connections to determine the involved components and the directions
    connection_list = {}
    for connection in app.blueprint.connections.values():

        # initialize connection list for later (just to safe a loop)
        connection_list[connection["key"]] = {}

        # calculate distance between roots of source and destination on the canvas
        diff_x = (
            app.root.ids[f'frame_{connection["from"]}'].pos[0]
            - app.root.ids[f'frame_{connection["to"]}'].pos[0]
        )
        diff_y = (
            app.root.ids[f'frame_{connection["from"]}'].pos[1]
            - app.root.ids[f'frame_{connection["to"]}'].pos[1]
        )

        if abs(diff_x) > abs(diff_y) and diff_x < 0:
            # the origin is left of the destination -> Connection is mostly horizontal
            # connection must go from right of the source to left of the destination
            # -> Store key of connection in the direction-lists of the components + coordinate difference
            connection_data[connection["from"]]["right"].append(
                [diff_y / diff_x, connection["key"], "out"]
            )
            connection_data[connection["to"]]["left"].append(
                [-diff_y / diff_x, connection["key"], "in"]
            )

        elif diff_y > 0:
            # the origin is over the destination -> connection is mostly vertical and going downwards
            # connection must go from bottom of the origin to the top of the destination
            # -> Store key of connection in the direction-lists of the components + coordinate difference
            connection_data[connection["from"]]["bottom"].append(
                [-diff_x, connection["key"], "out"]
            )
            connection_data[connection["to"]]["top"].append(
                [diff_x, connection["key"], "in"]
            )

        elif diff_y <= 0:
            # the originis under the destination -> connection is mostly vertical and going upwards
            # connection must go from top of the origin to the bottom of the destination
            # -> Store key of connection in the direction-lists of the components + coordinate difference
            connection_data[connection["from"]]["top"].append(
                [-diff_x, connection["key"], "out"]
            )
            connection_data[connection["to"]]["bottom"].append(
                [diff_x, connection["key"], "in"]
            )

    # calculate how many connections are going in and out at every side of the components and sort them by the
    # relative coordinate difference to their origins/destinations to avoid crossings

    for component in connection_data.values():
        for direction in component:
            component[direction].sort(key=lambda x: x[0])

            i = 0
            number_of_connections = len(component[direction])
            for connection_end in component[direction]:
                # set the id of the current connection at the component
                i += 1

                # set the offset of the connections breaking points
                connection_list[connection_end[1]].update(
                    {"offset": (number_of_connections - 1) / 2 + 1 - i}
                )

                # define the connection as horizontal or vertical
                if direction == "left":
                    connection_list[connection_end[1]].update(
                        {"direction": "horizontal", "key": connection_end[1]}
                    )
                elif direction == "bottom":
                    connection_list[connection_end[1]].update(
                        {"direction": "vertical", "key": connection_end[1]}
                    )

                # get the component that the connection has to start/end from
                if connection_end[2] == "in":
                    act_component = app.blueprint.components[
                        app.blueprint.connections[connection_end[1]]["to"]
                    ]
                else:
                    act_component = app.blueprint.components[
                        app.blueprint.connections[connection_end[1]]["from"]
                    ]

                # determine the point where the current end of the connection has to be located
                if direction == "bottom":
                    point_x = (
                        app.root.ids[f'frame_{act_component["key"]}'].pos[0]
                        + component_width[act_component["type"]]
                        / (number_of_connections + 1)
                        * i
                    )
                    point_y = (
                        app.root.ids[f'frame_{act_component["key"]}'].pos[1]
                        + component_height / 2
                    )
                elif direction == "top":
                    point_x = (
                        app.root.ids[f'frame_{act_component["key"]}'].pos[0]
                        + component_width[act_component["type"]]
                        / (number_of_connections + 1)
                        * i
                    )
                    point_y = (
                        app.root.ids[f'frame_{act_component["key"]}'].pos[1]
                        + component_height / 2
                    )
                elif direction == "left":
                    point_x = (
                        app.root.ids[f'frame_{act_component["key"]}'].pos[0]
                        + component_width[act_component["type"]] / 2
                    )
                    point_y = (
                        app.root.ids[f'frame_{act_component["key"]}'].pos[1]
                        + component_height / (number_of_connections + 1) * i
                    )
                elif direction == "right":
                    point_x = (
                        app.root.ids[f'frame_{act_component["key"]}'].pos[0]
                        + component_width[act_component["type"]] / 2
                    )
                    point_y = (
                        app.root.ids[f'frame_{act_component["key"]}'].pos[1]
                        + component_height / (number_of_connections + 1) * i
                    )

                if connection_end[2] == "out":
                    connection_list[connection_end[1]].update(
                        {"start_x": point_x, "start_y": point_y}
                    )
                else:
                    connection_list[connection_end[1]].update(
                        {"end_x": point_x, "end_y": point_y}
                    )

    # finally: go over the list of connections again and plot the lines!
    for connection in connection_list.values():
        # adjust the line width
        app.root.ids[f"line_{connection['key']}"].width = line_width

        # check, which type of connection has to be created:
        if connection["direction"] == "horizontal":
            app.root.ids[f"line_{connection['key']}"].points = (
                connection["start_x"],
                connection["start_y"],
                connection["start_x"]
                + (connection["end_x"] - connection["start_x"]) / 2
                + connection["offset"] * line_width * 3,
                connection["start_y"],
                connection["start_x"]
                + (connection["end_x"] - connection["start_x"]) / 2
                + connection["offset"] * line_width * 3,
                connection["end_y"],
                connection["end_x"],
                connection["end_y"],
            )

            # get the widths of destination and origin component
            source_width = component_width[
                app.blueprint.components[
                    app.blueprint.connections[connection["key"]]["from"]
                ]["type"]
            ]
            sink_width = component_width[
                app.blueprint.components[
                    app.blueprint.connections[connection["key"]]["to"]
                ]["type"]
            ]

            # adjust the points of the two triangles to form nice arrows at the beginning and end of the connection
            app.root.ids[f"pointer_start_{connection['key']}"].points = (
                connection["start_x"] + source_width / 2 + line_width,
                connection["start_y"] - line_width * 0.8,
                connection["start_x"] + source_width / 2 + line_width,
                connection["start_y"] + line_width * 0.8,
                connection["start_x"] + source_width / 2 + line_width * 2,
                connection["start_y"],
            )
            app.root.ids[f"pointer_end_{connection['key']}"].points = (
                connection["end_x"] - sink_width / 2 - line_width * 2,
                connection["end_y"] + line_width * 0.8,
                connection["end_x"] - sink_width / 2 - line_width * 2,
                connection["end_y"] - line_width * 0.8,
                connection["end_x"] - sink_width / 2 - line_width,
                connection["end_y"],
            )
        else:
            app.root.ids[f"line_{connection['key']}"].points = (
                connection["start_x"],
                connection["start_y"],
                connection["start_x"],
                connection["start_y"]
                + (connection["end_y"] - connection["start_y"]) / 2
                + connection["offset"] * line_width * 3,
                connection["end_x"],
                connection["start_y"]
                + (connection["end_y"] - connection["start_y"]) / 2
                + connection["offset"] * line_width * 3,
                connection["end_x"],
                connection["end_y"],
            )

            if connection["start_y"] > connection["end_y"]:
                # adjust the points of the two triangles to form nice arrows at the beginning and end of the connection
                app.root.ids[f"pointer_start_{connection['key']}"].points = (
                    connection["start_x"] - line_width * 0.8,
                    connection["start_y"] - component_height / 2 - line_width,
                    connection["start_x"] + line_width * 0.8,
                    connection["start_y"] - component_height / 2 - line_width,
                    connection["start_x"],
                    connection["start_y"] - component_height / 2 - line_width * 2,
                )
                app.root.ids[f"pointer_end_{connection['key']}"].points = (
                    connection["end_x"] - line_width * 0.8,
                    connection["end_y"] + component_height / 2 + line_width * 2,
                    connection["end_x"] + line_width * 0.8,
                    connection["end_y"] + component_height / 2 + line_width * 2,
                    connection["end_x"],
                    connection["end_y"] + component_height / 2 + line_width,
                )
            else:
                # adjust the points of the two triangles to form nice arrows at the beginning and end of the connection
                app.root.ids[f"pointer_start_{connection['key']}"].points = (
                    connection["start_x"] - line_width * 0.8,
                    connection["start_y"] + component_height / 2 + line_width,
                    connection["start_x"] + line_width * 0.8,
                    connection["start_y"] + component_height / 2 + line_width,
                    connection["start_x"],
                    connection["start_y"] + component_height / 2 + line_width * 2,
                )
                app.root.ids[f"pointer_end_{connection['key']}"].points = (
                    connection["end_x"] - line_width * 0.8,
                    connection["end_y"] - component_height / 2 - line_width * 2,
                    connection["end_x"] + line_width * 0.8,
                    connection["end_y"] - component_height / 2 - line_width * 2,
                    connection["end_x"],
                    connection["end_y"] - component_height / 2 - line_width,
                )

    # iterate over all components
    for component in app.blueprint.components.values():
        # set the positions for the labels and icons
        app.root.ids[f"text_{component['key']}"].pos = (
            app.root.ids[f"frame_{component['key']}"].pos[0]
            - component_width[component["type"]] * 0.5,
            app.root.ids[f"frame_{component['key']}"].pos[1]
            - component_height * 0.45
            - 30,
        )

        # set the font size of labels
        app.root.ids[f"text_{component['key']}"].font_size = 18 * scaling_factor

        # set the size of the components
        app.root.ids[f"frame_{component['key']}"].size = (
            component_width[component["type"]],
            component_height,
        )
        app.root.ids[f"text_{component['key']}"].size = (
            component_width[component["type"]] * 2,
            100,
        )

        # pools need their circles adjusted
        if component["type"] == "pool":
            # adjust position of circles
            app.root.ids[f"outer_circle_{component['key']}"].pos = app.root.ids[
                f"frame_{component['key']}"
            ].pos
            app.root.ids[f"inner_circle_{component['key']}"].pos = (
                app.root.ids[f"frame_{component['key']}"].pos[0] + 2 * line_width,
                app.root.ids[f"frame_{component['key']}"].pos[1] + 2 * line_width,
            )
            # adjust size of circles
            app.root.ids[f"outer_circle_{component['key']}"].size = (
                component_height,
                component_height,
            )
            app.root.ids[f"inner_circle_{component['key']}"].size = (
                component_height - 4 * line_width,
                component_height - 4 * line_width,
            )

    # highlight the selected component
    if (
        app.selected_asset == None
        or app.selected_asset == ""
        or app.selected_asset["type"] == "energy"
        or app.selected_asset["type"] == "material"
        or app.selected_asset["type"] == "connection"
    ):
        #  if the user selected a flow, a connection or no component at all: move the highlight image out of sight
        app.root.ids["highlight"].pos = [-1000, -1000]

    else:
        # choose the correct highlight asset:
        app.root.ids["highlight"].source = app.config["assets"]["highlights"][
            app.selected_asset["type"]
        ]
        # adjust it in size
        app.root.ids["highlight"].size = [
            component_width[app.selected_asset["type"]] * 2,
            component_height * 2,
        ]
        # place it behind the selected component
        app.root.ids["highlight"].pos = [
            app.root.ids[f"frame_{app.selected_asset['key']}"].pos[0]
            - component_width[app.selected_asset["type"]] / 2,
            app.root.ids[f"frame_{app.selected_asset['key']}"].pos[1]
            - component_height / 2,
        ]

    # place "new connection" button
    if (
        app.selected_asset == None
        or app.selected_asset == ""
        or app.selected_asset["type"] == "energy"
        or app.selected_asset["type"] == "material"
        or app.selected_asset["type"] == "connection"
        or app.selected_asset["type"] == "sink"
        or len(app.blueprint.components) < 2
    ):
        app.root.ids["new_connection"].pos = [-1000, -1000]
    else:
        app.root.ids["new_connection"].pos = [
            app.root.ids[f"frame_{app.selected_asset['key']}"].pos[0]
            + component_width[app.selected_asset["type"]],
            app.root.ids[f"frame_{app.selected_asset['key']}"].pos[1]
            + component_height,
        ]

    if app.connection_edit_mode:
        if "mouse_pos" in kwargs:
            window_height, window_width = Window.size
            canvas_height, canvas_width = app.root.ids.canvas_layout.size
            canvas_y, canvas_x = app.root.ids.canvas_layout.pos
            end_x = (kwargs["mouse_pos"][0]) * get_dpi() / 96
            end_y = (kwargs["mouse_pos"][1] - 65) * get_dpi() / 96
            app.root.ids[f"line_preview"].points = (
                app.root.ids[f"frame_{app.selected_asset['key']}"].pos[0]
                + component_width[app.selected_asset["type"]] / 2,
                app.root.ids[f"frame_{app.selected_asset['key']}"].pos[1]
                + component_height / 2,
                end_x,
                end_y,
            )
