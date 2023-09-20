from tkinter import filedialog

import numpy as np
import pandas as pd
from kivy_garden.graph import LinePlot
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.snackbar import Snackbar


def import_timeseries_xlsx(app):
    """
    This function lets the user choose an excel file containing timeseries and imports all of them to the tool
    """

    # ask for filename
    filetype = [("xlsx", "*.xlsx")]
    filepath = filedialog.askopenfilename(defaultextension=filetype, filetypes=filetype)

    if not filepath == "":
        # import the excel sheet
        app.timeseries = pd.read_excel(filepath, sheet_name="Timeseries")

        # update the list of available timeseries
        update_timeseries_list(app)

    # inform the user
    Snackbar(text=f"{len(app.timeseries.keys())} new timeseries imported").open()


def update_timeseries_list(app):
    # clear existing list
    app.root.ids.screen_timeseries.ids.list_timeseries.clear_widgets()
    # iterate over all imported timeseries
    for key in app.timeseries:

        # apply filter
        search_text = app.root.ids.screen_timeseries.ids.textfield_search.text
        if search_text.upper() not in key.upper():
            continue

        # create list item
        item = ThreeLineListItem(
            text=key,
            secondary_text=app.timeseries[key][0],
            tertiary_text=f"Timesteps: {app.timeseries[key][2:].notnull().sum()}",
            on_touch_down=lambda instance, touch: select_timeseries_list_item(
                app, instance, touch
            ),
        )

        # append item to list
        app.root.ids.screen_timeseries.ids.list_timeseries.add_widget(item)


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
    app.root.ids.screen_timeseries.ids.label_selected_timeseries.text = list_item.text

    # get data for selected timeseries and write it into self.selected_timeseries
    app.root.ids.screen_timeseries.selected_timeseries = list_item.text

    # update preview
    update_timeseries_preview(app)


def update_timeseries_preview(app):
    """
    This function creates a graph of a timeseries and hands it over to the preview canvas
    """

    graph = app.root.ids.screen_timeseries.ids.timeseries_preview

    for plot in list(graph.plots):
        graph.remove_plot(plot)
    # initialize the timeseries plot if not done yet
    timeseries_plot = LinePlot(color=app.main_color.get_rgba(), line_width=1)
    graph.add_plot(timeseries_plot)

    timeseries_data = np.array(
        app.timeseries[app.root.ids.screen_timeseries.selected_timeseries][
            1 : app.blueprint.info["timesteps"] + 1
        ]
    )

    # update plot points for the graph
    timeseries_plot.points = [(x, y) for x, y in enumerate(timeseries_data)]

    max_value = float(np.amax(timeseries_data))

    graph.xlabel = "Hours"

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

    # # set points depending on given user information
    # if value_type == "Static Value":
    #
    #     # if user wants a static value: just read out the value from gui
    #     value = float(self.root.ids.textfield_static_value.text)
    #     max_value = value
    #
    #     # update plot points for the graph
    #     self.selected_timeseries = (
    #         np.ones(self.selected_scenario["timesteps"]) * value
    #     )
    #     self.timeseries_plot.points = [
    #         (x, y) for x, y in enumerate(self.selected_timeseries)
    #     ]
    #     self.root.ids.timeseries_preview.ylabel = (
    #         self.root.ids.textfield_static_value_unit.text
    #     )
    #
    #     # update Y-axis_label:
    #     self.root.ids.timeseries_preview.ylabel = (
    #         self.root.ids.textfield_static_value_unit.text
    #     )

    # elif value_type == "Custom Timeseries":
    #     # if user wants a timeseries: take the currently selected timeseries and scale it as demanded
    #     if (
    #         self.root.ids.textfield_timeseries_scaling.text
    #         == "with a peak value of"
    #     ):
    #         # scale timeseries to given peak value
    #         self.selected_timeseries = (
    #             self.selected_timeseries
    #             / float(np.amax(self.selected_timeseries))
    #             * float(self.root.ids.textfield_custom_timeseries.text)
    #         )
    #
    #     elif (
    #         self.root.ids.textfield_timeseries_scaling.text
    #         == "with an average value of"
    #     ):
    #         # scale timeseries to given average value
    #         self.selected_timeseries = (
    #             self.selected_timeseries
    #             / np.mean(self.selected_timeseries)
    #             * float(self.root.ids.textfield_custom_timeseries.text)
    #         )
    #
    #     else:
    #         # scale timeseries to given integral value
    #         self.selected_timeseries = (
    #             self.selected_timeseries
    #             / np.sum(self.selected_timeseries)
    #             * float(self.root.ids.textfield_custom_timeseries.text)
    #         )

    # # update Y-axis_label:
    # self.root.ids.timeseries_preview.ylabel = (
    #     self.root.ids.textfield_custom_timeseries_unit.text
    # )
    #
    #     )
    # ]
