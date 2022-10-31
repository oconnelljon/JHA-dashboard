from datetime import date, datetime
import dataretrieval.nwis as nwis
import utils.param_codes as pc
from dash import dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from utils import download, utils
import json

app = dash.Dash()
application = app.server

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    id="H1",
                    children="The QCinator, it's coming for your data!",
                    style={"textAlign": "center", "marginTop": 40, "marginBottom": 40},
                ),
                html.Div(
                    [
                        "Station ID: ",
                        dcc.Input(
                            id="station_ID",
                            value="12323840",
                            debounce=True,
                            inputMode="numeric",
                            autoFocus=True,
                            minLength=8,
                            placeholder="enter station",
                            type="text",
                        ),
                    ]
                ),
                html.Div(
                    [
                        "Select Date Range",
                        dcc.DatePickerRange(
                            id="date_range",
                            start_date=date(2020, 3, 1),
                            end_date=date(2020, 11, 1),
                            initial_visible_month=datetime.now(),
                        ),
                    ],
                ),
                html.Div(
                    [
                        "Select parameter by name: ",
                        dcc.Dropdown(
                            id="param_select",
                            options=pc.param_labels,
                            value="p00400",
                        ),
                    ],
                    style={"width": "49%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        "Filter by sample type: ",
                        dcc.Dropdown(
                            id="sample_code_select",
                            options=pc.sample_codes,
                            value="9",
                        ),
                    ],
                    style={"width": "20%"},
                ),
                dcc.Graph(id="scatter_plot"),
                html.Div(
                    [
                        "Select X axis parameter: ",
                        dcc.Dropdown(
                            id="param_select_X",
                            options=pc.param_labels,
                            value="p00400",
                        ),
                    ]
                ),
                html.Div(
                    [
                        "Select Y axis parameter: ",
                        dcc.Dropdown(
                            id="param_select_Y",
                            options=pc.param_labels,
                            value="p00400",
                        ),
                    ]
                ),
                dcc.Graph(id="plot_X_vs_Y", style={"display": "inline-block"}),
                dcc.Store(id="memory_data", storage_type="memory"),
                dcc.Store(id="filtered_data", storage_type="memory"),
            ]
        ),
    ]
)


@app.callback(
    Output("memory_data", "data"),
    [
        Input("station_ID", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
    ],
)
def get_qw_data(site, start, end):
    df = nwis.get_record(sites=site, service="qwdata", start=start, end=end, access="3")
    return df.to_json()


# @app.callback(
#     Output("filtered_data", "data"),
#     [
#         Input("sample_code_select", "value"),
#         Input("memory_data", "value"),
#     ],
# )
# def filter_qw_data(sample_code, data):
#     df = pd.read_json(data)
#     df = df.loc[df["samp_type_cd"] == sample_code]
#     return df.to_json()


@app.callback(
    Output("scatter_plot", "figure"),
    [
        Input("param_select", "value"),
        Input("memory_data", "data"),
        Input("sample_code_select", "value"),
    ],
)
def plot_parameter(param, data, sample_code):
    df = pd.read_json(data)
    try:
        sample_code = int(sample_code)
        df = df.loc[df["samp_type_cd"] == sample_code]
    except ValueError:
        df = df.loc[df["samp_type_cd"] == sample_code]
    fig = go.Figure(
        [
            go.Scatter(
                mode="markers",
                x=df.index,
                y=df[param],
                name="pH",
            ),
        ],
    )
    fig.update_layout(
        title="",
        xaxis_title="Date",
        yaxis_title=pc.parameters.get(param),
    )
    return fig


@app.callback(
    Output("plot_X_vs_Y", "figure"),
    [
        Input("station_ID", "value"),
        Input("param_select_X", "value"),
        Input("param_select_Y", "value"),
        Input("memory_data", "data"),
    ],
)
def x_vs_y(station, param_x: str, param_y: str, data):
    df = pd.read_json(data)
    fig = go.Figure(
        [
            go.Scatter(
                mode="markers",
                x=df[param_x],
                y=df[param_y],
                name="pH",
            ),
        ],
    )

    x_title = pc.parameters.get(param_x)
    y_title = pc.parameters.get(param_y)
    if len(x_title) > 30:
        x_title = utils.title_wrapper(x_title)
    if len(y_title) > 30:
        y_title = utils.title_wrapper(y_title)

    fig.update_layout(
        title=f"Station: {station}",
        title_x=0.5,
        xaxis_title=x_title,
        yaxis_title=y_title,
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


if __name__ == "__main__":
    app.run()
