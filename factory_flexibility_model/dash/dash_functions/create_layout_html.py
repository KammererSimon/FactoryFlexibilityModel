# This script is called on the following paths:
# -> fm.dash.create_dash()

import dash_bootstrap_components as dbc

# IMPORTS
from dash import dcc, html


# CODE START
def create_layout_html(
    style,
    card_style,
    card_style_contrast,
    component_info,
    dropdowns,
    figures,
    simulation,
):
    """
    This function contains the definition of the html-layout of the plotly-dashboard for result visualization.
    It takes all the prepared gui-components with their layout definitions and links them at the correct positions in the layout-tree.

    :param style: [dict] style definitions defined in fm.dash.create_dash()
    :param card_style: [dict] style definitions defined in fm.dash.create_dash()
    :param card_style_contrast: [dict] style definitions defined in fm.dash.create_dash()
    :param component_info [dict] List of prepared string outputs defined in fm.dash.create_dash()
    :param dropdowns: [dict] List of prepared dropdown menus defined in fm.dash.create_dash()
    :param figurese: [dict] List of prepared figures defined in fm.dash.create_dash()
    :param simulation: [fm.simulation-object] fm.Simulation object that the dashboard is visualizing
    :return: plotly-html-layout definition
    """

    # get simulation length
    T = simulation.T

    # define layout
    layout = html.Div(
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
                                                    component_info["detailed_cost"],
                                                ],
                                                style=card_style,
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["total_cost"],
                                                    dcc.Markdown(
                                                        children="#### OPERATION COST",
                                                        style=style[
                                                            "value_description"
                                                        ],
                                                    ),
                                                ],
                                                style=card_style_contrast,
                                            ),
                                            dbc.Row(
                                                [
                                                    component_info["input_information"],
                                                    dcc.Markdown(
                                                        children="#### TOTAL THROUGHPUT",
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
                                        style=card_style
                                        | {
                                            "backgroundColor": style["card_color"],
                                        },
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    component_info["pie_in_title"],
                                                    dbc.Row([figures["pie_in"]]),
                                                ],
                                                style=card_style,
                                            ),
                                        ],
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    component_info["pie_out_title"],
                                                    dbc.Row([figures["pie_out"]]),
                                                ],
                                                style=card_style,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
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
                                                        children="#### THERMAL PROFILE",
                                                        style=style["card_title"],
                                                    ),
                                                    dbc.Row([figures["thermal"]]),
                                                ],
                                                style=card_style,
                                            ),
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### ENERGY FLOWS",
                                                        style=style["card_title"],
                                                    ),
                                                    dbc.Row([figures["thermal2"]]),
                                                ],
                                                style=card_style,
                                            ),
                                        ],
                                        width=7,
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
                                                        [figures["schedule3"]],
                                                        style={"height": "40vh"},
                                                    ),
                                                ],
                                                style=card_style | {"height": "40vh"},
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
                                                style={"height": "40vh"},
                                            ),
                                            dbc.Row(
                                                [figures["schedule2"]],
                                                style={"height": "40vh"},
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
                    dcc.Tab(
                        label="HEATPUMPS",
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
                                                    dropdowns["heatpump"],
                                                    dcc.Markdown(
                                                        children="##### Time interval:",
                                                        style=style["H2"],
                                                    ),
                                                    dcc.RangeSlider(
                                                        0,
                                                        T,
                                                        1,
                                                        value=[0, T],
                                                        id="timestep_slider_heatpump",
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
                                                    component_info["heatpump_sum_in"],
                                                    dcc.Markdown(
                                                        children="#### ELECTRICITY INPUT",
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
                                                    component_info["heatpump_sum_out"],
                                                    dcc.Markdown(
                                                        children="#### TOTAL HEAT OUTPUT",
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
                                                    component_info["heatpump_avg_cop"],
                                                    dcc.Markdown(
                                                        children="#### SEASONAL PERFORMANCE FACTOR",
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
                                                    component_info["heatpump_cop_range"],
                                                    dcc.Markdown(
                                                        children="#### COP RANGE",
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
                                                    dbc.Row(
                                                        [
                                                            dcc.Markdown(
                                                                children="#### COP Profile",
                                                                style=style[
                                                                    "card_title"
                                                                ],
                                                            )
                                                        ],
                                                    ),  # style={"height": "3vh"}),
                                                    dbc.Row(
                                                        [
                                                            figures[
                                                                "heatpump_cop_profile"
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
                                                    ),
                                                    dbc.Row([figures["heatpump_utilization"]]),
                                                ],
                                                style=card_style,
                                            ),
                                            dbc.Row(
                                                [
                                                    dcc.Markdown(
                                                        children="#### SOURCE TEMPERATURE / COP",
                                                        style=style["card_title"],
                                                    ),
                                                    dbc.Row([figures["heatpump_cop"]]),
                                                ],
                                                style=card_style,
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                        ],
                    ),
                ]
            ),
            dbc.Row(
                dcc.Markdown(
                    children=f"##### FACTORY LAYOUT: {simulation.factory.name}"
                ),
                style=style["H3"],
            ),
        ],
    )
    return layout
