import dash
from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dataretrieval.nwis as nwis

import utils.qwpretreival as qwp
import utils.param_codes as pc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils import utils
import json
import requests
import io
from datetime import date, datetime, timedelta
from typing import List

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # Include __name__, serves as reference for finding .css files.
# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
STAID_coords = pd.read_csv("src/data/JHA_STAID_INFO.csv")


def process_coords():
    coords = pd.read_csv("src/data/JHA_STAID_INFO.csv")
    coords["STAID"] = "USGS-" + coords["STAID"].astype(str)
    return coords


staid_coords = process_coords()
staid_list = staid_coords["STAID"].to_list()
response = requests.post(
    url="https://www.waterqualitydata.us/data/Result/search?",
    data={
        "siteid": [staid_list],
        "startDateLo": "01-01-2005",
        "startDateHi": "12-31-2023",
        "service": "results",
    },
)

decode_response = io.StringIO(response.content.decode("utf-8"))
dataframe = pd.read_csv(decode_response)
dataframe["STAID"] = dataframe["STAID"].astype(str)


navbar = html.Div(
    [
        html.Div(
            html.Div("USGS"),
            className="navbar-brand-container",
        ),
        html.Div(
            html.Div("Jackson Hole Airport"),
            className="navbar-JHA-container",
        ),
        html.Div(
            html.Ul(
                # [html.Li(dbc.NavLink("Item 1")), html.Li(dbc.NavLink("Item 2"))],
                className="navlink-list",
            ),
            className="navbar-link-container",
        ),
    ],
    className="navbar-container",
)

sidebar_select = html.Aside(
    [
        html.Div(
            [
                html.P("Data Access Level"),
                dcc.Dropdown(
                    id="access_dropdown",
                    value="0",
                    options=pc.access_level_codes,
                    persistence=True,
                ),
            ],
            className="data-access-container",
        ),
        html.Div(
            [
                html.P("Station ID: "),
                dcc.Dropdown(
                    id="station_ID",
                    value="433641110441501",
                    options=pc.station_list,
                    persistence=True,
                    multi=True,
                ),
            ],
            className="station-select-container",
        ),
        html.Div(
            [
                html.P("Select Date Range"),
                dcc.DatePickerRange(
                    id="date_range",
                    start_date=datetime.now().date() - timedelta(days=1460),
                    end_date=datetime.now().date(),
                    initial_visible_month=datetime.now(),
                    persistence=True,
                    style={
                        "color": "#333",
                    },
                ),
            ],
            className="daterange-container",
        ),
        html.Div(
            [
                "Time plot and map view parameter: ",
                dcc.Dropdown(
                    id="param_select",
                    options=pc.param_labels,
                    value="p00400",
                    persistence=True,
                ),
            ],
            className="select-time-param-container",
            # style={"width": "49%", "display": "inline-block"},
        ),
        html.Div(
            [
                "Scatter X parameter: ",
                dcc.Dropdown(
                    id="param_select_X",
                    options=pc.param_labels,
                    value="p00400",
                ),
            ],
            className="select-x-container",
        ),
        html.Div(
            [
                "Scatter Y parameter: ",
                dcc.Dropdown(
                    id="param_select_Y",
                    options=pc.param_labels,
                    value="p00400",
                ),
            ],
            className="select-y-container",
        ),
        # dcc.Graph(id="sidebar-location-map", figure=create_map()),
    ],
    className="sidebar-container",
)

scatter_time_container = html.Div(
    [
        dcc.Graph(id="scatter_plot", className="scatter-plot"),
    ],
    className="scatter-time-container",
)

scatter_params_container = html.Div(
    [
        dcc.Graph(id="plot_X_vs_Y"),
    ],
    className="scatter-params-container",
)

# expand on this for map view tab
map_view = html.Div(id="map-tab-graph", className="map-view-container")

