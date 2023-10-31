# IMPORTS
import numpy as np
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import LinePlot
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import IconLeftWidget, IconRightWidget, TwoLineAvatarIconListItem


# CLASSES
class DialogParameterConfig(BoxLayout):
    parameter = None
    unit = StringProperty()
    selected_timeseries = StringProperty()
    timeseries = ObjectProperty()


class PopupAddStaticValue(BoxLayout):
    pass


class PopupAddTimeseries(BoxLayout):
    pass


# FUNCTIONS
def add_static_parameter_value(app):
    """
    This function takes the value currently given by the user via the textfield_value and appends it to the parameter list of the component within app.session_data["parameters"]
    """

    # get the value to store
    value = app.popup.content_cls.ids.textfield_value.text

    # close popup
    app.popup.dismiss()

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

    # close popup
    app.popup.dismiss()

    # create a key to adress the variation
    variation = 0
    while variation in app.session_data["parameters"][asset_key][parameter_key].keys():
        variation += 1

    # store the value under the determined key
    app.session_data["parameters"][asset_key][parameter_key][variation] = {
        "type": "timeseries",
        "value": app.popup.selected_timeseries,
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


def delete_timeseries(app, timeseries_key):
    """
    This function deletes the timeseries referenced by timeseries_key from app.session_data["timeseries"]
    :param timeseries_key: [str] key to one of the items of app.session_data["timeseries"]
    """
    del app.session_data["timeseries"][timeseries_key]
    update_timeseries_list(app)


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
    app.popup.content_cls.ids.label_selected_timeseries.text = list_item.text

    # get data for selected timeseries and write it into self.selected_timeseries
    app.popup.selected_timeseries = list_item.text

    # write the values of the current timeseries into dialog.timeseries
    app.popup.timeseries = np.array(
        app.session_data["timeseries"][app.popup.selected_timeseries]["values"]
    )

    app.popup.content_cls.ids.button_add_timeseries.disabled = False

    # update preview
    update_timeseries_preview(app)


def show_parameter_config_dialog(app, caller):
    """
    This function opens the dialog for configuring values of component parameters.
    """

    app.dialog = MDDialog(
        title=f"{app.selected_asset['name']}: {caller.text}",
        type="custom",
        content_cls=DialogParameterConfig(),
    )
    app.dialog.size_hint = (None, None)
    app.dialog.width = dp(650)
    app.dialog.height = dp(900)

    app.dialog.parameter_description = f"{caller.value_description} [{caller.unit}]"

    # get the parameter to be configured with the opened dialog
    app.dialog.parameter = caller.parameter

    app.dialog.unit = caller.unit
    update_parameter_value_list(app)
    app.dialog.open()


def show_popup_add_static_value(app):
    """
    This function creates a new dialog within app.popup. The Dialog Layout is taken from ui.dialogs.dialog_add_static_value.kv.
    It contains a single input field  for the user to give a float input
    """

    # create popup

    app.popup = MDDialog(
        title="Static Value Definition",
        type="custom",
        content_cls=PopupAddStaticValue(),
    )

    app.popup.height = dp(200)
    app.popup.width = dp(500)
    app.popup.content_cls.ids.textfield_value.hint_text = (
        app.dialog.parameter_description
    )
    app.popup.open()


def show_popup_add_timeseries(app):
    """
    This function creates a new popup within app.dialog. The Popup Layout is taken from ui.dialogs.dialog_parameter_config.kv.
    It contains a list of imported timeseries and a preview graph for the currently selected timeseries
    """

    # create popup
    app.popup = MDDialog(
        title="Timeseries Selection",
        type="custom",
        content_cls=PopupAddTimeseries(),
    )

    app.popup.height = dp(800)
    app.popup.width = dp(1000)

    # initialize timeseries list
    update_timeseries_list(app)

    # open popup
    app.popup.open()


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
            secondary_text = f"{value['value']} {app.dialog.unit}"

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
    """
    This function updates the list showing all the currently available timeseries within the session.
    First the existing list in the gui is being cleared, then it is iterated over the
    list app.session_data["timeseries"] and all existing timeseries are added to the list
    """

    # if app.dialog is not None:
    # clear existing list
    app.popup.content_cls.ids.list_timeseries.clear_widgets()
    # iterate over all imported timeseries
    for key in app.session_data["timeseries"].keys():

        # apply filter
        search_text = app.popup.content_cls.ids.textfield_search.text
        if search_text.upper() not in key.upper():
            continue

        # create list item
        item = TwoLineAvatarIconListItem(
            IconLeftWidget(icon="chart-line"),
            IconRightWidget(
                icon="delete",
                on_release=lambda x, timeseries_key=key: delete_timeseries(
                    app, timeseries_key
                ),
            ),
            text=key,
            secondary_text=app.session_data["timeseries"][key]["description"],
            on_touch_down=lambda instance, touch: select_timeseries_list_item(
                app, instance, touch
            ),
        )

        # append item to list
        app.popup.content_cls.ids.list_timeseries.add_widget(item)


def update_timeseries_preview(app):
    """
    This function creates a graph of a timeseries and hands it over to the preview canvas together with some general info on the selected timeseries to be displayed within the info labels of the dialog.
    """

    # write timeseries characteristics into labels
    app.popup.content_cls.ids.label_value_max.text = (
        f"Maximum Value: {round(app.popup.timeseries.max(),2)} {app.dialog.unit}"
    )
    app.popup.content_cls.ids.label_value_min.text = (
        f"Minimum Value: {round(app.popup.timeseries.min(),2)} {app.dialog.unit}"
    )
    app.popup.content_cls.ids.label_value_avg.text = (
        f"Average Value: {round(app.popup.timeseries.mean(),2)} {app.dialog.unit}"
    )
    app.popup.content_cls.ids.label_timesteps.text = (
        f"Length: {app.popup.timeseries.shape[0]} Timesteps"
    )

    graph = app.popup.content_cls.ids.timeseries_preview

    for plot in list(graph.plots):
        graph.remove_plot(plot)
    # initialize the timeseries plot if not done yet
    timeseries_plot = LinePlot(color=app.main_color.get_rgba(), line_width=1)
    graph.add_plot(timeseries_plot)

    # update plot points for the graph
    timeseries_plot.points = [(x, y) for x, y in enumerate(app.popup.timeseries)]

    max_value = float(np.amax(app.popup.timeseries))

    graph.xlabel = "Hours"
    graph.ylabel = app.dialog.unit

    # set scaling of X-Axes
    if app.popup.timeseries.size < app.blueprint.info["timesteps"]:
        graph.xmax = app.popup.timeseries.size
    else:
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


def validate_value(app, textfield):
    """
    This function is called, when the user changes the value that is written in the static value input textfield within the corresponding popup.
    The function checks if the value is a valid numeric input and updates the graph on the right side of the dialog accordingly
    """

    app.popup.content_cls.ids.button_add_static_value.disabled = True
    # empty inputs do not have to be validated
    if textfield.text.strip() == "":
        textfield.text = ""
        textfield.error = True

        return

    # Make sure that the input is a number
    try:
        textfield.text = textfield.text.replace(",", ".").strip()
    except:
        if not textfield.text == "-":
            textfield.text = textfield.text[:-1]
            return

    textfield.error = False
    app.popup.content_cls.ids.button_add_static_value.disabled = False
