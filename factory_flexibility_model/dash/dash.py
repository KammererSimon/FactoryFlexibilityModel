"""
This module contains the result dashboard that can be used to show and analyze the results of a solved simulation.
It consists of a single function "create_dash", which takes a solved simulation object as input and uses the plotly dash library to create an interactive browserbased dashboard.

Usage:
------
1. Create a factory layout, solve the simulation

2. Call the `create_dash()`_ function and hand over the solved `Simulation`_ object

3. After some preprocessing the function will provide you with an ip where the dashboard is being hosted in realtime. Click this link to open your browser and view the results

4. The function stays active providing the backbone for the interactive dashboard until the execution is canceled

.. image:: _static/dashboard_illustration.png
"""


# IMPORT 3RD PARTY PACKAGES
import copy
import warnings

import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc
from dash_bootstrap_templates import load_figure_template
from plotly.express.colors import sample_colorscale
from plotly.subplots import make_subplots
from dash_auth import BasicAuth

from factory_flexibility_model.dash.dash_functions.create_cost_overview import (
    create_cost_overview,
)
from factory_flexibility_model.dash.dash_functions.create_emission_overview import (
    create_emission_overview,
)
from factory_flexibility_model.dash.dash_functions.create_layout_html import (
    create_layout_html,
)


# CODE START
def create_dash(simulation, authentication: None):
    """
    .. _create_dash():
    This function takes a solved simulation object and creates an interactive browserbased dashboard.

    :param simulation: Simulation - Object.
    :param: authentication: [dict]: a dict of combinations of usernames and passwords that are valid to access the dashboard
    :return: Nothing. The script ends with providing a dashboard on an internal server and goes into a loop to process user inputs within the dashboard until it is being cancelled externally.
    """

    # Check, that Simulation has been performed and results are existing
    if not simulation.simulated:
        warnings.warn(
            "Scenario has not been simulated yet. Calling the Simulation routine... If you want to execute it with specific parameters do it before calling the show_results-function)"
        )
        simulation.simulate()

    # TODO: Separate the next section into a config file!
    # INITIALIZE APP AND SET LAYOUT
    app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

    if authentication is not None:
        BasicAuth(app, authentication)

    load_figure_template("FLATLY")
    colors = {
        "main": (29, 66, 118),
        "second": (120, 120, 120),
        "card": (255, 255, 255),
        "text_dark": (156, 156, 156),
        "text_light": (250, 250, 250),
        "background": (240, 240, 240),
        "scale_brightness": [
            (0, 0, 0),
            (13, 24, 33),
            (24, 42, 59),
            (34, 60, 83),
            (49, 86, 119),
            (29, 66, 118),
            (86, 138, 184),
            (122, 163, 199),
            (158, 189, 215),
            (194, 213, 230),
            (255, 255, 255),
        ],
        "scale_saturation": [
            (0, 84, 156),
            (39, 13, 156),
            (78, 119, 156),
            (117, 137, 156),
            (156, 156, 156),
        ],
    }
    main_font = "helvetica"  # akkurat-light"
    plot_font = "helvetica"
    style = {
        "overflow": "hidden",
        "background": "#%02x%02x%02x" % colors["background"],
        "card_color": "#%02x%02x%02x" % colors["card"],
        "card_color_dark": "#%02x%02x%02x" % colors["scale_brightness"][5],
        "main_color": "#%02x%02x%02x" % colors["main"],
        "main_color_rgb": f"rgb{colors['main']}",
        "second_color": "#%02x%02x%02x" % colors["second"],
        "second_color_rgb": f"rgb{colors['second']}",
        "text": "#%02x%02x%02x" % colors["text_dark"],
        "font": main_font,
        "plot_font": plot_font,
        "axis_color": "grey",
        "grid_color": "lightgrey",
        "diagram_title_size": 30,
        "H1": {
            "marginTop": "30px",
            "marginBottom": "30px",
            "textAlign": "center",
            "color": "#%02x%02x%02x" % colors["main"],
            "font-family": main_font,
        },
        "H2": {
            "marginLeft": "10px",
            "marginTop": "5px",
            "marginBottom": "0px",
            "textAlign": "left",
            "color": "#%02x%02x%02x" % colors["scale_brightness"][9],
            "font-family": main_font,
        },
        "H3": {
            "marginLeft": "10px",
            "marginTop": "10px",
            "marginBottom": "10px",
            "textAlign": "center",
            "color": colors["second"],
            "font-family": main_font,
        },
        "card_title": {
            "marginLeft": "5px",
            "marginTop": "10px",
            "marginBottom": "5px",
            "textAlign": "left",
            "color": "#%02x%02x%02x" % colors["second"],
            "font-family": plot_font,
        },
        "card_title_contrast": {
            "marginLeft": "10px",
            "marginTop": "20px",
            "marginBottom": "0px",
            "textAlign": "left",
            "color": "#%02x%02x%02x" % colors["text_light"],
            "font-family": main_font,
        },
        "value_description": {
            "marginLeft": "10px",
            "marginTop": "0px",
            "marginBottom": "0px",
            "textAlign": "center",
            "color": "#%02x%02x%02x" % colors["scale_brightness"][9],
            "font-family": main_font,
        },
        "highlight_value": {
            "marginLeft": "10px",
            "marginTop": "50px",
            "marginBottom": "00px",
            "textAlign": "center",
            "color": "#%02x%02x%02x" % colors["scale_brightness"][10],
            "font-family": main_font,
            "className": "h-50",
            "justify": "center",
        },
        "margins": {
            "marginLeft": "10px",
            "marginRight": "10px",
            "marginTop": "10px",
            "marginBottom": "10px",
        },
    }
    figure_config = {
        "font_size": 18,
        "font_color": "grey",
        "paper_bgcolor": style["card_color"],
        "plot_bgcolor": style["card_color"],
        "font_family": style["font"],
        "title_font_size": style["diagram_title_size"],
        "title_x": 0,
        "margin": dict(l=5, r=5, t=5, b=5),
        "legend": dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    }
    card_style = {
        "borderRadius": "1vh",
        "padding": "1vh",
        "margin": "1vh",
        "border": f"0px solid {style['main_color']}",
        "backgroundColor": style["card_color"],
    }
    card_style_contrast = {
        "borderRadius": "1vh",
        "padding": "1vh",
        "margin": "1vh",
        "border": f"0px solid {style['main_color']}",
        "backgroundColor": style["card_color_dark"],
    }
    interpolation = {"smoothed": "spline", "linear": "linear", "discrete": "hv"}
    T = simulation.factory.timesteps
    component_key_list = list(simulation.factory.components.keys())
    connection_key_list = list(simulation.factory.connections.keys())

    # INITIALIZE COMPONENTS

    # Figures
    figures = {
        "pie_in": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={"height": "40vh", "width": "40vh"},
        ),
        "pie_out": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "40vh",
            },
        ),
        "sankey": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "80vh",
            },
        ),
        "converter": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "80vh",
            },
        ),
        "converter_efficiency": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "40vh",
            },
        ),
        "pool": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "70vh",
            },
        ),
        "sink": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "70vh",
            },
        ),
        "source": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "40vh",
            },
        ),
        "source_cost": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "30vh",
            },
        ),
        "storage": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "70vh",
            },
        ),
        "thermal": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "40vh",
            },
        ),
        "thermal2": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "40vh",
            },
        ),
        "schedule1": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "40vh",
            },
        ),
        "schedule2": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "40vh",
            },
        ),
        "schedule3": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "30vh",
            },
        ),
        "heatpump_utilization": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "30vh",
            },
        ),
        "heatpump_cop": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "30vh",
            },
        ),
        "heatpump_cop_profile": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "30vh",
            },
        ),
    }

    # Textboxes
    component_info = {
        "sankey_title": dcc.Markdown(style=style["card_title"]),
        "pie_in_title": dcc.Markdown(style=style["card_title"]),
        "pie_out_title": dcc.Markdown(style=style["card_title"]),
        "input_information": dcc.Markdown(style=style["highlight_value"]),
        "output_information": dcc.Markdown(style=style["highlight_value"]),
        "total_cost": dcc.Markdown(style=style["highlight_value"]),
        "converter_config": dcc.Markdown(style={"marginLeft": "10px"}),
        "converter_results": dcc.Markdown(style={"marginLeft": "10px"}),
        "detailed_cost": dcc.Markdown(style={"marginLeft": "10px"}),
        "detailed_emissions": dcc.Markdown(style={"marginLeft": "10px"}),
        "pool_config": dcc.Markdown(style={"marginLeft": "10px"}),
        "sink_config": dcc.Markdown(style={"marginLeft": "10px"}),
        "source_config": dcc.Markdown(style={"marginLeft": "10px"}),
        "source_sum": dcc.Markdown(style=style["highlight_value"]),
        "source_cost": dcc.Markdown(style=style["highlight_value"]),
        "source_minmax": dcc.Markdown(style=style["highlight_value"]),
        "source_avg": dcc.Markdown(style=style["highlight_value"]),
        "sink_sum": dcc.Markdown(style=style["highlight_value"]),
        "sink_cost": dcc.Markdown(style=style["highlight_value"]),
        "sink_minmax": dcc.Markdown(style=style["highlight_value"]),
        "sink_avg": dcc.Markdown(style=style["highlight_value"]),
        "storage_config": dcc.Markdown(style={"marginLeft": "10px"}),
        "storage_results": dcc.Markdown(style={"marginLeft": "10px"}),
        "slack": dcc.Markdown(style={"marginLeft": "10px"}),
        "converter": dcc.Markdown(style={"marginLeft": "10px"}),
        "schedule_config": dcc.Markdown(style={"marginLeft": "10px"}),
        "schedule_results": dcc.Markdown(style={"marginLeft": "10px"}),
        "thermal_config": dcc.Markdown(style={"marginLeft": "10px"}),
        "thermal_results": dcc.Markdown(style={"marginLeft": "10px"}),
        "deadtime": dcc.Markdown(style={"marginLeft": "10px"}),
        "heatpump_config": dcc.Markdown(style={"marginLeft": "10px"}),
        "heatpump_sum_in": dcc.Markdown(style=style["highlight_value"]),
        "heatpump_sum_out": dcc.Markdown(style=style["highlight_value"]),
        "heatpump_avg_cop": dcc.Markdown(style=style["highlight_value"]),
        "heatpump_cop_range": dcc.Markdown(style=style["highlight_value"]),
    }
    # Dropdowns
    dropdowns = {
        "linestyle_source": dcc.Dropdown(
            options=["smoothed", "linear", "discrete"],
            value="discrete",
            clearable=False,
        ),
        "linestyle_sink": dcc.Dropdown(
            options=["smoothed", "linear", "discrete"],
            value="discrete",
            clearable=False,
        ),
        "linestyle_pool": dcc.Dropdown(
            options=["smoothed", "linear", "discrete"],
            value="discrete",
            clearable=False,
        ),
        "linestyle_schedule": dcc.Dropdown(
            options=["smoothed", "linear", "discrete"],
            value="discrete",
            clearable=False,
        ),
        "sankey": dcc.Dropdown(
            options=[
                "Factory Architecture",
                "Energy Flows",
                "Material Flows",
                "Energy Losses",
                "Material Losses",
            ],
            value="Factory Architecture",
            clearable=False,
        ),
    }
    options = {
        "converter": [],
        "deadtime": [],
        "heatpump": [],
        "pool": [],
        "sink": [],
        "source": [],
        "storage": [],
        "slack": [],
        "schedule": [],
        "thermalsystem": [],
        "triggerdemand": [],
    }
    for c in simulation.factory.components:
        options[simulation.factory.components[c].type].append(
            simulation.factory.components[c].name
        )
    for arg in options:
        if options[arg] == []:
            dropdowns[arg] = dcc.Dropdown(
                options=options[arg], clearable=False, disabled=True
            )
        else:
            dropdowns[arg] = dcc.Dropdown(
                options=options[arg],
                value=options[arg][0],
                clearable=False,
                disabled=False,
            )

    # DEFINE DASH LAYOUT
    # app.layout = dbc.Container([theme_switch], className="m-4 dbc")
    app.layout = create_layout_html(
        style,
        card_style,
        card_style_contrast,
        component_info,
        dropdowns,
        figures,
        simulation,
    )

    # SET CALLBACKS
    # TAB: OVERVIEW
    @app.callback(
        Output(figures["sankey"], component_property="figure"),
        Output(figures["pie_in"], component_property="figure"),
        Output(figures["pie_out"], component_property="figure"),
        Output(component_info["sankey_title"], component_property="children"),
        Output(component_info["pie_in_title"], component_property="children"),
        Output(component_info["pie_out_title"], component_property="children"),
        Output(component_info["input_information"], component_property="children"),
        Output(component_info["total_cost"], component_property="children"),
        Output(component_info["detailed_cost"], component_property="children"),
        Output(component_info["detailed_emissions"], component_property="children"),
        Input(dropdowns["sankey"], component_property="value"),
    )
    def update_plots_overview(
        user_input,
    ):  # function arguments come from the Component property of the Input
        # CREATE SANKEY PLOTS
        # create weights for the displayed connections based on the user validate:
        connection_list = np.empty((0, 4), int)
        connection_colorlist = []
        for i in simulation.factory.connections:
            if user_input == "Energy Flows":
                if simulation.factory.connections[i].flowtype.is_energy():
                    connection_list = np.append(
                        connection_list,
                        np.array(
                            [
                                [
                                    component_key_list.index(
                                        simulation.factory.connections[i].origin.key
                                    ),
                                    component_key_list.index(
                                        simulation.factory.connections[
                                            i
                                        ].destination.key
                                    ),
                                    sum(
                                        simulation.result[
                                            simulation.factory.connections[i].key
                                        ]
                                    ),
                                    connection_key_list.index(
                                        simulation.factory.connections[i].key
                                    ),
                                ]
                            ]
                        ),
                        axis=0,
                    )
                    # add the color of the new connection to the colorlist
                    connection_colorlist.append(
                        simulation.factory.connections[i].flowtype.color.hex
                    )
            elif user_input == "Material Flows":
                if simulation.factory.connections[i].flowtype.is_material():
                    connection_list = np.append(
                        connection_list,
                        np.array(
                            [
                                [
                                    component_key_list.index(
                                        simulation.factory.connections[i].origin.key
                                    ),
                                    component_key_list.index(
                                        simulation.factory.connections[
                                            i
                                        ].destination.key
                                    ),
                                    sum(
                                        simulation.result[
                                            simulation.factory.connections[i].key
                                        ]
                                    ),
                                    connection_key_list.index(
                                        simulation.factory.connections[i].key
                                    ),
                                ]
                            ]
                        ),
                        axis=0,
                    )
                    # add the color of the new connection to the colorlist
                    connection_colorlist.append(
                        simulation.factory.connections[i].flowtype.color.hex
                    )
            elif user_input == "Factory Architecture":
                connection_list = np.append(
                    connection_list,
                    np.array(
                        [
                            [
                                component_key_list.index(
                                    simulation.factory.connections[i].origin.key
                                ),
                                component_key_list.index(
                                    simulation.factory.connections[i].destination.key
                                ),
                                simulation.factory.connections[i].weight,
                                connection_key_list.index(
                                    simulation.factory.connections[i].key
                                ),
                            ]
                        ]
                    ),
                    axis=0,
                )

                # add the color of the new connection to the colorlist
                connection_colorlist.append(
                    simulation.factory.connections[i].flowtype.color.hex
                )
            elif user_input == "Energy Losses":
                if (
                    simulation.factory.connections[i].flowtype.is_losses()
                    and simulation.factory.connections[i].flowtype.unit.quantity_type
                    == "energy"
                ):
                    connection_list = np.append(
                        connection_list,
                        np.array(
                            [
                                [
                                    component_key_list.index(
                                        simulation.factory.connections[i].origin.key
                                    ),
                                    component_key_list.index(
                                        simulation.factory.connections[
                                            i
                                        ].destination.key
                                    ),
                                    sum(
                                        simulation.result[
                                            simulation.factory.connections[i].key
                                        ]
                                    ),
                                    connection_key_list.index(
                                        simulation.factory.connections[i].key
                                    ),
                                ]
                            ]
                        ),
                        axis=0,
                    )
                    # add the color of the new connection to the colorlist
                    connection_colorlist.append(
                        simulation.factory.connections[i].flowtype.color.hex
                    )
            elif user_input == "Material Losses":
                if (
                    simulation.factory.connections[i].flowtype.is_losses()
                    and simulation.factory.connections[i].flowtype.unit.quantity_type
                    == "material"
                ):
                    connection_list = np.append(
                        connection_list,
                        np.array(
                            [
                                [
                                    component_key_list.index(
                                        simulation.factory.connections[i].origin.key
                                    ),
                                    component_key_list.index(
                                        simulation.factory.connections[
                                            i
                                        ].destination.key
                                    ),
                                    sum(
                                        simulation.result[
                                            simulation.factory.connections[i].key
                                        ]
                                    ),
                                    simulation.factory.connections.keys().index(
                                        simulation.factory.connections[i].key
                                    ),
                                ]
                            ]
                        ),
                        axis=0,
                    )
                    # add the color of the new connection to the colorlist
                    connection_colorlist.append(
                        simulation.factory.connections[i].flowtype.color.hex
                    )

        # create a list of existing components to be displayed
        component_namelist = []
        component_colorlist = []
        for i in simulation.factory.components:
            component_colorlist.append(
                simulation.factory.components[i].flowtype.color.hex
            )  # add fitting color to the colorlist
            component_namelist.append(simulation.factory.components[i].name)

        fig_sankey = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=70,
                        thickness=20,
                        line=dict(color="grey", width=0.8),
                        label=component_namelist,
                        color=component_colorlist,
                    ),
                    link=dict(
                        source=connection_list[:, 0],
                        target=connection_list[:, 1],
                        value=connection_list[:, 2],
                        color=connection_colorlist,
                    ),
                )
            ]
        )

        if user_input == "Energy Flows":
            title_sankey = "##### ENERGY FLOWS"
        elif user_input == "Factory Architecture":
            title_sankey = "##### SIMULATION ARCHITECTURE"
        elif user_input == "Material Flows":
            title_sankey = "##### MATERIAL FLOWS"
        elif user_input == "Energy Losses":
            title_sankey = "##### ENERGY LOSSES"
        elif user_input == "Material Losses":
            title_sankey = "##### MATERIAL LOSSES"
        fig_sankey.update_layout(figure_config)

        # CREATE PIEPLOTS
        # collect data
        values_in = []
        names_in = []
        values_out = []
        names_out = []
        for c in simulation.factory.components:
            component = simulation.factory.components[c]
            if component.type == "source":
                if component.flowtype.is_energy() and user_input == "Energy Flows":
                    values_in = np.append(
                        values_in, sum(simulation.result[component.key]["utilization"])
                    )
                    names_in.append(component.name)

                if component.flowtype.is_material() and user_input == "Material Flows":
                    values_in = np.append(
                        values_in, sum(simulation.result[component.key]["utilization"])
                    )
                    names_in.append(component.name)

            if component.type == "sink":
                if component.flowtype.is_energy() and user_input == "Energy Flows":
                    values_out = np.append(
                        values_out,
                        sum(simulation.result[component.key]["utilization"]),
                    )
                    names_out.append(component.name)

                if (
                    not component.flowtype.is_energy()
                    and user_input == "Material Flows"
                ):
                    values_out = np.append(
                        values_out,
                        sum(simulation.result[component.key]["utilization"]),
                    )
                    names_out.append(component.name)
        if user_input == "Energy Losses":
            for c in simulation.factory.connections:
                connection = simulation.factory.connections[c]
                if connection.flowtype.is_energy() and connection.flowtype.is_losses():
                    values_in = np.append(
                        values_in, sum(simulation.result[connection.key])
                    )
                    names_in.append(connection.origin.name)
        if user_input == "Material Losses":
            for c in simulation.factory.connections:
                connection = simulation.factory.connections[c]
                if (
                    connection.flowtype.is_material()
                    and connection.flowtype.is_losses()
                ):
                    values_in = np.append(
                        values_in, sum(simulation.result[connection.key])
                    )
                    names_in.append(connection.origin.name)
        df_in = {"values": values_in, "names": names_in}
        df_out = {"values": values_out, "names": names_out}

        # create pie descriptions
        title_in = ""
        title_out = ""
        input_info = ""
        if user_input == "Energy Flows":
            title_in = "##### DISTRIBUTION OF ENERGY INPUTS"
            title_out = "##### DISTRIBUTION OF ENERGY OUTPUTS"
            input_info = f"## {simulation.factory.units['energy'].get_value_expression(sum(values_in), 'flow')}"
        elif user_input == "Material Flows":
            title_in = "##### DISTRIBUTION OF MATERIAL INPUTS"
            title_out = "##### DISTRIBUTION OF MATERIAL OUTPUTS"
            input_info = f"## {simulation.factory.units['mass'].get_value_expression(sum(values_in), 'flow')}"
        elif user_input == "Energy Losses" or user_input == "Material Losses":
            title_in = "##### ORIGINS OF LOSSES"
            title_out = ""

        # create diagrams
        fig_pie_in = px.pie(
            df_in,
            names="names",
            values="values",
            color_discrete_sequence=["rgb(156, 156, 156)", style["main_color_rgb"]],
        )
        fig_pie_in.update_layout(figure_config)
        fig_pie_out = px.pie(
            df_out,
            names="names",
            values="values",
            color_discrete_sequence=["rgb(156, 156, 156)", style["main_color_rgb"]],
        )
        fig_pie_out.update_layout(figure_config)

        total_cost = (
            f"## {round(simulation.result['objective'])} {simulation.factory.currency}"
        )

        detailed_costs = create_cost_overview(simulation)
        detailed_emissions = create_emission_overview(simulation)

        return (
            fig_sankey,
            fig_pie_in,
            fig_pie_out,
            title_sankey,
            title_in,
            title_out,
            input_info,
            total_cost,
            detailed_costs,
            detailed_emissions
        )  # returned objects are assigned to the Component property of the Output

    # TAB: CONVERTERS
    @app.callback(
        Output(figures["converter"], component_property="figure"),
        Output(figures["converter_efficiency"], component_property="figure"),
        Output(component_info["converter_config"], component_property="children"),
        Output(component_info["converter_results"], component_property="children"),
        Input(dropdowns["converter"], component_property="value"),
        Input("timestep_slider_converter", "value"),
    )
    def update_plots_converter(user_input, timesteps):
        if not user_input == None:
            t0 = timesteps[0]
            t1 = timesteps[1]
            x = np.arange(t0, t1, 1)
            component = simulation.factory.components[
                simulation.factory.get_key(user_input)
            ]
            Pmin = min(component.power_min)
            if component.power_max_limited:
                Pmax = int(max(component.power_max))
            else:
                Pmax = round(max(simulation.result[component.key]["utilization"])) + 10

            # plot utilization
            data = (
                simulation.result[component.key]["utilization"][t0:t1]
                / simulation.scenario.timefactor
                * simulation.factory.timefactor
            )
            fig = go.Figure()

            # Print Utilization
            if component.power_min_limited:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=component.power_min[t0:t1] * component.availability[t0:t1],
                        line_color="rgb(192,0,0)",
                        name="Pmin",
                        line_dash="dot",
                    )
                )
            if component.power_max_limited:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=component.power_max[t0:t1] * component.availability[t0:t1],
                        line_color="rgb(192,0,0)",
                        name="power_max",
                        line_dash="dash",
                    )
                )
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=data,
                    line_shape="hv",
                    line_color=style["main_color_rgb"],
                    name="Utilization",
                )
            )
            fig.update_layout(figure_config)
            fig.update_xaxes(
                title_text=f"Simulation Interval",
                linewidth=2,
                linecolor=style["axis_color"],
            )
            fig.update_yaxes(
                title_text=f"Utilization {component.flowtype.unit_flowrate()}",
                range=[0, Pmax * 1.05],
                linewidth=2,
                linecolor=style["axis_color"],
            )
            # plot efficiency
            efficiency = np.zeros(Pmax + 10)
            for p in range(Pmax + 10):
                if component.eta_variable:
                    if p >= Pmin and p <= component.power_nominal:
                        efficiency[p] = (
                            component.eta_max
                            - component.delta_eta_low * (component.power_nominal - p)
                            - 1
                            + component.eta_base
                        ) * 100
                    if p >= component.power_nominal and p <= Pmax:
                        efficiency[p] = (
                            component.eta_max
                            - component.delta_eta_high * (p - component.power_nominal)
                            - 1
                            + component.eta_base
                        ) * 100
                else:
                    if p >= Pmin and p <= max(component.power_max):
                        efficiency[p] = component.eta_max * component.eta_base * 100
                    else:
                        efficiency[p] = 0

            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=np.arange(0, Pmax + 10),
                    y=efficiency,
                    line_shape="linear",
                    line_color=style["main_color_rgb"],
                    name="Efficiency",
                )
            )
            if component.power_min_limited:
                fig2.add_vline(
                    x=Pmin,
                    line_width=2,
                    line_dash="dash",
                    line_color="rgb(192,0,0)",
                    annotation_text="Pmin",
                )
            if component.power_max_limited:
                fig2.add_vline(
                    x=Pmax,
                    line_width=2,
                    line_dash="dash",
                    line_color="rgb(192,0,0)",
                    annotation_text="power_max",
                )
            if component.eta_variable:
                if Pmax - component.power_nominal > component.power_nominal - min(
                    component.power_min
                ):
                    fig2.add_vline(
                        x=component.power_nominal,
                        line_width=2,
                        line_dash="dash",
                        line_color=style["second_color_rgb"],
                        annotation_text="Pnominal",
                        annotation_position="top right",
                    )
                else:
                    fig2.add_vline(
                        x=component.power_nominal,
                        line_width=2,
                        line_dash="dash",
                        line_color=style["second_color_rgb"],
                        annotation_text="Pnominal",
                        annotation_position="top left",
                    )

            fig2.update_layout(figure_config)
            fig2.update_xaxes(
                title_text=f"Utilization [SU/Δt]",
                linewidth=2,
                linecolor=style["axis_color"],
            )
            fig2.update_yaxes(
                title_text=f"Efficiency [%]",
                range=[0, 100],
                linewidth=2,
                linecolor=style["axis_color"],
            )

            # collect configuration information
            config = f"\n **Pnominal**: {component.power_nominal} {component.flowtype.unit_flowrate()}\n "
            if component.power_max_limited:
                config = (
                    config
                    + f"\n**power_max:** {component.flowtype.get_value_expression(round(max(component.power_max)), 'flowrate')}\n "
                )
            else:
                config = config + f"\n**power_max**: Unlimited \n"
            if component.power_min_limited:
                config = (
                    config
                    + f"\n**Pmin**: {component.flowtype.get_value_expression(round(min(component.power_min)), 'flowrate')}\n"
                )
            else:
                config = config + f"\n**Pmin**: 0 SU/Δt \n"
            if component.power_ramp_max_pos < 10000000:
                config = (
                    config
                    + f"\n**Fastest Rampup:** {component.flowtype.get_value_expression(round(component.power_ramp_max_pos), 'flowrate')} \n "
                )
            else:
                config = config + f"\n**Fastest Rampup:** Unlimited \n "
            if component.power_ramp_max_neg < 10000000:
                config = (
                    config
                    + f"\n**Fastest Rampdown:** {component.flowtype.get_value_expression(round(component.power_ramp_max_neg), 'flowrate')} \n "
                )
            else:
                config = config + f"\n**Fastest Rampdown:** Unlimited \n "
            if component.eta_variable:
                config = (
                    config
                    + f"\n **Optimal efficiency:** {round(component.eta_max*component.eta_base * 100)}% \n"
                )
            else:
                config = (
                    config
                    + f"\n **Efficiency:** {round(component.eta_max * component.eta_base * 100)}% \n"
                )

            config = config + f"\n **Is switchable?**: {component.switchable} \n "

            # collect result information
            results = ""
            results = (
                results
                + f"\n **Total Conversion**: {component.flowtype.get_value_expression(round(sum(simulation.result[component.key]['utilization'])), 'flow')}  \n"
                f"\n **Highest Utilization**: {component.flowtype.get_value_expression(round(max(simulation.result[component.key]['utilization'])), 'flowrate')} \n"
                f"\n **Lowest Utilization**: {component.flowtype.get_value_expression(round(min(simulation.result[component.key]['utilization'])), 'flowrate')} \n "
                f"\n **Average Utilization**: {component.flowtype.get_value_expression(round(simulation.result[component.key]['utilization'].mean()), 'flowrate')} \n"
                f"\n **Activation Time**: {sum(simulation.result[component.key]['utilization'] > 0.001)} Intervals ({round(sum(simulation.result[component.key]['utilization'] > 0.001) / T *100)}% of time)\n"
            )

        else:
            fig = go.Figure()
            fig2 = go.Figure()
            config = f"\n**Pmin**: unlimited \n"
            results = ""
        return fig, fig2, config, results

    # TAB: POOLS
    @app.callback(
        Output(figures["pool"], component_property="figure"),
        Input(dropdowns["pool"], component_property="value"),
        Input("timestep_slider_pool", "value"),
        Input(dropdowns["linestyle_pool"], component_property="value"),
    )
    def update_plots_pool(user_input, timesteps, linestyle):
        if user_input == None:
            return go.Figure()

        t0 = timesteps[0]
        t1 = timesteps[1]
        x = np.arange(t0, t1, 1)
        component = simulation.factory.components[
            simulation.factory.get_key(user_input)
        ]

        fig = go.Figure()
        # create positive side of the diagram
        c = sample_colorscale(
            "darkmint", list(np.linspace(0.3, 1, len(component.inputs)))
        )
        for i in range(0, len(component.inputs)):
            if max(simulation.result[component.inputs[i].key][t0:t1]) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=np.array(simulation.result[component.inputs[i].key][t0:t1])
                        / simulation.scenario.timefactor
                        * simulation.factory.timefactor,
                        hoverinfo="x",
                        mode="lines",
                        stackgroup="one",
                        line_shape=interpolation[linestyle],
                        name=f" Inflow from {component.inputs[i].origin.name}",
                        line={"color": c[i]},
                    )
                )

        # create negative side of the diagram
        c = sample_colorscale(
            "peach", list(np.linspace(0.3, 1, len(component.outputs)))
        )
        for i in range(0, len(component.outputs)):
            if max(simulation.result[component.outputs[i].key][t0:t1]) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=-np.array(simulation.result[component.outputs[i].key][t0:t1])
                        / simulation.scenario.timefactor
                        * simulation.factory.timefactor,
                        hoverinfo="x",
                        mode="lines",
                        stackgroup="two",
                        line_shape=interpolation[linestyle],
                        name=f"Outflow to {component.outputs[i].destination.name}",
                        line={"color": c[i]},
                    )
                )

        fig.update_layout(
            figure_config,
            # title_text="BILANCE SUM AT POOL",
            xaxis_title="Simulation interval",
            yaxis_title=f"{component.flowtype.name} [{component.inputs[0].flowtype.unit.get_unit_flowrate()}]",
        )
        return fig

    # TAB: SOURCE
    @app.callback(
        Output(figures["source"], component_property="figure"),
        Output(figures["source_cost"], component_property="figure"),
        Output(component_info["source_sum"], component_property="children"),
        Output(component_info["source_cost"], component_property="children"),
        Output(component_info["source_minmax"], component_property="children"),
        Output(component_info["source_avg"], component_property="children"),
        Input(dropdowns["source"], component_property="value"),
        Input(dropdowns["linestyle_source"], component_property="value"),
        Input("timestep_slider_source", "value"),
    )
    def update_plots_source(user_input, linestyle, timesteps):
        t0 = timesteps[0]
        t1 = timesteps[1]
        x = np.arange(t0, t1, 1)
        component = simulation.factory.components[
            simulation.factory.get_key(user_input)
        ]
        data = (
            simulation.result[component.key]["utilization"][t0:t1]
            / simulation.scenario.timefactor
            * simulation.factory.timefactor
        )

        fig = go.Figure()

        if component.power_min_limited:
            figures["sink"].add_trace(
                go.Scatter(
                    x=x,
                    y=np.ones(t1 - t0) * component.power_min[t0:t1],
                    line_color="rgb(192,0,0)",
                    name="Pmin",
                    line_dash="dot",
                )
            )
        if component.power_max_limited:
            Pmax = max(component.power_max)
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.ones(t1 - t0)
                    * component.power_max[t0:t1]
                    * component.availability[t0:t1],
                    line_color="rgb(192,0,0)",
                    name="Valid operation points",
                    line_dash="dash",
                    line_shape=interpolation[linestyle],
                )
            )
        else:
            Pmax = max(data)

        fig.add_trace(
            go.Scatter(
                x=x,
                y=data,
                line_shape=interpolation[linestyle],
                line_color=style["main_color_rgb"],
                name="Utilization",
            )
        )
        fig.update_layout(
            figure_config,
            xaxis_title="Timesteps",
            yaxis_title=f"{component.flowtype_description} {component.flowtype.unit.get_unit_flowrate()}",
            showlegend=False,
        )
        fig.update_xaxes(linewidth=2, linecolor=style["axis_color"])
        fig.update_yaxes(linewidth=2, linecolor=style["axis_color"], range=[0, Pmax])

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=np.ones(t1 - t0) * component.cost[t0:t1],
                line_color=f"rgb{colors['main']}",
                name="Cost",
                line_shape=interpolation[linestyle],
            )
        )
        fig2.update_layout(
            figure_config,
            xaxis_title="Timesteps",
            yaxis_title=f"€ / {component.flowtype.unit.get_unit_flow()}",
        )

        source_sum = "## " + component.flowtype.unit.get_value_expression(
            value=round(sum(simulation.result[component.key]["utilization"][t0:t1])),
            quantity_type="flow",
        )
        source_cost = f"## {round(sum(simulation.result[component.key]['utilization'][t0:t1] * component.cost[t0:t1]))} €"
        source_minmax = (
            f"## {component.flowtype.unit.get_value_expression(value=round(min(simulation.result[component.key]['utilization'][t0:t1])), quantity_type='flowrate')} "
            f"- {component.flowtype.unit.get_value_expression(value=round(max(simulation.result[component.key]['utilization'][t0:t1])), quantity_type='flowrate')}"
        )
        source_avg = f"## {component.flowtype.unit.get_value_expression(value=round(simulation.result[component.key]['utilization'][t0:t1].mean()), quantity_type='flowrate')}"
        return fig, fig2, source_sum, source_cost, source_minmax, source_avg

    # TAB: SINK
    @app.callback(
        Output(figures["sink"], component_property="figure"),
        Output(component_info["sink_sum"], component_property="children"),
        Output(component_info["sink_cost"], component_property="children"),
        Output(component_info["sink_minmax"], component_property="children"),
        Output(component_info["sink_avg"], component_property="children"),
        Input(dropdowns["sink"], component_property="value"),
        Input(dropdowns["linestyle_sink"], component_property="value"),
        Input("timestep_slider_sink", "value"),
    )
    def update_plots_sink(user_input, linestyle, timesteps):
        t0 = timesteps[0]
        t1 = timesteps[1]
        x = np.arange(t0, t1, 1)
        component = simulation.factory.components[
            simulation.factory.get_key(user_input)
        ]
        data = (
            simulation.result[component.key]["utilization"][t0:t1]
            / simulation.scenario.timefactor
            * simulation.factory.timefactor
        )
        fig = go.Figure()

        if component.power_min_limited:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.ones(t1 - t0) * component.power_min[t0:t1],
                    line_color="rgb(192,0,0)",
                    name="Pmin",
                    line_dash="dot",
                )
            )
        if component.power_max_limited:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.ones(t1 - t0) * component.power_max[t0:t1],
                    line_color="rgb(192,0,0)",
                    name="power_max",
                    line_dash="dash",
                )
            )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=data,
                line_shape=interpolation[linestyle],
                line_color=style["main_color_rgb"],
                name="Utilization",
            )
        )

        fig.update_layout(
            figure_config,
            # title_text="UTILIZATION",
            xaxis_title="Timesteps",
            yaxis_title=f"{component.flowtype_description} [{component.flowtype.unit.get_unit_flowrate()}]",
        )
        fig.update_xaxes(linewidth=2, linecolor=style["axis_color"])
        fig.update_yaxes(
            linewidth=2, linecolor=style["axis_color"], range=[0, max(data) * 1.05]
        )

        sink_sum = "## " + component.flowtype.unit.get_value_expression(
            value=round(sum(simulation.result[component.key]["utilization"][t0:t1])),
            quantity_type="flow",
        )
        sink_minmax = f"## {component.flowtype.unit.get_value_expression(round(min(simulation.result[component.key]['utilization'][t0:t1])), 'flowrate')} - {component.flowtype.unit.get_value_expression(round(max(simulation.result[component.key]['utilization'][t0:t1])), 'flowrate')}"

        cost = 0
        if component.chargeable:
            cost += sum(
                simulation.result[component.key]["utilization"][t0:t1]
                * component.cost[t0:t1]
            )
        if component.refundable:
            cost += -sum(
                simulation.result[component.key]["utilization"][t0:t1]
                * component.revenue[t0:t1]
            )
        sink_cost = f"## {round(cost)} €"

        if component.power_max_limited:
            sink_avg = f"## {component.flowtype.unit.get_value_expression(round(simulation.result[component.key]['utilization'][t0:t1].mean()), 'flowrate')} / {round(((simulation.result[component.key]['utilization'][t0:t1] + 0.000001) / (component.power_max[t0:t1] * component.availability[t0:t1] + 0.000001)).mean() * 100)}%"
        else:
            sink_avg = f"## {component.flowtype.unit.get_value_expression(round(simulation.result[component.key]['utilization'][t0:t1].mean()), 'flowrate')}"

        return fig, sink_sum, sink_cost, sink_minmax, sink_avg

    # TAB: STORAGE
    @app.callback(
        Output(figures["storage"], component_property="figure"),
        Output(component_info["storage_config"], component_property="children"),
        Output(component_info["storage_results"], component_property="children"),
        Input(dropdowns["storage"], component_property="value"),
        Input("timestep_slider_storage", "value"),
    )
    def update_plots_storage(user_input, timesteps):
        if not user_input == None:
            t0 = timesteps[0]
            t1 = timesteps[1]
            x = np.arange(t0, t1, 1)

            component = simulation.factory.components[
                simulation.factory.get_key(user_input)
            ]

            data = (
                -simulation.result[component.key]["utilization"][t0:t1]
                / simulation.scenario.timefactor
                * simulation.factory.timefactor
            )
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Print SOC in background on secondary axis
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.r_[simulation.result[component.key]["SOC"][t0:t1]],
                    line_color="rgb(200,200,200)",
                    stackgroup="one",
                    name="SOC",
                ),
                secondary_y=False,
            )
            # Print Pcharge_min and Pcharge_max
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.ones(t1 - t0) * component.power_max_charge,
                    line_color="rgb(192,0,0)",
                    name="Max Inflow / Capacity",
                    line_dash="dot",
                ),
                secondary_y=True,
            )
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=-np.ones(t1 - t0) * component.power_max_discharge,
                    line_color="rgb(192,0,0)",
                    name="Max Outflow",
                    line_dash="dash",
                ),
                secondary_y=True,
            )

            # Print Pcharge
            fig.add_hline(y=0, line_color="lightgrey", secondary_y=True)
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=data,
                    line_shape="hv",
                    line_color=style["main_color_rgb"],
                    name="Utilization",
                ),
                secondary_y=True,
            )

            fig.update_layout(
                figure_config,
                xaxis_title="Timesteps",
            )
            fig.update_yaxes(
                title_text=f"State of charge [{component.flowtype.unit.get_unit_flow()}]",
                range=[0, component.capacity],
                secondary_y=False,
                linewidth=2,
                linecolor=style["axis_color"],
            )
            fig.update_yaxes(
                title_text=f"Inflow/Outflow [{component.flowtype.unit.get_unit_flowrate()}]",
                range=[min(data) * 1.1, max(data) * 1.1],
                secondary_y=True,
                linewidth=2,
                linecolor=style["axis_color"],
            )

            inputs = ""
            input_sum = 0
            for i_input in component.inputs:
                inputs += f"\n * {i_input.origin.name}\n"
                input_sum += sum(simulation.result[i_input.key])

            outputs = ""
            output_sum = 0
            for i_output in component.outputs:
                outputs += f"\n * {i_output.destination.name}\n"
                output_sum += sum(simulation.result[i_output.key])

            config = (
                f"\n **Max usable capacity:** {component.flowtype.unit.get_value_expression(component.capacity,'flow')}\n"
                f"\n **Base efficiency:** {component.efficiency * 100} %\n"
                f"\n **SOC start:** {component.flowtype.unit.get_value_expression(component.soc_start * component.capacity,'flow')} ({component.soc_start * 100}%)\n"
                f"\n **Leakage per timestep:** \n"
                f"\n * {component.leakage_time} % of total Capacity\n"
                f"\n * {component.leakage_SOC} % of SOC\n"
                f"\n **Max charging Power:** {component.flowtype.unit.get_value_expression(component.power_max_charge,'flow')}\n"
                f"\n **Max discharging Power:** {component.flowtype.unit.get_value_expression(component.power_max_discharge,'flow')}\n"
                f"\n **Input:** \n"
                f"\n {inputs} \n"
                f"\n **Output:** \n"
                f"\n {outputs} \n"
                f"\n **Capital cost of used capacity:** {component.capacity_charge} {simulation.factory.currency}/{component.flowtype.unit.get_unit_flow()}\n"
            )

            results = (
                f"\n **Used capacity:** {component.flowtype.unit.get_value_expression(round(simulation.result[component.key]['SOC'].max()), 'flow')}\n"
                f"\n **Total inflow:** {component.flowtype.unit.get_value_expression(round(input_sum), 'flow')}\n"
                f"\n **Total outflow:** {component.flowtype.unit.get_value_expression(round(output_sum), 'flow')}\n"
                f"\n **Occuring losses:** {component.flowtype.unit.get_value_expression(round(sum(simulation.result[component.to_losses.key])), 'flow')} ({round(sum(simulation.result[component.to_losses.key]) / input_sum * 100, 2)}%)\n "
                f"\n **Max input power:** {component.flowtype.unit.get_value_expression(-round(min(simulation.result[component.key]['utilization'])), 'flowrate')}\n "
                f"\n **Max output power:** {component.flowtype.unit.get_value_expression(round(max(simulation.result[component.key]['utilization'])), 'flowrate')}\n "
                f"\n **Average SOC:** {component.flowtype.unit.get_value_expression(round(simulation.result[component.key]['SOC'].mean()), 'flow')}\n "
                f"\n **Charging circles:** {round(input_sum / (simulation.result[component.key]['SOC'].max() + 0.0001))} (Estimated) \n "
                f"\n **Resulting capital cost:** {round(component.capacity_charge / 8760 * simulation.T * round(simulation.result[component.key]['SOC'].max() + 0.0001),2)}{simulation.factory.currency} \n "
            )
        else:
            fig = go.Figure()
            config = ""
            results = ""
        return fig, config, results

    # TAB: THERMAL SYSTEM
    @app.callback(
        Output(figures["thermal"], component_property="figure"),
        Output(figures["thermal2"], component_property="figure"),
        Output(component_info["thermal_config"], component_property="children"),
        Output(component_info["thermal_results"], component_property="children"),
        Input(dropdowns["thermalsystem"], component_property="value"),
        Input("timestep_slider_thermal", "value"),
    )
    def update_plots_thermal(user_input, timesteps):
        # Abort if there are no thermal systems in the simulation
        if user_input == None:
            return go.Figure(), go.Figure(), "", ""

        t0 = timesteps[0]
        t1 = timesteps[1]
        x = np.arange(t0, t1, 1)
        component = simulation.factory.components[
            simulation.factory.get_key(user_input)
        ]

        """TEMPERATURE FIGURE"""
        fig1 = go.Figure()

        fig1.add_trace(
            go.Scatter(
                x=x,
                y=component.temperature_min[t0:t1] - 273.15,
                line_color="rgb(192,0,0)",
                hoverinfo="x+y",
                mode="lines",
                line_dash="dot",
                name="Lower temperature boundary",
            ),
        )
        fig1.add_trace(
            go.Scatter(
                x=x,
                y=np.ones(t1 - t0) * (component.temperature_max[t0:t1] - 273.15),
                line_color="rgb(192,0,0)",
                hoverinfo="x+y",
                line_dash="dot",
                mode="lines",
                name="Upper temperature boundary",
            ),
        )

        # print realized temperature
        fig1.add_trace(
            go.Scatter(
                x=x,
                y=simulation.result[component.key]["temperature"][t0:t1] - 273.15,
                line_color=style["main_color"],
                hoverinfo="x+y",
                mode="lines",
                name="System Temperature",
            ),
        )
        fig1.add_trace(
            go.Scatter(
                x=x,
                y=component.temperature_ambient[t0:t1] - 273.15,
                line_color=style["second_color"],
                hoverinfo="x+y",
                mode="lines",
                name="Ambient Temperature",
            ),
        )

        fig1.update_layout(
            figure_config,
            # xaxis={"visible": False, "showticklabels": False},
            xaxis_title="Timesteps",
            legend=dict(yanchor="bottom", y=0.99, xanchor="left", x=0.01),
        )

        fig1.update_yaxes(
            linewidth=2,
            linecolor=style["axis_color"],
            title_text="Temperature [°C]",
            range=[
                min(min(component.temperature_min), min(component.temperature_ambient))
                - 5
                - 273.15,
                (
                    max(
                        max(component.temperature_max),
                        max(component.temperature_ambient),
                    )
                    - 273.15
                )
                * 1.05,
            ],
        )

        """IN/OUTFLOW FIGURE"""
        fig2 = go.Figure()
        # create positive side of the diagram
        total_heating = 0
        inputs = ""
        for i in range(0, len(component.inputs)):
            fig2.add_trace(
                go.Scatter(
                    x=x,
                    y=np.array(simulation.result[component.inputs[i].key][t0:t1])
                    / simulation.scenario.timefactor
                    * simulation.factory.timefactor,
                    hoverinfo="x+y",
                    mode="lines",
                    stackgroup="one",
                    line_shape="hv",
                    name=component.inputs[i].origin.name,
                )
            )
            total_heating += sum(simulation.result[component.inputs[i].key])
            inputs += f"\n * {component.inputs[i].origin.name}\n"
        # add gains
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=np.array(simulation.result[component.from_gains.key][t0:t1])
                / simulation.scenario.timefactor
                * simulation.factory.timefactor,
                hoverinfo="x+y",
                mode="lines",
                stackgroup="one",
                line_shape="hv",
                name="Ambient Gains",
            )
        )
        # create negative side of the diagram
        total_cooling = 0
        outputs = ""
        for i in range(0, len(component.outputs)):
            fig2.add_trace(
                go.Scatter(
                    x=x,
                    y=-np.array(simulation.result[component.outputs[i].key][t0:t1])
                    / simulation.scenario.timefactor
                    * simulation.factory.timefactor,
                    hoverinfo="x+y",
                    mode="lines",
                    stackgroup="two",
                    line_shape="hv",
                    name=component.outputs[i].destination.name,
                )
            )
            total_cooling += sum(simulation.result[component.outputs[i].key])
            outputs += f"\n * {component.outputs[i].origin.name}\n"
        # add losses
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=-np.array(simulation.result[component.to_losses.key][t0:t1])
                / simulation.scenario.timefactor
                * simulation.factory.timefactor,
                hoverinfo="x+y",
                mode="lines",
                stackgroup="two",
                line_shape="hv",
                name="Thermal Losses",
            )
        )

        fig2.update_layout(
            figure_config,
            xaxis_title="Timesteps",
            yaxis_title="Energy gains / losses [kWh/Δt]",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        )
        fig2.update_xaxes(linewidth=2, linecolor=style["axis_color"])
        fig2.update_yaxes(linewidth=2, linecolor=style["axis_color"])

        config = (
            f"\n **Thermal Resistance:** {component.R} K/kW\n"
            f"\n **Thermal Capacity:** {component.C} kWh/K\n"
            f"\n **Tstart:** {component.temperature_start - 273.15} °C \n"
            f"\n **Tstart=Tend?:** {component.sustainable}\n"
            f"\n **Inputs:** \n"
            f"\n {inputs} \n"
            f"\n **Outputs:** \n"
            f"\n {outputs} \n"
        )
        results = (
            f"\n **Total Heating:** {round(total_heating)} {component.flowtype.unit.get_unit_flow()}\n "
            f"\n **Total Cooling:** {round(total_cooling)} {component.flowtype.unit.get_unit_flow()}\n "
            f"\n **Total thermal losses:** {round(sum(simulation.result[component.to_losses.key]))}{component.flowtype.unit.get_unit_flow()}\n"
            f"\n **T max:** {round(max(simulation.result[component.key]['temperature'])-273.15)} °C\n "
            f"\n **T min:** {round(min(simulation.result[component.key]['temperature'])-273.15)} °C\n "
            f"\n **T average:** {round(simulation.result[component.key]['temperature'].mean()-273.15)} °C\n "
        )

        return fig1, fig2, config, results

    # TAB: SCHEDULE
    @app.callback(
        Output(figures["schedule1"], component_property="figure"),
        Output(figures["schedule2"], component_property="figure"),
        Output(figures["schedule3"], component_property="figure"),
        Output(component_info["schedule_config"], component_property="children"),
        Output(component_info["schedule_results"], component_property="children"),
        Input(dropdowns["schedule"], component_property="value"),
        Input(dropdowns["linestyle_schedule"], component_property="value"),
        Input("timestep_slider_schedule", "value"),
    )
    def update_plots_schedule(user_input, linestyle, timesteps):
        if not user_input == None:
            t0 = timesteps[0]
            t1 = timesteps[1]
            x = np.arange(t0, t1, 1)
            component = simulation.factory.components[
                simulation.factory.get_key(user_input)
            ]

            utilization = simulation.result[component.key]["utilization"].transpose()
            availability = simulation.result[component.key]["availability"].transpose()

            # Create utilization-graph
            fig1 = go.Figure()

            data = (
                sum(utilization[:, t0:t1])
                / simulation.scenario.timefactor
                * simulation.factory.timefactor
            )
            if component.power_max_limited:
                fig1.add_trace(
                    go.Scatter(
                        x=x,
                        y=np.ones(t1 - t0) * component.power_max[t0:t1],
                        line_color="rgb(192,0,0)",
                        name="power_max",
                        line_dash="dash",
                    )
                )
            fig1.add_trace(
                go.Scatter(
                    x=x,
                    y=data,
                    line_shape=interpolation[linestyle],
                    line_color=style["main_color_rgb"],
                    name="Utilization",
                )
            )

            fig1.update_layout(figure_config)
            fig1.update_xaxes(
                linecolor=style["axis_color"],
                showgrid=True,
                showticklabels=True,
                title_text="Simulation interval",
                linewidth=2,
            )
            fig1.update_yaxes(
                title_text=f"Total utilization [{component.flowtype.unit_flow()}]",
                linewidth=2,
                range=[0, max(sum(utilization)) * 1.05],
                linecolor=style["axis_color"],
                gridcolor=style["grid_color"],
            )

            # Create fulfilment-graph
            fig2 = go.Figure()
            data2 = copy.copy(utilization[:, t0 : t1 - 1])
            data2[availability[:, t0 : t1 - 1] == 1] = None
            delete = []
            for z in range(len(data2)):
                if np.nansum(data2[z, :]) == 0:
                    delete.append(z)
            data2 = np.delete(data2, delete, 0)

            fig2.add_heatmap(
                z=data2[::-1, :],
                colorscale=[[0, "rgb(200,200,200)"], [1, style["main_color_rgb"]]],
                showlegend=False,
                showscale=False,
            )

            fig2.update_layout(figure_config)
            fig2.update_annotations(font_size=style["diagram_title_size"])
            fig2.update_xaxes(
                linecolor=style["axis_color"],
                showgrid=True,
                showticklabels=True,
                title_text="Simulation interval",
                linewidth=2,
            )
            fig2.update_yaxes(
                title_text="Part demands",
                linewidth=2,
                linecolor=style["axis_color"],
                showgrid=False,
                showticklabels=True,
            )

            # create demand heatmap
            data3 = np.zeros(
                [int(max(component.demands[:, 1] - component.demands[:, 0])) + 1, T]
            )
            for i in range(len(component.demands)):
                data3[
                    int(component.demands[i, 1] - component.demands[i, 0]),
                    int(component.demands[i, 0] - 1),
                ] = component.demands[i, 3]

            fig3 = go.Figure()
            fig3.add_heatmap(
                z=data3[:, t0 : t1 - 1],
                legendgrouptitle={"text": "Amount of demand"},
                colorscale=[[0, "rgb(200,200,200)"], [1, style["main_color_rgb"]]],
            )  # , row=1, col=1,showlegend=False, showscale=False)
            fig3.update_layout(
                figure_config,
                # title_text="DEMANDS",
            )
            fig3.update_yaxes(
                title_text="Available timeinterval for fullfilment",
                linewidth=2,
                linecolor=style["axis_color"],
            )
            fig3.update_xaxes(
                title_text=f"Timestep of demand occurance",
                linewidth=2,
                linecolor=style["axis_color"],
                gridcolor=style["grid_color"],
                tickvals=np.linspace(1, t1 - t0, num=10, endpoint=True),
                ticktext=np.linspace(t0, t1, num=10, endpoint=True).round(),
            )

            # create Component info
            config = ""
            if component.power_max_limited:
                config = (
                    config
                    + f"\n**power_max:** {component.flowtype.unit.get_value_expression(max(component.power_max), 'flowrate')}\n "
                )
            else:
                config = config + f"\n**power_max**: unlimited \n"

            config = (
                config
                + f"\n **Flow**: {component.flowtype.name} \n \n**Unit:** {component.flowtype.unit.get_unit_flow()}\n \n **Number of Demands:** {len(component.demands)} \n"
            )

            results = f"\n **Total Flow:** {component.flowtype.unit.get_value_expression(round(sum(sum(utilization))), 'flow')}\n \n **power_max:** {component.flowtype.unit.get_value_expression(max(sum(utilization)), 'flowrate')}\n"
        else:
            fig1 = go.Figure()
            fig2 = go.Figure()
            fig3 = go.Figure()
            config = ""
            results = ""

        return fig1, fig2, fig3, config, results

    @app.callback(
        Output(figures["heatpump_utilization"], component_property="figure"),
        Output(figures["heatpump_cop"], component_property="figure"),
        Output(figures["heatpump_cop_profile"], component_property="figure"),
        Output(component_info["heatpump_sum_in"], component_property="children"),
        Output(component_info["heatpump_sum_out"], component_property="children"),
        Output(component_info["heatpump_avg_cop"], component_property="children"),
        Output(component_info["heatpump_cop_range"], component_property="children"),
        Input(dropdowns["heatpump"], component_property="value"),
        Input("timestep_slider_heatpump", "value"),
    )
    def update_plots_heatpump(user_input, timesteps):
        # determine timerange to display
        t0 = timesteps[0]
        t1 = timesteps[1]
        x = np.arange(t0, t1, 1)

        # get heatpump component
        component = simulation.factory.components[
            simulation.factory.get_key(user_input)
        ]

        # CREATE UTILIZATION FIGURE
        input_electricity = (
                simulation.result[component.key]["input_electricity"][t0:t1]
                / simulation.scenario.timefactor
                * simulation.factory.timefactor
        )
        input_heat = (
                simulation.result[component.key]["input_heat"][t0:t1]
                / simulation.scenario.timefactor
                * simulation.factory.timefactor
        )
        output_heat = (
                simulation.result[component.key]["output_heat"][t0:t1]
                / simulation.scenario.timefactor
                * simulation.factory.timefactor
        )

        fig = go.Figure()

        # add trace for electricity input
        fig.add_trace(
            go.Scatter(
                x=x,
                y=input_electricity,
                hoverinfo="x",
                mode="lines",
                stackgroup="one",
                name=f"Electricity Consumption",
                line={"color": component.input_main.flowtype.color.hex},
            )
        )

        # add trace for heat source input
        fig.add_trace(
            go.Scatter(

                x=x,
                y=input_heat,
                hoverinfo="x",
                mode="lines",
                stackgroup="one",
                name=f"Input from Heat Source",
                line={"color": component.input_gains.flowtype.color.hex},
            )
        )

        fig.update_layout(
            figure_config,
            xaxis_title="Timesteps",
            yaxis_title=f"Heat Output [kW]",
            showlegend=True,
        )
        fig.update_xaxes(linewidth=2, linecolor=style["axis_color"])
        fig.update_yaxes(linewidth=2, linecolor=style["axis_color"])

        # CREATE TEMPERATURE AND COP PLOT
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=np.ones(t1 - t0) * component.temperature_source[t0:t1],
                line_color=f"rgb{colors['main']}",
                name="Source Temperature",
            ),
            secondary_y=False,
        )
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=np.ones(t1 - t0) * component.cop[t0:t1],
                line_color="rgb(192,0,0)",
                name="COP",
            ),
            secondary_y=True,
        )
        fig2.update_layout(
            figure_config,
            xaxis_title="Timesteps",
        )

        fig2.update_yaxes(
            title_text=f"Source Temperature [°C]",
            secondary_y=False,
            linewidth=2,
            linecolor=style["axis_color"],
        )

        fig2.update_yaxes(
            title_text=f"Realized COP",
            secondary_y=True,
            linewidth=2,
            linecolor=style["axis_color"],
            range=[1, 7]
        )

        # CREATE COP PROFILE PLOT
        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatter(
                x=np.arange(-273, 173),
                y=component.cop_profile,
                line_color="rgb(192,0,0)",
                name="COP",
            )
        )
        fig3.update_layout(
            figure_config,
            xaxis=dict(title="Source Temperature", range=[-20, 30]),
            yaxis_title=f"COP",
            showlegend=False,
        )



        # COLLECT PARAMETER INFORMATIONS
        heatpump_sum_in = "## " + component.input_main.flowtype.unit.get_value_expression(
            value=round(sum(simulation.result[component.key]["utilization"][t0:t1])),
            quantity_type="flow",
        )

        heatpump_sum_out = "## " + component.input_main.flowtype.unit.get_value_expression(
            value=round(sum(simulation.result[component.key]["output_heat"][t0:t1])),
            quantity_type="flow",
        )

        heatpump_avg_cop = f"## {round(sum(simulation.result[component.key]['utilization'][t0:t1] * component.cop[t0:t1])/sum(simulation.result[component.key]['utilization'][t0:t1]),2)}"

        heatpump_cop_range = f"## {round(min(component.cop[t0:t1]),2)} - {round(max(component.cop[t0:t1]),2)}"


        return fig, fig2, fig3, heatpump_sum_in, heatpump_sum_out, heatpump_avg_cop, heatpump_cop_range

    # Run app
    app.run_server(port=8053)
