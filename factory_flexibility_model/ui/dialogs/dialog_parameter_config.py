# IMPORTS
import numpy as np
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import LinePlot
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import (
    IconLeftWidget,
    IconRightWidget,
    TwoLineAvatarIconListItem,
    TwoLineListItem,
)


# CLASSES
class dialog_parameter_config(BoxLayout):
    parameter = None
    unit = StringProperty()
    selected_timeseries = StringProperty()
    timeseries = ObjectProperty()


# FUNCTIONS
def show_parameter_config_dialog(app, caller):
    """
    This function opens the dialog for configuring values of component parameters.
    """

    app.dialog = MDDialog(
        title=f"{app.selected_asset['name']}: {caller.text}",
        type="custom",
        content_cls=dialog_parameter_config(),
    )

    app.dialog.size_hint = (None, None)
    app.dialog.width = dp(1500)
    app.dialog.height = dp(900)

    app.dialog.unit = app.selected_asset["flowtype"].unit.get_unit_flowrate()

    app.dialog.parameter = caller.parameter
    app.dialog.content_cls.ids.textfield_value.hint_text = (
        f"{caller.value_description} [{app.dialog.unit}]"
    )

    update_timeseries_list(app)
    update_parameter_value_list(app)
    app.dialog.open()


def select_parameter_type(app, segmented_control, segmented_item):
    """
    This function is being called when the user uses the segmentedcontrol to switch between static values and timeseries data.
    It switches the screen displayed in the left area of the dialog according to the users selection.
    :param app: pointer to the main GUI-object
    :param segmented_control: segmented control object -> unused
    :param segmented_item: item that the user clicked on -> is used to determine which screen to show
    """
    app.dialog.content_cls.ids.parameter_type_screens.current = segmented_item.text


def add_static_parameter_value(app):
    """
    this function takes the value currently given by the user via the textfield_value and appends it to the parameter list of the component within app.session_data["parameters"]
    """
    # get the value to store
    value = app.dialog.content_cls.ids.textfield_value.text

    # get the asset and parameter keys
    asset_key = app.selected_asset["key"]
    parameter_key = app.dialog.parameter

    # create a key to adress the variation
    variation = 0
    while variation in app.session_data["parameters"][asset_key][parameter_key].keys():
        variation += 1

    # store the value under the determined key
    app.session_data["parameters"][asset_key][parameter_key][variation] = {
        "type": "static",
        "value": value,
    }

    update_parameter_value_list(app)


def add_timeseries_parameter_value(app):
    """
    This function takes the timeseries currently selected by the user and appends it to the parameter list of the component within app.session_data["parameters"]
    """

    # get the asset and parameter keys
    asset_key = app.selected_asset["key"]
    parameter_key = app.dialog.parameter

    # create a key to adress the variation
    variation = 0
    while variation in app.session_data["parameters"][asset_key][parameter_key].keys():
        variation += 1

    # store the value under the determined key
    app.session_data["parameters"][asset_key][parameter_key][variation] = {
        "type": "timeseries",
        "value": app.dialog.selected_timeseries,
    }

    update_parameter_value_list(app)


def delete_parameter_value(app, value_key):
    """
    This function takes a pointer to a currently running app and a key to one of the values in the currently opened parametervalue definitiondialog. It deletes the referenced parameter from the app.session_data["parameters"] dict and refreshes the value list in the dialog.
    :param app: Pointer to the currently running app instance
    :param value_key: [str] Key to one value within the parameterlist of the selected asset
    :return: true
    """
    del app.session_data["parameters"][app.selected_asset["key"]][app.dialog.parameter][
        value_key
    ]
    update_parameter_value_list(app)


