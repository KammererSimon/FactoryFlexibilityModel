""" FACTORY DASH """
""" This script sets up a webbased dashboard to visualizue the results of a simulation run using plotly dash"""

import copy
import warnings

import dash_bootstrap_components as dbc

# IMPORT 3RD PARTY PACKAGES
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from dash_bootstrap_templates import load_figure_template
from plotly.express.colors import sample_colorscale
from plotly.subplots import make_subplots


# CODE START
def create_dash(simulation):
    pass

    # Check, that simulation has been performed and results are existing
    if not simulation.simulated:
        warnings.warn(
            "Scenario has not been simulated yet. Calling the simulation routine... If you want to execute it with specific parameters do it before calling the show_results-function)"
        )
        simulation.simulate()

    # TODO: Separate the next section into a config file!
    # INITIALIZE APP AND SET LAYOUT
    app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
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
    T = simulation.scenario.number_of_timesteps

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
                "height": "30vh",
            },
        ),
        "thermal2": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "30vh",
            },
        ),
        "schedule1": dcc.Graph(
            figure={},
            config=dict(responsive=True),
            style={
                "height": "30vh",
            },
        ),
        "schedule2": dcc.Graph(
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
        "pool": [],
        "sink": [],
        "source": [],
        "storage": [],
        "slack": [],
        "converter": [],
        "schedule": [],
        "thermalsystem": [],
        "triggerdemand": [],
        "deadtime": [],
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
    app.layout = html.Div(
        style={"backgroundColor": style["background"], "overflow": "hidden"},
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Markdown(children="# FACTORY SIMULATION"), style=style["H1"]
                    )
                ],
            ),
            dcc.Tabs(
                [
                    dcc.Tab(
                        label="OVERVIEW",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### OPTIONS",
                                                        style=style[
                                                            "card_title_contrast"
                                                        ],
                                                    ),
                                                    dcc.Markdown(
                                                        children="##### Select View:",
                                                        style=style["H2"],
                                                    ),
                                                    dropdowns["sankey"],
                                                ],
                                                style=card_style_contrast,
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["pie_in_title"],
                                                    dbc.Row([figures["pie_in"]]),
                                                ],
                                                style=card_style,
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["input_information"],
                                                    dcc.Markdown(
                                                        children="#### TOTAL INFLOW",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                style=card_style_contrast,
                                            ),
                                        ],
                                        width=2,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    component_info["sankey_title"],
                                                    figures["sankey"],
                                                ]
                                            )
                                        ],
                                        width=8,
                                        style=card_style
                                        | {
                                            "backgroundColor": style["card_color"],
                                        },
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    component_info["total_cost"],
                                                    dcc.Markdown(
                                                        children="#### TOTAL OPERATION COST",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                style=card_style_contrast,
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["pie_out_title"],
                                                    dbc.Row([figures["pie_out"]]),
                                                ],
                                                style=card_style,
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info[
                                                        "output_information"
                                                    ],
                                                    dcc.Markdown(
                                                        children="#### TOTAL OUTFLOW",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                align="start",
                                                style=card_style_contrast,
                                            ),
                                        ]
                                    ),
                                ],
                            )
                        ],
                    ),
                    dcc.Tab(
                        label="CONVERTERS",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### OPTIONS",
                                                        style=style[
                                                            "card_title_contrast"
                                                        ],
                                                    ),
                                                    dcc.Markdown(
                                                        children="##### Converter:",
                                                        style=style["H2"],
                                                    ),
                                                    dropdowns["converter"],
                                                    dcc.Markdown(
                                                        children="##### Time interval:",
                                                        style=style["H2"],
                                                    ),
                                                    dcc.RangeSlider(
                                                        0,
                                                        T,
                                                        1,
                                                        value=[0, T],
                                                        updatemode="drag",
                                                        id="timestep_slider_converter",
                                                        marks={0: "0", T: f"{T}"},
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                        },
                                                    ),
                                                ],
                                                style=card_style
                                                | {
                                                    "backgroundColor": style[
                                                        "card_color_dark"
                                                    ]
                                                },
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Row(
                                                        [
                                                            dcc.Markdown(
                                                                children="#### EFFICIENCY",
                                                                style=style[
                                                                    "card_title"
                                                                ],
                                                            )
                                                        ],
                                                    ),  # style={"height": "3vh"}),
                                                    dbc.Row(
                                                        [
                                                            figures[
                                                                "converter_efficiency"
                                                            ]
                                                        ]
                                                    ),
                                                ],
                                                style=card_style,
                                            ),
                                        ],
                                        width=2,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### UTILIZATION",
                                                        style=style["card_title"],
                                                    )
                                                ],
                                            ),
                                            dbc.Row([figures["converter"]]),
                                        ],
                                        width=8,
                                        style=card_style,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### COMPONENT CONFIGURATION",
                                                        style=style["card_title"],
                                                    ),
                                                    component_info["converter_config"],
                                                ],
                                                style=card_style,
                                            ),
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### COMPONENT RESULTS",
                                                        style=style["card_title"],
                                                    ),
                                                    component_info["converter_results"],
                                                ],
                                                style=card_style,
                                            ),
                                        ]
                                    ),
                                ],
                            )
                        ],
                    ),
                    dcc.Tab(
                        label="POOLS",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dcc.Markdown(
                                                children="#### OPTIONS",
                                                style=style["card_title_contrast"],
                                            ),
                                            dcc.Markdown(
                                                children="##### Select Pool:",
                                                style=style["H2"],
                                            ),
                                            dropdowns["pool"],
                                            dcc.Markdown(
                                                children="##### Interpolation:",
                                                style=style["H2"],
                                            ),
                                            dropdowns["linestyle_pool"],
                                            dcc.Markdown(
                                                children="##### Time interval:",
                                                style=style["H2"],
                                            ),
                                            dcc.RangeSlider(
                                                0,
                                                T,
                                                1,
                                                value=[0, T],
                                                id="timestep_slider_pool",
                                                marks={0: "0", T: f"{T}"},
                                                tooltip={
                                                    "placement": "bottom",
                                                    "always_visible": True,
                                                },
                                                updatemode="drag",
                                            ),
                                        ],
                                        width=2,
                                        style=card_style_contrast,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### BILANCE OF INFLOWS AND OUTFLOWS",
                                                        style=style["card_title"],
                                                    )
                                                ],
                                                style={"height": "3vh"},
                                            ),
                                            dbc.Row(
                                                [figures["pool"]],
                                                style={"height": "55vh"},
                                            ),
                                        ],
                                        width=9,
                                        style=card_style,
                                    ),
                                ],
                                style={"height": "86vh"},
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="SOURCES",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### OPTIONS",
                                                        style=style[
                                                            "card_title_contrast"
                                                        ],
                                                    ),
                                                    dcc.Markdown(
                                                        children="##### Component:",
                                                        style=style["H2"],
                                                    ),
                                                    dropdowns["source"],
                                                    dcc.Markdown(
                                                        children="##### Interpolation:",
                                                        style=style["H2"],
                                                    ),
                                                    dropdowns["linestyle_source"],
                                                    dcc.Markdown(
                                                        children="##### Time interval:",
                                                        style=style["H2"],
                                                    ),
                                                    dcc.RangeSlider(
                                                        0,
                                                        T,
                                                        1,
                                                        value=[0, T],
                                                        id="timestep_slider_source",
                                                        marks={0: "0", T: f"{T}"},
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                        },
                                                        updatemode="drag",
                                                    ),
                                                ],
                                                style=card_style_contrast,
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["source_sum"],
                                                    dcc.Markdown(
                                                        children="#### TOTAL INPUT",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                align="start",
                                                style=card_style_contrast,
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["source_minmax"],
                                                    dcc.Markdown(
                                                        children="#### RANGE OF INPUT POWER",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                align="start",
                                                style=card_style_contrast,
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["source_avg"],
                                                    dcc.Markdown(
                                                        children="#### AVERAGE INPUT POWER",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                align="start",
                                                style=card_style_contrast,
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["source_cost"],
                                                    dcc.Markdown(
                                                        children="#### TOTAL COST",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                align="start",
                                                style=card_style_contrast,
                                            ),
                                        ],
                                        width=2,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### UTILIZATION",
                                                        style=style["card_title"],
                                                    ),
                                                    dbc.Row([figures["source"]]),
                                                ],
                                                style=card_style,
                                            ),
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### COST",
                                                        style=style["card_title"],
                                                    ),
                                                    dbc.Row([figures["source_cost"]]),
                                                ],
                                                style=card_style,
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="SINKS",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### OPTIONS",
                                                        style=style["card_title"],
                                                    ),
                                                    dcc.Markdown(
                                                        children="##### Component:",
                                                        style=style["H2"],
                                                    ),
                                                    dropdowns["sink"],
                                                    dcc.Markdown(
                                                        children="##### Interpolation:",
                                                        style=style["H2"],
                                                    ),
                                                    dropdowns["linestyle_sink"],
                                                    dcc.Markdown(
                                                        children="##### Time interval:",
                                                        style=style["H2"],
                                                    ),
                                                    dcc.RangeSlider(
                                                        0,
                                                        T,
                                                        1,
                                                        value=[0, T],
                                                        updatemode="drag",
                                                        id="timestep_slider_sink",
                                                        marks={0: "0", T: f"{T}"},
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                        },
                                                    ),
                                                ],
                                                style=card_style_contrast
                                                | {"height": "26vh"},
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["sink_sum"],
                                                    dcc.Markdown(
                                                        children="#### TOTAL OUTPUT",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                align="start",
                                                style=card_style_contrast
                                                | {"height": "11vh"},
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["sink_minmax"],
                                                    dcc.Markdown(
                                                        children="#### RANGE OF OUTPUT POWER",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                align="start",
                                                style=card_style_contrast
                                                | {"height": "11vh"},
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["sink_avg"],
                                                    dcc.Markdown(
                                                        children="#### AVERAGE OUTPUT POWER",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                align="start",
                                                style=card_style_contrast
                                                | {"height": "11vh"},
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["sink_cost"],
                                                    dcc.Markdown(
                                                        children="#### TOTAL COST/REVENUE",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                align="start",
                                                style=card_style_contrast
                                                | {"height": "11vh"},
                                            ),
                                        ],
                                        width=2,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### UTILIZATION",
                                                        style=style["card_title"],
                                                    )
                                                ],
                                                style={"height": "3vh"},
                                            ),
                                            dbc.Row(
                                                [figures["sink"]],
                                                style={"height": "55vh"},
                                            ),
                                        ],
                                        width=9,
                                        style=card_style,
                                    ),
                                ],
                                style={
                                    "height": "86vh",
                                },
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="STORAGES",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dcc.Markdown(
                                                children="#### OPTIONS",
                                                style=style["card_title"],
                                            ),
                                            dcc.Markdown(
                                                children="##### Storage:",
                                                style=style["H2"],
                                            ),
                                            dropdowns["storage"],
                                            dcc.Markdown(
                                                children="##### Time interval:",
                                                style=style["H2"],
                                            ),
                                            dcc.RangeSlider(
                                                0,
                                                T,
                                                1,
                                                value=[0, T],
                                                id="timestep_slider_storage",
                                                marks={0: "0", T: f"{T}"},
                                                tooltip={
                                                    "placement": "bottom",
                                                    "always_visible": True,
                                                },
                                                updatemode="drag",
                                            ),
                                        ],
                                        width=2,
                                        style=card_style,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### UTILIZATION",
                                                        style=style["card_title"],
                                                    )
                                                ],
                                            ),
                                            dbc.Row(
                                                [figures["storage"]],
                                            ),
                                        ],
                                        width=7,
                                        style=card_style,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### COMPONENT CONFIGURATION",
                                                        style=style["card_title"],
                                                    ),
                                                    component_info["storage_config"],
                                                ],
                                                style=card_style,
                                            ),
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### COMPONENT RESULTS",
                                                        style=style["card_title"],
                                                    ),
                                                    component_info["storage_results"],
                                                ],
                                                style=card_style,
                                            ),
                                        ],
                                        width=2,
                                    ),
                                ],
                            )
                        ],
                    ),
                    dcc.Tab(
                        label="THERMAL SYSTEMS",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dcc.Markdown(
                                                children="#### OPTIONS",
                                                style=style["card_title"],
                                            ),
                                            dcc.Markdown(
                                                children="##### Select Component:",
                                                style=style["H2"],
                                            ),
                                            dropdowns["thermalsystem"],
                                            dcc.Markdown(
                                                children="##### Time interval:",
                                                style=style["H2"],
                                            ),
                                            dcc.RangeSlider(
                                                0,
                                                T,
                                                1,
                                                value=[0, T],
                                                id="timestep_slider_thermal",
                                                marks={0: "0", T: f"{T}"},
                                                tooltip={
                                                    "placement": "bottom",
                                                    "always_visible": True,
                                                },
                                                updatemode="drag",
                                            ),
                                        ],
                                        width=2,
                                        style=card_style,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### UTILIZATION",
                                                        style=style["card_title"],
                                                    )
                                                ],
                                            ),
                                            dbc.Row(
                                                figures["thermal"],
                                                style={
                                                    "backgroundColor": style[
                                                        "card_color"
                                                    ]
                                                },
                                            ),
                                            dbc.Row(
                                                figures["thermal2"],
                                                style={
                                                    "backgroundColor": style[
                                                        "card_color"
                                                    ]
                                                },
                                            ),
                                        ],
                                        width=7,
                                        style=card_style,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### CONFIGURATION",
                                                        style=style["card_title"],
                                                    ),
                                                    component_info["thermal_config"],
                                                ],
                                                style=card_style,
                                            ),
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### RESULTS",
                                                        style=style["card_title"],
                                                    ),
                                                    component_info["thermal_results"],
                                                ],
                                                style=card_style,
                                            ),
                                        ],
                                        width=2,
                                    ),
                                ],
                                style={"height": "66vh"},
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="SCHEDULERS",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### OPTIONS",
                                                        style=style["card_title"],
                                                    ),
                                                    dcc.Markdown(
                                                        children="##### Scheduler:",
                                                        style=style["H2"],
                                                    ),
                                                    dropdowns["schedule"],
                                                    dcc.Markdown(
                                                        children="##### Interpolation:",
                                                        style=style["H2"],
                                                    ),
                                                    dropdowns["linestyle_schedule"],
                                                    dcc.Markdown(
                                                        children="##### Time interval:",
                                                        style=style["H2"],
                                                    ),
                                                    dcc.RangeSlider(
                                                        0,
                                                        T,
                                                        1,
                                                        value=[0, T],
                                                        updatemode="drag",
                                                        id="timestep_slider_schedule",
                                                        marks={0: "0", T: f"{T}"},
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                        },
                                                    ),
                                                ],
                                                style=card_style,
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Row(
                                                        [
                                                            dcc.Markdown(
                                                                children="#### UTILIZATION",
                                                                style=style[
                                                                    "card_title"
                                                                ],
                                                            )
                                                        ],
                                                        style={"height": "3vh"},
                                                    ),
                                                    dbc.Row(
                                                        [figures["schedule2"]],
                                                        style={"height": "26vh"},
                                                    ),
                                                ],
                                                style=card_style | {"height": "30vh"},
                                            ),
                                        ],
                                        width=2,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### UTILIZATION",
                                                        style=style["card_title"],
                                                    )
                                                ],
                                                style={"height": "3vh"},
                                            ),
                                            dbc.Row(
                                                [figures["schedule1"]],
                                                style={"height": "55vh"},
                                            ),
                                        ],
                                        width=7,
                                        style=card_style,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### COMPONENT CONFIGURATION",
                                                        style=style["card_title"],
                                                    ),
                                                    component_info["schedule_config"],
                                                ],
                                                style=card_style | {"height": "30vh"},
                                            ),
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### COMPONENT RESULTS",
                                                        style=style["card_title"],
                                                    ),
                                                    component_info["schedule_results"],
                                                ],
                                                style=card_style | {"height": "30vh"},
                                            ),
                                        ],
                                        width=2,
                                    ),
                                ],
                                style={"height": "86vh"},
                            ),
                        ],
                    ),
                ]
            ),
            dbc.Row(
                dcc.Markdown(
                    children=f"##### FACTORY LAYOUT: {simulation.factory.name} | SCENARIO: {simulation.scenario.name}"
                ),
                style=style["H3"],
            ),
        ],
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
        Output(component_info["output_information"], component_property="children"),
        Output(component_info["total_cost"], component_property="children"),
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
                                    simulation.factory.connections[
                                        i
                                    ].source.component_id,
                                    simulation.factory.connections[i].sink.component_id,
                                    sum(
                                        simulation.result[
                                            simulation.factory.connections[i].name
                                        ]
                                    ),
                                    simulation.factory.connections[i].connection_id,
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
                                    simulation.factory.connections[
                                        i
                                    ].source.component_id,
                                    simulation.factory.connections[i].sink.component_id,
                                    sum(
                                        simulation.result[
                                            simulation.factory.connections[i].name
                                        ]
                                    ),
                                    simulation.factory.connections[i].connection_id,
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
                                simulation.factory.connections[i].source.component_id,
                                simulation.factory.connections[i].sink.component_id,
                                simulation.factory.connections[i].weight_source,
                                simulation.factory.connections[i].connection_id,
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
                    and simulation.factory.connections[i].flowtype.unit.resource_type
                    == "energy"
                ):
                    connection_list = np.append(
                        connection_list,
                        np.array(
                            [
                                [
                                    simulation.factory.connections[
                                        i
                                    ].source.component_id,
                                    simulation.factory.connections[i].sink.component_id,
                                    sum(
                                        simulation.result[
                                            simulation.factory.connections[i].name
                                        ]
                                    ),
                                    simulation.factory.connections[i].connection_id,
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
                    and simulation.factory.connections[i].flowtype.type == "material"
                ):
                    connection_list = np.append(
                        connection_list,
                        np.array(
                            [
                                [
                                    simulation.factory.connections[
                                        i
                                    ].source.component_id,
                                    simulation.factory.connections[i].sink.component_id,
                                    sum(
                                        simulation.result[
                                            simulation.factory.connections[i].name
                                        ]
                                    ),
                                    simulation.factory.connections[i].connection_id,
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
        component_colorlist = []
        for i in simulation.factory.components:
            component_colorlist.append(
                simulation.factory.components[i].flowtype.color.hex
            )  # add fitting color to the colorlist

        fig_sankey = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=70,
                        thickness=20,
                        line=dict(color="grey", width=0.8),
                        label=simulation.factory.component_keys,
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
                        values_in, sum(simulation.result[component.name]["utilization"])
                    )
                    names_in.append(component.name)

                if component.flowtype.is_material() and user_input == "Material Flows":
                    values_in = np.append(
                        values_in, sum(simulation.result[component.name]["utilization"])
                    )
                    names_in.append(component.name)

            if component.type == "sink":
                if component.flowtype.is_energy() and user_input == "Energy Flows":
                    values_out = np.append(
                        values_out,
                        sum(simulation.result[component.name]["utilization"]),
                    )
                    names_out.append(component.name)

                if (
                    not component.flowtype.is_energy()
                    and user_input == "Material Flows"
                ):
                    values_out = np.append(
                        values_out,
                        sum(simulation.result[component.name]["utilization"]),
                    )
                    names_out.append(component.name)
        if user_input == "Energy Losses":
            for c in simulation.factory.connections:
                connection = simulation.factory.connections[c]
                if connection.flowtype.is_energy() and connection.flowtype.is_losses():
                    values_in = np.append(
                        values_in, sum(simulation.result[connection.name])
                    )
                    names_in.append(connection.source.name)
        if user_input == "Material Losses":
            for c in simulation.factory.connections:
                connection = simulation.factory.connections[c]
                if (
                    connection.flowtype.is_material()
                    and connection.flowtype.is_losses()
                ):
                    values_in = np.append(
                        values_in, sum(simulation.result[connection.name])
                    )
                    names_in.append(connection.source.name)
        df_in = {"values": values_in, "names": names_in}
        df_out = {"values": values_out, "names": names_out}

        # create pie descriptions
        title_in = ""
        title_out = ""
        if user_input == "Energy Flows":
            title_in = "##### DISTRIBUTION OF ENERGY INPUTS"
            title_out = "##### DISTRIBUTION OF ENERGY OUTPUTS"
            input_info = f"## {simulation.factory.units['kW'].get_value_expression(sum(values_in), 'flow')}"
            output_info = f"## {simulation.factory.units['kW'].get_value_expression(sum(values_out), 'flow')}"
        elif user_input == "Material Flows":
            title_in = "##### DISTRIBUTION OF MATERIAL INPUTS"
            title_out = "##### DISTRIBUTION OF MATERIAL OUTPUTS"
            input_info = f"## {simulation.factory.units['kg'].get_value_expression(sum(values_in), 'flow')}"
            output_info = f"## {simulation.factory.units['kg'].get_value_expression(sum(values_out), 'flow')}"
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

        total_cost = f"## € {round(simulation.result['objective'])}"

        return (
            fig_sankey,
            fig_pie_in,
            fig_pie_out,
            title_sankey,
            title_in,
            title_out,
            input_info,
            output_info,
            total_cost,
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
            component = simulation.factory.components[user_input]
            Pmin = min(component.power_min)
            if component.power_max_limited:
                Pmax = int(max(component.power_max))
            else:
                Pmax = round(max(simulation.result[component.name]["utilization"])) + 10

            # plot utilization
            data = (
                simulation.result[component.name]["utilization"][t0:t1]
                / simulation.scenario.timefactor
                * simulation.factory.timefactor
            )
            fig = go.Figure()

            # Print Utilization
            if component.power_min_limited:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=component.power_min[t0:t1],
                        line_color="rgb(192,0,0)",
                        name="Pmin",
                        line_dash="dot",
                    )
                )
            if component.power_max_limited:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=component.power_max[t0:t1],
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
                title_text=f"Utilization [SU/Δt]",
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
            config = f"\n **Pnominal**: {component.power_nominal} SU/Δt\n "
            if component.power_max_limited:
                config = (
                    config
                    + f"\n**power_max:** {round(max(component.power_max))} SU/Δt\n "
                )
            else:
                config = config + f"\n**power_max**: Unlimited \n"
            if component.power_min_limited:
                config = (
                    config + f"\n**Pmin**: {round(min(component.power_min))} SU/Δt\n"
                )
            else:
                config = config + f"\n**Pmin**: 0 SU/Δt \n"
            if component.max_pos_ramp_power < 10000000:
                config = (
                    config
                    + f"\n**Fastest Rampup:** {round(component.max_pos_ramp_power)} SU/Δt² \n "
                )
            else:
                config = config + f"\n**Fastest Rampup:** Unlimited \n "
            if component.max_neg_ramp_power < 10000000:
                config = (
                    config
                    + f"\n**Fastest Rampdown:** {round(component.max_neg_ramp_power)} SU/Δt² \n "
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
                + f"\n **Total Conversion**: {round(sum(simulation.result[component.name]['utilization']))} SU \n"
                f"\n **Highest Utilization**: {round(max(simulation.result[component.name]['utilization']))} SU/Δt \n"
                f"\n **Lowest Utilization**: {round(min(simulation.result[component.name]['utilization']))} SU/Δt \n "
                f"\n **Average Utilization**: {round(simulation.result[component.name]['utilization'].mean())} SU/Δt \n"
                f"\n **Activation Time**: {sum(simulation.result[component.name]['utilization'] > 0.001)} Intervals ({round(sum(simulation.result[component.name]['utilization'] > 0.001) / T *100)}% of time)\n"
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
        t0 = timesteps[0]
        t1 = timesteps[1]
        x = np.arange(t0, t1, 1)
        component = simulation.factory.components[user_input]

        fig = go.Figure()
        # create positive side of the diagram
        c = sample_colorscale(
            "darkmint", list(np.linspace(0.3, 1, len(component.inputs)))
        )
        for i in range(0, len(component.inputs)):
            if max(simulation.result[component.inputs[i].name][t0:t1]) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=np.array(simulation.result[component.inputs[i].name][t0:t1])
                        / simulation.scenario.timefactor
                        * simulation.factory.timefactor,
                        hoverinfo="x",
                        mode="lines",
                        stackgroup="one",
                        line_shape=interpolation[linestyle],
                        name=f" Inflow from {component.inputs[i].source.name}",
                        line={"color": c[i]},
                    )
                )

        # create negative side of the diagram
        c = sample_colorscale(
            "peach", list(np.linspace(0.3, 1, len(component.outputs)))
        )
        for i in range(0, len(component.outputs)):
            if max(simulation.result[component.outputs[i].name][t0:t1]) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=-np.array(simulation.result[component.outputs[i].name][t0:t1])
                        / simulation.scenario.timefactor
                        * simulation.factory.timefactor,
                        hoverinfo="x",
                        mode="lines",
                        stackgroup="two",
                        line_shape=interpolation[linestyle],
                        name=f"Outflow to {component.outputs[i].sink.name}",
                        line={"color": c[i]},
                    )
                )

        fig.update_layout(
            figure_config,
            # title_text="BILANCE SUM AT POOL",
            xaxis_title="Simulation interval",
            yaxis_title=f"{component.flowtype.flow_description} [{component.inputs[0].flowtype.unit_flow}]",
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
        component = simulation.factory.components[user_input]
        data = (
            simulation.result[component.name]["utilization"][t0:t1]
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
            yaxis_title=f"{component.flow_description} {component.flowtype.unit_flowrate()}",
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
            yaxis_title=f"€ / {component.flowtype.unit_flow}",
        )

        source_sum = f"## {round(sum(simulation.result[component.name]['utilization'][t0:t1]))} {component.flowtype.unit_flow}"
        source_minmax = f"## {round(min(simulation.result[component.name]['utilization'][t0:t1]))} - {round(max(simulation.result[component.name]['utilization'][t0:t1]))} {component.flowtype.unit_flowrate}"
        source_cost = f"## {round(sum(simulation.result[component.name]['utilization'][t0:t1] * component.cost[t0:t1]))} €"
        if component.power_max_limited:
            source_avg = f"## {round(simulation.result[component.name]['utilization'][t0:t1].mean())} {component.flowtype.unit_flowrate} / {round(((simulation.result[component.name]['utilization'][t0:t1] + 0.000001) / (component.power_max[t0:t1] * component.availability[t0:t1] + 0.000001)).mean() * 100)}%"
        else:
            source_avg = f"## {round(simulation.result[component.name]['utilization'][t0:t1].mean())} {component.flowtype.unit_flowrate}"

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
        component = simulation.factory.components[user_input]
        data = (
            simulation.result[component.name]["utilization"][t0:t1]
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
            yaxis_title=f"{component.flow_description} [{component.flowtype.unit_flowrate}]",
        )
        fig.update_xaxes(linewidth=2, linecolor=style["axis_color"])
        fig.update_yaxes(
            linewidth=2, linecolor=style["axis_color"], range=[0, max(data) * 1.05]
        )

        sink_sum = f"## {round(sum(simulation.result[component.name]['utilization'][t0:t1]))} {component.flowtype.unit_flow}"
        sink_minmax = f"## {round(min(simulation.result[component.name]['utilization'][t0:t1]))} - {round(max(simulation.result[component.name]['utilization'][t0:t1]))} {component.flowtype.unit_flowrate}"

        cost = 0
        if component.chargeable:
            cost += sum(
                simulation.result[component.name]["utilization"][t0:t1]
                * component.cost[t0:t1]
            )
        if component.refundable:
            cost += -sum(
                simulation.result[component.name]["utilization"][t0:t1]
                * component.revenue[t0:t1]
            )
        sink_cost = f"## {round(cost)} €"

        if component.power_max_limited:
            sink_avg = f"## {round(simulation.result[component.name]['utilization'][t0:t1].mean())} {component.flowtype.unit_flowrate} / {round(((simulation.result[component.name]['utilization'][t0:t1] + 0.000001) / (component.power_max[t0:t1] * component.availability[t0:t1] + 0.000001)).mean() * 100)}%"
        else:
            sink_avg = f"## {round(simulation.result[component.name]['utilization'][t0:t1].mean())} {component.flowtype.unit_flowrate}"

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

            component = simulation.factory.components[user_input]

            data = (
                -simulation.result[component.name]["utilization"][t0:t1]
                / simulation.scenario.timefactor
                * simulation.factory.timefactor
            )
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Print SOC in background on secondary axis
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.r_[simulation.result[component.name]["SOC"][t0:t1]],
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
                # title_text="UTILIZATION",
                xaxis_title="Timesteps",
            )
            fig.update_yaxes(
                title_text=f"State of charge [{component.flowtype.unit_flow}]",
                range=[0, component.capacity],
                secondary_y=False,
                linewidth=2,
                linecolor=style["axis_color"],
            )
            fig.update_yaxes(
                title_text=f"Inflow/Outflow [{component.flowtype.unit_flow}]",
                range=[min(data) * 1.1, max(data) * 1.1],
                secondary_y=True,
                linewidth=2,
                linecolor=style["axis_color"],
            )

            inputs = ""
            input_sum = 0
            for i_input in component.inputs:
                inputs += f"\n * {i_input.source.name}\n"
                input_sum += sum(simulation.result[i_input.name])

            outputs = ""
            output_sum = 0
            for i_output in component.outputs:
                outputs += f"\n * {i_output.sink.name}\n"
                output_sum += sum(simulation.result[i_output.name])

            config = (
                f"\n **Capacity:** {component.capacity} {component.flowtype.unit_flow}\n"
                f"\n **Base efficiency:** {component.efficiency * 100} %\n"
                f"\n **SOC_start:** {component.soc_start * component.capacity} {component.flowtype.unit_flow} ({component.soc_start * 100}%)\n"
                f"\n **SOC_end:** {simulation.result[component.name]['SOC'][t1-1]} {component.flowtype.unit_flow} ({(simulation.result[component.name]['SOC'][t1 - 1] - simulation.result[component.name]['utilization'][t1 - 1]) / component.capacity * 100}%)\n"
                f"\n **Leakage per timestep:** \n"
                f"\n * {component.leakage_time} % of total Capacity\n"
                f"\n * {component.leakage_SOC} % of SOC\n"
                f"\n **Max charging Power:** {component.power_max_charge} {component.flowtype.unit_flowrate}\n"
                f"\n **Max discharging Power:** {component.power_max_discharge} {component.flowtype.unit_flowrate}\n"
                f"\n **Inputs:** \n"
                f"\n {inputs} \n"
                f"\n **Outputs:** \n"
                f"\n {outputs} \n"
            )
            results = (
                f"\n **Total Inflow:** {round(input_sum)} {component.flowtype.unit_flow}\n"
                f"\n **Total Outflow:** {round(output_sum)} {component.flowtype.unit_flow}\n"
                f"\n **Occuring Losses:** {round(sum(simulation.result[component.to_losses.name]))} {component.flowtype.unit_flow} ({round(sum(simulation.result[component.to_losses.name]) / input_sum * 100, 2)}%)\n "
                f"\n **Max Input Power:** {-round(min(simulation.result[component.name]['utilization']))} {component.flowtype.unit_flowrate}\n "
                f"\n **Max Output Power:** {round(max(simulation.result[component.name]['utilization']))} {component.flowtype.unit_flowrate}\n "
                f"\n **Average SOC:** {round(simulation.result[component.name]['SOC'].mean())} {component.flowtype.unit_flow}\n "
                f"\n **Charging circles:** {round(input_sum / (component.capacity + 0.0001))} (Estimated) \n "
            )

            # f"\n **Total Cooling:** {round(total_cooling)} {Component.flowtype.unit}\n " \
            # f"\n **Total thermal losses:** {round(sum(simulation.result[Component.to_losses.name]))}{Component.flowtype.unit}\n" \
            # f"\n **Max charging Power:** {round(max(simulation.result[Component.name]['temperature']))} °C\n " \
            # f"\n **T min:** {round(min(simulation.result[Component.name]['temperature']))} °C\n " \
            # f"\n **T average:** {round(simulation.result[Component.name]['temperature'].mean())} °C\n "
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
        t0 = timesteps[0]
        t1 = timesteps[1]
        x = np.arange(t0, t1, 1)
        component = simulation.factory.components[user_input]

        """TEMPERATURE FIGURE"""
        fig1 = make_subplots(specs=[[{"secondary_y": True, "r": -0.06}]])

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
            secondary_y=False,
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
            secondary_y=False,
        )

        # print realized temperature
        fig1.add_trace(
            go.Scatter(
                x=x,
                y=simulation.result[component.name]["temperature"][t0:t1] - 273.15,
                line_color=style["main_color"],
                hoverinfo="x+y",
                mode="lines",
                name="System Temperature",
            ),
            secondary_y=True,
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
            secondary_y=True,
        )

        fig1.update_layout(
            figure_config,
            title_text="TEMPERATURE PROFILE",
            xaxis={"visible": False, "showticklabels": False},
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
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
            secondary_y=False,
        )
        fig1.update_yaxes(
            visible=False,
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
            secondary_y=True,
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
                    y=np.array(simulation.result[component.inputs[i].name][t0:t1])
                    / simulation.scenario.timefactor
                    * simulation.factory.timefactor,
                    hoverinfo="x+y",
                    mode="lines",
                    stackgroup="one",
                    line_shape="hv",
                    name=component.inputs[i].source.name,
                )
            )
            total_heating += sum(simulation.result[component.inputs[i].name])
            inputs += f"\n * {component.inputs[i].source.name}\n"
        # add gains
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=np.array(simulation.result[component.from_gains.name][t0:t1])
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
                    y=-np.array(simulation.result[component.outputs[i].name][t0:t1])
                    / simulation.scenario.timefactor
                    * simulation.factory.timefactor,
                    hoverinfo="x+y",
                    mode="lines",
                    stackgroup="two",
                    line_shape="hv",
                    name=component.outputs[i].name,
                )
            )
            total_cooling += sum(simulation.result[component.outputs[i].name])
            outputs += f"\n * {component.outputs[i].source.name}\n"
        # add losses
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=-np.array(simulation.result[component.to_losses.name][t0:t1])
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
            title_text="HEATING / COOLING / LOSSES",
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
            f"\n **Total Heating:** {round(total_heating)} {component.flowtype.unit_flow}\n "
            f"\n **Total Cooling:** {round(total_cooling)} {component.flowtype.unit_flow}\n "
            f"\n **Total thermal losses:** {round(sum(simulation.result[component.to_losses.name]))}{component.flowtype.unit_flow}\n"
            f"\n **T max:** {round(max(simulation.result[component.name]['temperature'])-273.15)} °C\n "
            f"\n **T min:** {round(min(simulation.result[component.name]['temperature'])-273.15)} °C\n "
            f"\n **T average:** {round(simulation.result[component.name]['temperature'].mean()-273.15)} °C\n "
        )

        return fig1, fig2, config, results

    # TAB: SCHEDULE
    @app.callback(
        Output(figures["schedule1"], component_property="figure"),
        Output(figures["schedule2"], component_property="figure"),
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
            component = simulation.factory.components[user_input]
            fig = make_subplots(
                rows=2, cols=1, subplot_titles=("PARTDEMAND FULLFILMENT", "TOTAL FLOW")
            )
            utilization = simulation.result[component.name]["utilization"].transpose()
            availability = simulation.result[component.name]["availability"].transpose()

            # Create utilization-graph
            data = (
                sum(utilization[:, t0:t1])
                / simulation.scenario.timefactor
                * simulation.factory.timefactor
            )
            if component.power_max_limited:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=np.ones(t1 - t0) * component.power_max[t0:t1],
                        line_color="rgb(192,0,0)",
                        name="power_max",
                        line_dash="dash",
                    ),
                    row=2,
                    col=1,
                )
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=data,
                    line_shape=interpolation[linestyle],
                    line_color=style["main_color_rgb"],
                    name="Utilization",
                ),
                row=2,
                col=1,
            )

            # Create fulfilment-graph
            data2 = copy.copy(utilization[:, t0 : t1 - 1])
            data2[availability[:, t0 : t1 - 1] == 0] = None
            delete = []
            for z in range(len(data2)):
                if np.nansum(data2[z, :]) == 0:
                    delete.append(z)
            data2 = np.delete(data2, delete, 0)
            fig.add_heatmap(
                z=data2[::-1, :],
                colorscale=[[0, "rgb(200,200,200)"], [1, style["main_color_rgb"]]],
                row=1,
                col=1,
                showlegend=False,
                showscale=False,
            )

            fig.update_layout(figure_config)
            fig.update_annotations(font_size=style["diagram_title_size"])
            fig.update_xaxes(
                title_text="",
                linewidth=2,
                linecolor=style["axis_color"],
                showgrid=True,
                showticklabels=False,
                row=1,
                col=1,
            )
            fig.update_xaxes(
                title_text="Simulation interval",
                linewidth=2,
                linecolor=style["axis_color"],
                row=2,
                col=1,
            )
            fig.update_yaxes(
                title_text="Part demands",
                linewidth=2,
                linecolor=style["axis_color"],
                showgrid=False,
                showticklabels=False,
                row=1,
                col=1,
            )
            fig.update_yaxes(
                title_text=f"{component.flow_description} [{component.flowtype.unit_flow}]",
                linewidth=2,
                range=[0, max(sum(utilization)) * 1.05],
                linecolor=style["axis_color"],
                gridcolor=style["grid_color"],
                row=2,
                col=1,
            )

            # create demand heatmap
            # duration=Component
            data3 = np.zeros(
                [max(component.demands[:, 1] - component.demands[:, 0]) + 1, T]
            )
            for i in range(len(component.demands)):
                data3[
                    component.demands[i, 1] - component.demands[i, 0],
                    component.demands[i, 0] - 1,
                ] = component.demands[i, 3]

            fig2 = go.Figure()
            fig2.add_heatmap(
                z=data3[:, t0 : t1 - 1],
                legendgrouptitle={"text": "Amount of demand"},
                colorscale=[[0, "rgb(200,200,200)"], [1, style["main_color_rgb"]]],
            )  # , row=1, col=1,showlegend=False, showscale=False)
            fig2.update_layout(
                figure_config,
                # title_text="DEMANDS",
            )
            fig2.update_yaxes(
                title_text="Available timeinterval for fullfilment",
                linewidth=2,
                linecolor=style["axis_color"],
            )
            fig2.update_xaxes(
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
                    + f"\n**power_max:** {max(component.power_max)} {component.flowtype.unit_flowrate}\n "
                )
            else:
                config = config + f"\n**power_max**: unlimited \n"

            config = (
                config
                + f"\n **Flow**: {component.flowtype.name} \n \n**Unit:** {component.flowtype.unit_flow}\n \n **Number of Demands:** {len(component.demands)} \n"
            )

            results = f"\n **Total Flow:** {round(sum(sum(utilization)))} {component.flowtype.unit_flow}\n \n **power_max:** {max(sum(utilization))}{component.flowtype.unit_flowrate}\n"
        else:
            fig = go.Figure()
            fig2 = go.Figure()
            config = ""
            results = ""

        return fig, fig2, config, results

    # Run app
    app.run_server(port=8053)