tabs = dcc.Tabs(
    [
        dcc.Tab(  # located in tabpanel tab-1 aka "Map view"
            map_view,
            label="Map view",
        ),
        dcc.Tab(  # located in tabpanel tab-0 aka "Graph view"
            [
                scatter_time_container,
                scatter_params_container,
            ],
            label="Graph view",
            className="tab0-graph-view",
        ),
    ],
    # id="tabs-main-container",  # dash appends -parent to this ID and creates a parent to hold tabs-main-container child
    # parent_className="tabs-tab-container",  # Contains tabs and tab content
    className="tabs-container",  # container for Tabs buttons only
    # tabs-content Div container created by dbc.Tabs and holds the dbc.Tab objects
)

application = app.server  # Important for debugging and using Flask!

app.layout = html.Div(
    [
        # dcc.Store(id="staid_coords", storage_type="memory"),
        dcc.Store(id="memory_data", storage_type="memory"),
        # State("map_view_cache", "data"),
        html.Div(
            [
                dcc.Location(id="url"),
                navbar,
                sidebar_select,
                html.Main(
                    html.Div(
                        tabs,
                        className="tabs-content-container",
                    ),
                    className="main-content-container",
                ),
            ],
            className="page-container",
        ),
    ],
    className="root",
)


@app.callback(
    Output("memory_data", "data"),
    [
        Input("staid_coords", "data"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
        Input("access_dropdown", "value"),
    ],
)
def get_qwp_data(coord_data, start, end):
    staids = process_coords(coord_data=coord_data)
    response = requests.post(url="https://www.waterqualitydata.us/data/Result/search?", data={"siteid": [staids], "startDateLo": start, "startDateHi": end, "service": "results"})
    decode_response = io.StringIO(response.content.decode("utf-8"))

    dataframe = pd.read_csv(decode_response)
    dataframe["STAID"] = dataframe["STAID"].astype(str)
    return dataframe.to_json()
    # coords["STAID"] = coords["STAID"].astype(str)
    # df2 = df.copy()
    # dataframe = pd.merge(dataframe, coords, on="STAID", how="left")


@app.callback(
    Output("map-tab-graph", "children"),
    [
        Input("memory_data", "data"),
        Input("param_select", "value"),
        Input("date_range", "end_date"),
    ],
)
def map_view_map(mem_data, param, end_date):
    MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoic2xlZXB5Y2F0IiwiYSI6ImNsOXhiZng3cDA4cmkzdnFhOWhxdDEwOHQifQ.SU3dYPdC5aFVgOJWGzjq2w"
    mem_df = pd.read_json(mem_data)
    mem_df = mem_df.astype({"STAID": str, "Latitude": float, "Longitude": float, "Datetime": str})

    # fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = go.Figure(
        data=px.scatter_mapbox(
            mem_df,
            lat="Latitude",
            lon="Longitude",
            color=param,
            color_continuous_scale=px.colors.sequential.Sunset,
            hover_name="STAID",
            hover_data=["Latitude", "Longitude", "Datetime", param],
            mapbox_style="streets",
        ),
        # layout={"legend": go.layout.Legend(title="git sum")},
    )
    fig.update_traces(
        marker={"size": 12},
    )
    # mem_df = mem_df.astype({"STAID": str, "Latitude": str, "Longitude": str, "Datetime": str})
    fig.update_layout(
        # coloraxis_showscale=False,
        # overwrite=True,
        autosize=True,
        title=f"Most recent values before {end_date} for {pc.parameters.get(param)}",
        coloraxis_colorbar=dict(
            title="",
        ),
        # legend=dict(title="mouse mouse"),
        # legend=go.layout.Legend(title="git sum"),
        # legend_title_text="git sum",
        hovermode="closest",
        margin=dict(l=10, r=10, t=50, b=10),
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            bearing=0,
            center=dict(
                lat=43.608685,
                lon=-110.736564,
            ),
            pitch=0,
            zoom=13.25,
        ),
    )

    return dcc.Graph(id="location-map", figure=fig, className="THEGRAPH", responsive=True)  # style={"width": "60vw", "height": "70vh"}


@app.callback(
    Output("staid_coords", "data"),
    Input("access_dropdown", "value"),
)
def load_local_staids(local_csv: str):
    df = pd.read_csv("src/data/JHA_STAID_INFO.csv")
    return df.to_json()


