
import factory_flexibility_model.io.factory_import as imp
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
def create_partial_utilization_plot():
    print("Creating Partial utilization figure")

    for simulation_file in [#"Partial_epex_2023_NG800_EL80_VOL80_CO2150_Reduction0_ElectricityEmissions_0.sim",
                            "Partial_epex_2023_NG800_EL80_VOL80_CO250_Reduction0_ElectricityEmissions_0.sim",
                            #"Partial_epex_2023_NG800_EL80_VOL40_CO250_Reduction0_ElectricityEmissions_0.sim",
                            "Partial_epex_2023_NG800_EL80_VOL80_CO250_Reduction0_ElectricityEmissions_0_with_ramping_cost.sim"]:
        simulation = imp.import_simulation(f"C:\\Users\\smsikamm\\PycharmProjects\\WattsInsight\\simulations\\{simulation_file}")

        hydrogen_dri = simulation.result["connection_20"]
        natural_gas_dri = simulation.result["connection_21"]
        electricity_price = simulation.factory.components['component_1'].cost
        electrolyzer = simulation.result["component_13"]["utilization"]
        hydrogen_storage = simulation.result["component_19"]["SOC"]
        x = np.arange(simulation.factory.timesteps)

        replacement_rate = hydrogen_dri/(hydrogen_dri+natural_gas_dri)

        fig = make_subplots(rows = 3, cols=1, shared_xaxes=True, specs=[[{"secondary_y": True}],
                                                                        [{"secondary_y": True}],
                                                                        [{"secondary_y": True}]])
        fig.update_layout(
            title=simulation_file,
            legend=dict(
                x=1.05,  # Position rechts außerhalb des Plots
                y=0.5,  # Vertikale Position in der Mitte
                xanchor="left",
                yanchor="middle"
            ),
        )
        fig.update_xaxes(showline=True, linecolor="black", linewidth=1, range=[1900, 2100])
        fig.update_yaxes(showline=True, linecolor="black", linewidth=1)
        # yachse des ersten subplots beschränken
        fig.update_yaxes(title_text="DRI Shaft Production [tDri/h]",
                         range=[0, 300], row=1, col=1, secondary_y=False)
        fig.update_yaxes(title_text="Electricity Price [$/MWh]",
                         range=[0, 300], secondary_y=True)

        # print background heatmap
        fig.add_trace(
            go.Heatmap(
                z=[replacement_rate],
                x=x,
                y=[1,300],
                colorscale=[[0, "rgb(102, 194, 165)"], [1,"rgb(252,141,98)"]],
                showscale=True,
                zsmooth="best",
                colorbar=dict(
                    title="",
                    tickvals=[0, 1],
                    ticktext=["100% NG DRI", "100% H₂-DRI"],
                    x=1,  # Position der Farbskala auf der x-Achse
                    y=0.9,  # Position der Farbskala auf der y-Achse (auf Höhe des ersten Subplots)
                    len=0.3,  # Höhe der Farbskala
                    yanchor="middle"
        )
            ),
            secondary_y=False,
            row=1,
            col=1
        )

        # cut heatmap from the top to show total production demand
        fig.add_trace(
            go.Scatter(
                x=x,
                y=hydrogen_dri+natural_gas_dri,
                hoverinfo="x",
                mode="lines",
                stackgroup="one",
                line_shape="hv",
                line={"color": "rgba(120,120,120,1)"},
                fillcolor="rgba(252,141,98,0)",
                name="DRI shaft production rate"
            ),
            secondary_y=False,
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=x,
                y=300-natural_gas_dri-hydrogen_dri,
                hoverinfo="x",
                mode="lines",
                stackgroup="one",
                line_shape="hv",
                line={"color": "white"},
                fillcolor="white",
                showlegend=False,
            ),
            secondary_y=False,
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=x,
                y=electricity_price,
                hoverinfo="x",
                line_color = "red",
                name="Electricity Price",
            ),
            secondary_y=True,
            row=1,
            col=1
        )

        # electrolyzer figure
        fig.update_yaxes(title_text="Electrolyzer utilization [kW]",
                         range=[0, 1200], row=2, col=1, secondary_y=False)

        fig.add_trace(
            go.Scatter(
                x=x,
                y=electrolyzer,
                hoverinfo="x",
                line_shape="hv",
                line_color="blue",
                name="Electrolyzer operation",
            ),
            secondary_y=False,
            row=2,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=x,
                y=electricity_price,
                hoverinfo="x",
                line_color="red",
                name="Electricity Price",
                showlegend=False,
            ),
            secondary_y=True,
            row=2,
            col=1
        )

        # storage plot
        fig.update_yaxes(title_text="Amount of stored Hydrogen [tH2]",
                         range=[0, 200], row=3, col=1, secondary_y=False)
        fig.add_trace(
            go.Scatter(
                x=x,
                y=hydrogen_storage,
                hoverinfo="x",
                mode="lines",
                stackgroup="one",
                name=f"Stored Hydrogen",
                line={"color": "rgba(50, 50, 50,0)"},
            ),
            secondary_y=False,
            row=3,
            col=1
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=electricity_price,
                hoverinfo="x",
                line_color="red",
                name="Electricity Price",
                showlegend=False
            ),
            secondary_y=True,
            row=3,
            col=1
        )

        fig.add_annotation(text="DRI shaft operation", xref="x domain", yref="y domain", x=0.5, y=1.1, row=1, col=1,
                           showarrow=False, font=dict(size=14))
        fig.add_annotation(text="Electrolyzer operation", xref="x domain", yref="y domain", x=0.5, y=1.1, row=2, col=1,
                           showarrow=False, font=dict(size=14))
        fig.add_annotation(text="Hydrogen storage operation", xref="x domain", yref="y domain", x=0.5, y=1.1, row=3,
                           col=1, showarrow=False, font=dict(size=14))

        fig.show()