def update_parameter_value_list(app):
    """
    This function updates the entries within the list of user specified parameters on the parameter_config_dialog.
    It reads out all the entries from app.session_data["parameters"][selected component] and generates a set of iconlistitems out of them.
    """

    # get the key of the currently defined parameter
    parameter = app.dialog.parameter

    # clear the current list
    app.dialog.content_cls.ids.list_parameter_variations.clear_widgets()

    # if no value for the parameter has been defined yet: create an empty dict and abort
    if (
        parameter
        not in app.session_data["parameters"][app.selected_asset["key"]].keys()
    ):
        app.session_data["parameters"][app.selected_asset["key"]][parameter] = {}
        return

    # iterate over all currently specified values for the component and parameter
    for variation, value in app.session_data["parameters"][app.selected_asset["key"]][
        parameter
    ].items():

        # define list entry depending on the kind of value that is being handled
        if value["type"] == "timeseries":
            text = "Timeseries"
            secondary_text = value["value"]
            icon = "chart-line"
        else:
            text = "Static Value"
            icon = "numeric"
            secondary_text = f"{value['value']} {app.selected_asset['flowtype'].unit.get_unit_flowrate()}"

        # create a list item with the current value
        item = TwoLineAvatarIconListItem(
            IconLeftWidget(icon=icon),
            IconRightWidget(
                icon="delete",
                on_release=lambda x, value_key=variation: delete_parameter_value(
                    app, value_key
                ),
            ),
            text=text,
            secondary_text=secondary_text,
        )
        # add list item to the value list
        app.dialog.content_cls.ids.list_parameter_variations.add_widget(item)


def update_timeseries_list(app):
    # if app.dialog is not None:
    # clear existing list
    app.dialog.content_cls.ids.list_timeseries.clear_widgets()
    # iterate over all imported timeseries
    for key in app.timeseries:

        # apply filter
        search_text = app.dialog.content_cls.ids.textfield_search.text
        if search_text.upper() not in key.upper():
            continue

        # create list item
        item = TwoLineListItem(
            text=key,
            secondary_text=app.timeseries[key][0],
            on_touch_down=lambda instance, touch: select_timeseries_list_item(
                app, instance, touch
            ),
        )

        # append item to list
        app.dialog.content_cls.ids.list_timeseries.add_widget(item)


def select_timeseries_list_item(app, list_item, touch):
    """
    This function is called everytime when the user selects a timeseries in the scenarioparameter definition.
    The selected timeseries is displayed in the preview window
    """

    # check, if the function call actually came from an object that has been clicked/moved
    if not list_item.collide_point(*touch.pos):
        # abort if not
        return

    # write the name of selected timeseries in the GUI
    app.dialog.content_cls.ids.label_selected_timeseries.text = list_item.text

    # get data for selected timeseries and write it into self.selected_timeseries
    app.dialog.selected_timeseries = list_item.text

    # update preview
    update_timeseries_preview(app)


def update_timeseries_preview(app):
    """
    This function creates a graph of a timeseries and hands it over to the preview canvas
    """

    # get values
    app.dialog.timeseries = np.array(
        app.timeseries[app.dialog.selected_timeseries][
            1 : app.blueprint.info["timesteps"] + 1
        ]
    )

    # write timeseries characteristics into labels
    app.dialog.content_cls.ids.label_value_max.text = (
        f"Max: {round(app.dialog.timeseries.max(),2)} {app.dialog.unit}"
    )
    app.dialog.content_cls.ids.label_value_min.text = (
        f"Min: {round(app.dialog.timeseries.min(),2)} {app.dialog.unit}"
    )
    app.dialog.content_cls.ids.label_value_avg.text = (
        f"Avg: {round(app.dialog.timeseries.mean(),2)} {app.dialog.unit}"
    )
    app.dialog.content_cls.ids.label_timesteps.text = (
        f"Length: {app.dialog.timeseries.shape[0]} Timesteps"
    )

    graph = app.dialog.content_cls.ids.timeseries_preview

    for plot in list(graph.plots):
        graph.remove_plot(plot)
    # initialize the timeseries plot if not done yet
    timeseries_plot = LinePlot(color=app.main_color.get_rgba(), line_width=1)
    graph.add_plot(timeseries_plot)

    # update plot points for the graph
    timeseries_plot.points = [(x, y) for x, y in enumerate(app.dialog.timeseries)]

    max_value = float(np.amax(app.dialog.timeseries))

    graph.xlabel = "Hours"
    graph.ylabel = app.dialog.unit

    # set scaling of X-Axes
    graph.xmax = app.blueprint.info["timesteps"]
    graph.xmin = 0
    graph.x_ticks_major = 24

    # set scaling of Y-Axes
    graph.ymin = 0
    if max_value == 0:
        graph.ymax = 1
        graph.y_ticks_major = 0.2
    else:
        # determine dimension of value
        x = max_value
        i = 0
        while x > 1:
            x = x / 10
            i += 1

        # set y scale of graph
        graph.ymax = 10**i * round(x + 0.1, 1)

        graph.y_ticks_major = 10**i / 5