# @app.callback(
#     Output("memory_data", "data"),
#     [
#         Input("staid_coords", "data"),
#         Input("date_range", "start_date"),
#         Input("date_range", "end_date"),
#         Input("access_dropdown", "value"),
#     ],
# )
# def get_nwis_qw_data(coord_data, start, end, access):
#     coords = pd.read_json(coord_data)
#     site_list = coords["STAID"].astype(str).tolist()
#     df = nwis.get_record(sites=site_list, service="qwdata", start=start, end=end, access=access, datetime_index=False)  # parameterCd=99162, no "p" when querying.
#     if isinstance(df.index, pd.MultiIndex):
#         for station in site_list:
#             df.loc[df.index.get_level_values("site_no") == station, "STAID"] = station
#     else:
#         df["STAID"] = df["site_no"]
#     df["STAID"] = df["STAID"].astype(str)
#     coords["STAID"] = coords["STAID"].astype(str)
#     # df2 = df.copy()
#     df = pd.merge(df, coords, on="STAID", how="left")
#     df.rename({"dec_long_va": "Longitude", "dec_lat_va": "Latitude"}, axis=1, inplace=True)
#     df["Datetime"] = df["sample_dt"] + " " + df["sample_tm"]
#     return df.to_json()


@app.callback(
    Output("scatter_plot", "figure"),
    [
        Input("memory_data", "data"),
        Input("station_ID", "value"),
        Input("param_select", "value"),
    ],
)
def plot_parameter(data, stations: List, param: str, sample_code: int = 9):
    """Plots parameter as a function of time.

    Parameters
    ----------
    data : JSON
        JSON object from memory_data cache
    stations : List
        List of STAIDS from station_ID multi-dropdown
    param : str
        Parameter code, e.g. p00400 from param_select dropdown
    sample_code : int, optional
        Sample code to filter data set, by default 9

    Returns
    -------
    px.scatter() figure to scatter_plot location
    """
    mem_df = pd.read_json(data)
    mem_df = mem_df.astype({"STAID": str, "Latitude": float, "Longitude": float, "Datetime": str})

    mem_df = mem_df.loc[mem_df["STAID"].isin(stations)]
    mem_df["sample_dt"] = pd.to_datetime(mem_df["sample_dt"], format="%Y-%m-%d")
    try:
        mem_df = mem_df.loc[mem_df["samp_type_cd"] == sample_code]
    except ValueError:
        mem_df = mem_df.loc[mem_df["samp_type_cd"] == sample_code]

    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter(
        mem_df,
        x="sample_dt",
        y=param,
        color="STAID",
        # hover_name="STAID",
        # hover_data=["STAID", "Datetime", param],
        hover_data=dict(
            STAID=True,
            Datetime=True,
            sample_dt=False,
        ),
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        title="",
        xaxis_title="Date",
        yaxis_title=pc.parameters.get(param),
    )
    return fig


@app.callback(
    Output("plot_X_vs_Y", "figure"),
    [
        Input("memory_data", "data"),
        Input("station_ID", "value"),
        Input("param_select_X", "value"),
        Input("param_select_Y", "value"),
    ],
)
def x_vs_y(data, stations, param_x: str, param_y: str):
    mem_df = pd.read_json(data)
    mem_df = mem_df.astype({"STAID": str, "Latitude": float, "Longitude": float, "Datetime": str})
    mem_df = mem_df.loc[mem_df["STAID"].isin(stations)]
    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter(
        mem_df,
        x=param_x,
        y=param_y,
        color="STAID",
        hover_data=dict(
            STAID=True,
            Datetime=True,
        ),
    )

    x_title = str(pc.parameters.get(param_x))
    y_title = str(pc.parameters.get(param_y))
    if len(x_title) > 30:
        x_title = utils.title_wrapper(x_title)
    if len(y_title) > 30:
        y_title = utils.title_wrapper(y_title)

    fig.update_layout(
        # title=f"Station: {station}",
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
    # app.run_server()
    app.run_server(debug=True)
