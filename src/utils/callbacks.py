# callbacks.py
import pandas as pd
from dash import Input, Output
import dash
import plotly.express as px
import plotly.graph_objects as go
import utils.param_codes as pc
from utils import utils


@dash.callback(
    Output("plot_xy", "figure"),
    [
        Input("memory-xy-plot", "data"),
        Input("param_select_x", "value"),
        Input("param_select_y", "value"),
    ],
)
def plot_xy(mem_data, param_x: str, param_y: str):
    mem_df = pd.read_json(mem_data)
    x_data = mem_df.loc[mem_df["USGSPCode"] == param_x]
    y_data = mem_df.loc[mem_df["USGSPCode"] == param_y]
    # y_data = y_data.loc[:,["staid", "datetime", "ResultMeasureValue", "USGSPCode"]]  # Can take out later, just helping debug now.
    combined = pd.merge(x_data, y_data, on="datetime")
    combined = combined.dropna(subset=["ResultMeasureValue_x", "ResultMeasureValue_y"])
    combined.rename(columns={"staid_x": "staid"}, inplace=True)
    combined.rename(columns={"station_nm_x": "station_nm"}, inplace=True)
    # combined_x = combined["ResultMeasureValue_x"].array
    # combined_y = combined["ResultMeasureValue_y"].array
    # combined_color = "station_nm"
    # if combined.empty:
    #     combined_color = array("f", [1.0])
    #     combined_x = array("f", [float("NaN")])
    #     combined_y = array("f", [float("NaN")])

    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter(
        combined,
        x="ResultMeasureValue_x",
        y="ResultMeasureValue_y",
        color="station_nm",
        # """
        # Need to work on labels.
        # Look for more SMCLs
        # other graphs?
        # """
        labels={
            "station_nm": "Station Name",
            "datetime": "Sample Date",
            "staid": "Station ID",
        },
        hover_data=dict(
            station_nm=True,
            staid=True,
            datetime=True,
            ResultMeasureValue_x=False,
            ResultMeasureValue_y=False,
        ),
    )

    try:
        if smcl := pc.SMCL_DICT.get(mem_df.loc[mem_df["USGSPCode"] == param_x]["CharacteristicName"].unique()[0], False):
            fig = utils.add_xline(fig=fig, smcl=smcl)
    except IndexError:
        print("Invalid index, no worries")

    try:
        if smcl := pc.SMCL_DICT.get(mem_df.loc[mem_df["USGSPCode"] == param_y]["CharacteristicName"].unique()[0], False):
            fig = utils.add_yline(fig=fig, smcl=smcl)
    except IndexError:
        print("Invalid index, no worries")

    x_title = str(available_param_dict.get(param_x))
    y_title = str(available_param_dict.get(param_y))
    if len(x_title) > 30:
        x_title = utils.title_wrapper(x_title)
    if len(y_title) > 30:
        y_title = utils.title_wrapper(y_title)

    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        title_x=0.5,
        xaxis_title=x_title,
        yaxis_title=y_title,
        coloraxis_colorbar=dict(
            title="No Data",
        ),
    )
    fig.update_xaxes(
        constrain="domain",
    )
    if param_x == param_y:
        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
        )
    return fig