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

    figures = {"figure_scenario_corridor": dcc.Graph(figure={}, config=dict(responsive=True), style={'height': '40vh'}),
               "figure_boxplots": dcc.Graph(figure={}, config=dict(responsive=True), style={'height': '70vh'})}

    labels = {"label_simulation_count": dcc.Markdown(style={"marginLeft": "10px"})}

    sliders = {'slider_electricity_price': dcc.RangeSlider(round(min(df["avg_cost_electricity"])), round(max(df["avg_cost_electricity"])), value=[round(min(df["avg_cost_electricity"])), round(max(df["avg_cost_electricity"]))], id='slider_electricity_price'),
               'slider_electricity_volatility': dcc.RangeSlider(min(df["volantility_electricity"]), max(df["volantility_electricity"]), value=[min(df["volantility_electricity"]), max(df["volantility_electricity"])], id='slider_electricity_volatility'),
               'slider_gas_price': dcc.RangeSlider(min(df["cost_natural_gas"]), max(df["cost_natural_gas"]), value=[min(df["cost_natural_gas"]), max(df["cost_natural_gas"])], id='slider_gas_price'),
               'slider_carbon_price': dcc.RangeSlider(min(df["cost_CO2"]), max(df["cost_CO2"]), value=[min(df["cost_CO2"]), max(df["cost_CO2"])], id='slider_carbon_price'),
               'slider_pledged_reduction': dcc.RangeSlider(min(df["co2_reduction"]), max(df["co2_reduction"]), value=[min(df["co2_reduction"]), max(df["co2_reduction"])], id='slider_pledged_reduction')}

    app.layout = html.Div(style={'backgroundColor': style['background'], 'overflow': 'hidden'}, children=[
            dbc.Row(children=[
                dbc.Col(children=[
                    dcc.Markdown(children='## Scenario Selection'),
                    dcc.Markdown(children='##### Electricity Price Range:'),
                    sliders["slider_electricity_price"],
                    dcc.Markdown(children='##### Electricity Volatility Range:'),
                    sliders["slider_electricity_volatility"],
                    dcc.Markdown(children='##### Gas Price Range:'),
                    sliders["slider_gas_price"],
                    dcc.Markdown(children='##### Carbon Price Range:'),
                    sliders["slider_carbon_price"],
                    dcc.Markdown(children='##### Decarbonization Range:'),
                    sliders["slider_pledged_reduction"],
                    labels["label_simulation_count"],
                    figures["figure_scenario_corridor"]],
                    width=3,
                    style=card_style,
                ),
                dbc.Col(children=[figures["figure_boxplots"]],
                        style=card_style,),
                dcc.Graph(id="parallel_coordinates",figure={}, config=dict(responsive=True), style={'height': '70vh'})
            ]),
        ])

    @app.callback(
            Output(figures["figure_scenario_corridor"], component_property='figure'),
            Output(figures["figure_boxplots"], component_property='figure'),
            Output(labels["label_simulation_count"], component_property='children'),
            Input(sliders["slider_electricity_price"], component_property='value'),
            Input(sliders["slider_electricity_volatility"], component_property='value'),
            Input(sliders["slider_gas_price"], component_property='value'),
            Input(sliders["slider_carbon_price"], component_property='value'),
            Input(sliders["slider_pledged_reduction"], component_property='value'))
    def update_plot(range_electricity_price, range_volatility, range_gas_price, range_carbon_price, range_pledged_reduction):
        # initiate figure
        fig = go.Figure()

        # add max-scenario values
        fig.add_trace(go.Scatterpolar(
            r=[range_electricity_price[1]/max(df["avg_cost_electricity"]),
               range_volatility[1]/max(df["volantility_electricity"]),
               range_gas_price[1]/max(df["cost_natural_gas"]),
               range_carbon_price[1]/max(df["cost_CO2"]),
               range_pledged_reduction[1]/max(df["co2_reduction"])],
            theta=['Electricity Price', 'Electricity Market Volatility', 'Natural Gas Price', 'Carbon Price',
                   'Pledged Emission Reduction'],
            fill='toself',
            name='Selected Scenario Range',
            marker=dict(color='blue'),
            line=dict(color='blue')
        ))

        # add min scenario values
        fig.add_trace(go.Scatterpolar(
            r=[range_electricity_price[0] / max(df["avg_cost_electricity"]),
               range_volatility[0] / max(df["volantility_electricity"]),
               range_gas_price[0] / max(df["cost_natural_gas"]),
               range_carbon_price[0] / max(df["cost_CO2"]),
               range_pledged_reduction[0] / max(df["co2_reduction"])],
            theta=['Electricity Price', 'Electricity Market Volatility', 'Natural Gas Price', 'Carbon Price',
                   'Pledged Emission Reduction'],
            fill='toself',
            name='',
            marker=dict(color='white'),
            fillcolor='rgba(255,255,255,1)',
            line=dict(color='white')
        ))

        # Layout anpassen
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                ),
                angularaxis=dict(
                    tickvals=[0, 1, 2, 3, 4],
                    ticktext=[f"Electricity Price {round(max(df["avg_cost_electricity"]))}€",
                              f"Electricity Volatility {max(df["volantility_electricity"])}%",
                              f"Natural gas Price {round(max(df["cost_natural_gas"]),2)}€",
                              f"CO2 Price {max(df["cost_CO2"])}€/ton",
                              f"Pledged CO2 Reduction {max(df["co2_reduction"])}%"]
                )
            )
        )

        # gefilterten dataframe anlegen
        filtered_df = df[
            (df["avg_cost_electricity"].between(range_electricity_price[0], range_electricity_price[1])) &
            (df["volantility_electricity"].between(range_volatility[0], range_volatility[1])) &
            (df["cost_natural_gas"].between(range_gas_price[0], range_gas_price[1])) &
            (df["cost_CO2"].between(range_carbon_price[0], range_carbon_price[1])) &
            (df["co2_reduction"].between(range_pledged_reduction[0], range_pledged_reduction[1]))
            ].copy()

        # string zur Anzeige der resultierenden Datensatzgröße erstellen
        simulation_count = f"### Resulting simulation dataset: {len(filtered_df)}"

        # initiate figure for Boxplot
        fig2 = go.Figure()

        # add boxplots for each layout
        for layout in filtered_df["Layout"].unique():
            fig2.add_trace(go.Box(
                y=filtered_df[filtered_df["Layout"] == layout]["cost_per_ton"],
                name=layout,
                boxmean=True
            ))

        # Layout anpassen
        fig2.update_layout(
            title="Cost per Ton by Layout",
            yaxis_title="Cost per Ton",
            xaxis_title="Layout"
        )

        return fig, fig2, simulation_count

    #
    # fig3 = go.Figure(data=
    # go.Parcoords(
    #     line=dict(color=df['cost_per_ton'],
    #               colorscale='Geyser',
    #               showscale=True,
    #               cmin=0,
    #               cmax=1250),
    #     dimensions=list([
    #         dict(range=[0, 200],
    #              constraintrange=[0, 200],
    #              label="Electricity Price [$/MWh]", values=df['avg_cost_electricity']),
    #         dict(range=[0, 1],
    #              label='Electricity Volatility [%]', values=df['volantility_electricity']),
    #         dict(range=[0, 2500],
    #              label='Cost Natural Gas [$/t]', values=df['cost_natural_gas']),
    #         dict(range=[0, 100],
    #              label='Carbon Price [$/tCO2]', values=df['cost_CO2']),
    #         dict(range=[0, 100],
    #              label='Decarbonization Rate', values=df['co2_reduction']),
    #     ])
    # )
    # )

    # Run app
    app.run_server(port=8053)
