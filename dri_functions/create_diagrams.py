import pandas as pd
import plotly.express as px
import numpy as np
from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import os
from plotly.subplots import make_subplots
from plotly.express.colors import sample_colorscale
import plotly.graph_objects as go
import warnings
import copy

def create_boxplot_dash():
    filepath = f"{os.getcwd()}\\simulations\\output_data\\DRI_Auswertung.xlsx"
    x_parameter = "avg_cost_electricity"
    y_parameter = "electricity_savings_ratio"
    title = "Diagram Title"
    df = pd.read_excel(filepath)
    df = df.drop(df.index[0])

    #df = df[df["cost_CO2"] != 0].copy()
    #df = df[df["cost_CO2"] != 50].copy()
    #df = df[df["cost_natural_gas"] != 200].copy()
    #df = df[df["cost_natural_gas"] != 300].copy()

    app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
    load_figure_template("FLATLY")
    colors = {"main": (29, 66, 118),
            "second": (120, 120, 120),
            "card": (255, 255, 255),
            "text_dark": (156, 156, 156),
            "text_light": (250, 250, 250),
            "background": (240, 240, 240),
            "scale_brightness": [(0, 0, 0),
                                 (13, 24, 33),
                                 (24, 42, 59),
                                 (34, 60, 83),
                                 (49, 86, 119),
                                 (29, 66, 118),
                                 (86, 138, 184),
                                 (122, 163, 199),
                                 (158, 189, 215),
                                 (194, 213, 230),
                                 (255, 255, 255)],
            "scale_saturation": [(0, 84, 156),
                                 (39, 13, 156),
                                 (78, 119, 156),
                                 (117, 137, 156),
                                 (156, 156, 156)]}
    main_font = "helvetica"  # akkurat-light"
    plot_font = "helvetica"
    style = {
        'overflow': 'hidden',
        'background': '#%02x%02x%02x' % colors["background"],
        'card_color': '#%02x%02x%02x' % colors["card"],
        'card_color_dark': '#%02x%02x%02x' % colors["scale_brightness"][5],
        'main_color': '#%02x%02x%02x' % colors["main"],
        'main_color_rgb': f"rgb{colors['main']}",
        'second_color': '#%02x%02x%02x' % colors["second"],
        'second_color_rgb': f"rgb{colors['second']}",
        'text': '#%02x%02x%02x' % colors["text_dark"] ,
        'font': main_font,
        'plot_font': plot_font,
        'axis_color': "grey",
        'grid_color': "lightgrey",
        "diagram_title_size": 30,
        "H1": {"marginTop": "30px", "marginBottom": "30px", "textAlign": "center",
               "color": '#%02x%02x%02x' % colors["main"], "font-family": main_font},
        "H2": {"marginLeft": "10px", "marginTop": "5px", "marginBottom": "0px", "textAlign": "left",
               "color": '#%02x%02x%02x' % colors["scale_brightness"][9], "font-family": main_font},
        "H3": {"marginLeft": "10px", "marginTop": "10px", "marginBottom": "10px", "textAlign": "center",
               "color": colors["second"], "font-family": main_font},
        "card_title": {"marginLeft": "5px", "marginTop": "10px", "marginBottom": "5px", "textAlign": "left",
                       "color": '#%02x%02x%02x' % colors["second"], "font-family": plot_font},
        "card_title_contrast": {"marginLeft": "10px", "marginTop": "20px", "marginBottom": "0px", "textAlign": "left",
                                "color": '#%02x%02x%02x' % colors["text_light"], "font-family": main_font},
        "value_description": {"marginLeft": "10px", "marginTop": "0px", "marginBottom": "0px", "textAlign": "center",
                              "color": '#%02x%02x%02x' % colors["scale_brightness"][9],"font-family": main_font},
        "highlight_value": {"marginLeft": "10px", "marginTop": "50px", "marginBottom": "00px", "textAlign": "center",
                              "color": '#%02x%02x%02x' % colors["scale_brightness"][10], "font-family": main_font, "className": "h-50", "justify": "center"},
        "margins": {"marginLeft": "10px", "marginRight": "10px", "marginTop": "10px", "marginBottom": "10px"},
    }
    figure_config = {"font_size": 18,
                         "font_color": "grey",
                         "paper_bgcolor": style["card_color"],
                         "plot_bgcolor": style["card_color"],
                         "font_family": style["font"],
                         "title_font_size": style["diagram_title_size"],
                         "title_x": 0,
                         "margin": dict(l=5, r=5, t=5, b=5)}
    card_style = {"borderRadius": "1vh", "padding": "1vh", "margin": "1vh", "border": f"0px solid {style['main_color']}", 'backgroundColor': style["card_color"]}
    color_mapping = {
        "DRI_Type_1": "blue",
        "DRI_Type_2": "red",
        "DRI_Type_3": "green",
    }

    figure = dcc.Graph(figure={}, config=dict(responsive=True), style={'height': '90vh'})
    dropdown_x = dcc.Dropdown(options=list(df.head()), value="avg_cost_electricity", clearable=False, style={'width': '80vh'})
    dropdown_y = dcc.Dropdown(options=list(df.head()), value="cost_per_ton", clearable=False, style={'width': '80vh'})

    app.layout = html.Div(style={'backgroundColor': style['background'], 'overflow': 'hidden'}, children=[
            dcc.Markdown(children='##### X-Axes Parameter:'),
            dropdown_x,
            dcc.Markdown(children='##### Y-Axes Parameter:'),
            dropdown_y,
            figure])

    @app.callback(
            Output(figure, component_property='figure'),
            Input(dropdown_x, component_property='value'),
            Input(dropdown_y, component_property='value'))
    def update_plot(x_parameter, y_parameter):
        # CREATE BOXPLOT
        fig = px.box(df,
                     x=x_parameter,
                     y=y_parameter,
                     #box=True,
                     color="Layout",
                     title=title,
                     labels={x_parameter: x_parameter,
                             y_parameter: y_parameter,
                             "Layout": "DRI Type"},
                     points="outliers",
                     category_orders={"Layout": sorted(df["Layout"].unique())},
                     color_discrete_map=color_mapping
                     )
        fig.update_layout(figure_config)
        return fig

    # Run app
    app.run_server(port=8053)
