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
from array import array

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # Include __name__, serves as reference for finding .css files.
app.title = "JHA-USGS Dashboard"
# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
STAID_COORDS = pd.read_csv("src/data/JHA_STAID_INFO.csv")
DEFAULT_PCODE = "p00400"
DEFAULT_STAID = "USGS-433615110440001"
# default_start_year = datetime.today().date() - timedelta(days=365)
default_start_date = (pd.Timestamp.today() - pd.DateOffset(years=2)).date()


def process_coords():
    coords = pd.read_csv("src/data/JHA_STAID_INFO.csv")
    coords["staid"] = "USGS-" + coords["staid"].astype(str)  # Need to concat "USGS-" to the start of the staid for qwp query
    return coords


staid_coords = process_coords()
staid_list = staid_coords["staid"].to_list()
response = requests.post(
    url="https://www.waterqualitydata.us/data/Result/search?",
    data={
        "siteid": [staid_list],
        # "startDateLo": default_start_date.strftime("%m-%d-%Y"),
        "startDateLo": "01-01-2020",
        "startDateHi": "12-31-2023",
        "service": "results",
    },
    headers={"user-agent": "python"},
)

decode_response = io.StringIO(response.content.decode("utf-8"))
dataframe = pd.read_csv(decode_response, dtype={"USGSPCode": str})
dataframe["USGSPCode"] = "p" + dataframe["USGSPCode"]
dataframe.rename(columns={"MonitoringLocationIdentifier": "staid"}, inplace=True)
dataframe["datetime"] = dataframe["ActivityStartDate"] + " " + dataframe["ActivityStartTime/Time"]
dataframe["ValueAndUnits"] = dataframe["ResultMeasureValue"].astype(str) + " " + dataframe["ResultMeasure/MeasureUnitCode"].astype(str)
dataframe.loc[dataframe["ValueAndUnits"] == "nan nan", "ValueAndUnits"] = "No Value"
dataframe.loc[(dataframe["ValueAndUnits"] == "No Value") & (dataframe["ResultDetectionConditionText"] == "Not Detected"), "ValueAndUnits"] = "Not Detected"
dataframe["param_label"] = dataframe["CharacteristicName"] + ", " + dataframe["ResultSampleFractionText"].fillna("") + ", " + dataframe["ResultMeasure/MeasureUnitCode"].fillna("")
dataframe["param_label"] = dataframe["param_label"].str.replace(", , ", ", ")
dataframe["param_label"] = dataframe["param_label"].str.replace("asNO3", "as NO3")
dataframe["param_label"] = dataframe["param_label"].str.replace("asPO4", "as PO4")
dataframe["param_label"] = dataframe["param_label"].str.replace("deg C, deg C", "deg C")
dataframe["param_label"] = dataframe["param_label"].str.rstrip(", ")

available_parameters = dataframe.drop_duplicates("param_label")
# available_parameters = available_parameters[["USGSPCode", "param_label"]]
available_param_dict = dict(zip(dataframe["USGSPCode"], dataframe["param_label"]))
available_param_labels = [{"label": label, "value": pcode} for label, pcode in zip(available_parameters["param_label"], available_parameters["USGSPCode"])]
# old_params = pc.PARAMETERS

# This is all the available data for all the stations.  Hopefully.
# Query at the start, then sort intermediates to pass to Callbacks
ALL_DATA = pd.merge(dataframe, staid_coords, on="staid", how="left")
ALL_DATA.sort_values(by="datetime", ascending=True, inplace=True)

# Setup a dataframe to handle missing values when plotting on the map.  Every well
# should plot, and if no data is found, display a black marker and Result = No Data when hovering.
nodata_df = pd.DataFrame(
    {
        "staid": pc.STATION_LIST,
        "datetime": ["1970-01-01 00:00:00" for _ in pc.STATION_LIST],
        "ResultMeasureValue": [float("NaN") for _ in pc.STATION_LIST],
        # "USGSPCode": [param for _ in pc.STATION_LIST],
        "Result": ["No Data" for _ in pc.STATION_LIST],
    }
)

nodata_df_staids = pd.merge(nodata_df, staid_coords, on="staid", how="left")
nodata_df_staids = nodata_df_staids.loc[
    :,
    ["staid", "datetime", "Result", "ResultMeasureValue", "dec_lat_va", "dec_long_va"],
]
nodata_df_staids = nodata_df_staids.rename(
    columns={
        "staid": "Station ID",
        "dec_lat_va": "Latitude",
        "dec_long_va": "Longitude",
        "datetime": "Sample Date",
    }
)

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
                html.P("Station ID: "),
                dcc.Dropdown(
                    id="station_ID",
                    options=pc.STATION_LIST,
                    persistence=False,
                    multi=True,
                ),
            ],
            className="sidebar-sub-container",
            id="station-select-container",
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
            className="sidebar-sub-container",
            id="daterange-container",
        ),
        html.Div(
            [
                "Time plot and map view parameter: ",
                dcc.Dropdown(
                    id="param_select",
                    options=available_param_dict,
                    value=DEFAULT_PCODE,
                    persistence=True,
                ),
            ],
            className="sidebar-sub-container",
            id="select-time-param-container",
        ),
        html.Div(
            [
                "Scatter X parameter: ",
                dcc.Dropdown(
                    id="param_select_X",
                    options=available_param_dict,
                    value=DEFAULT_PCODE,
                ),
            ],
            className="sidebar-sub-container",
            id="select-x-container",
        ),
        html.Div(
            [
                "Scatter Y parameter: ",
                dcc.Dropdown(
                    id="param_select_Y",
                    options=available_param_dict,
                    value=DEFAULT_PCODE,
                ),
            ],
            className="sidebar-sub-container",
            id="select-y-container",
        ),
        # Map
        html.Div(id="map-tab-graph", className="map-view-container"),
        # Download button/modal section
        html.Div(
            [
                dbc.Button("Download", color="primary", id="download-button", n_clicks=0),
                dbc.Modal(
                    [
                        dbc.ModalBody(
                            [
                                dbc.Label("Download all data."),
                                html.Div(
                                    [
                                        dbc.Button("Download", color="primary", id="download-modal-button", n_clicks=0),
                                        dcc.Download(id="download-dataframe-csv"),
                                        dbc.Button("Cancel", id="cancel-button", n_clicks=0),
                                    ],
                                    id="modal-button-container",
                                ),
                            ],
                        )
                    ],
                    id="download-modal-container",
                    is_open=False,
                ),
            ],
            className="sidebar-download-container",
            id="download-button-container",
        )
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
# map_view = html.Div(id="map-tab-graph", className="map-view-container")

application = app.server  # Important for debugging and using Flask!

app.layout = html.Div(
    [
        dcc.Store(id="memory-time-plot", storage_type="memory"),
        dcc.Store(id="memory-scatter-plot", storage_type="memory"),
        html.Div(
            [
                dcc.Location(id="url"),
                navbar,
                html.Main(
                    [
                        sidebar_select,
                        html.Div(
                            [
                                scatter_time_container,
                                scatter_params_container,
                            ],
                            className="graph-content-container",
                        ),
                    ],
                    className="main-container",
                ),
            ],
            className="page-container",
        ),
    ],
    className="root",
)


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-modal-button", "n_clicks"),
    prevent_initial_call=True,
)
def user_download(n_clicks):
    return dcc.send_data_frame(ALL_DATA.to_csv, "You_data.csv")


@app.callback(
    Output("download-modal-container", "is_open"),
    [Input("download-button", "n_clicks"), Input("cancel-button", "n_clicks")],
    [State("download-modal-container", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    return not is_open if n1 or n2 else is_open


@app.callback(
    Output("memory-time-plot", "data"),
    [
        Input("station_ID", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
        Input("param_select", "value"),
    ],
)
def filter_timeplot_data(staid, start_date, end_date, param):
    # .isin() method needs a list for querying properly.
    if isinstance(staid, str):
        staid = [staid]
    if not staid:
        staid = pc.STATION_LIST
    # filtered = ALL_DATA.loc[(ALL_DATA["ActivityStartDate"] >= str(start_date)) & (ALL_DATA["ActivityStartDate"] <= str(end_date)) & (ALL_DATA["staid"].isin([staid])) & (ALL_DATA["USGSPCode"] == param)]
    pcode_mask = ALL_DATA["USGSPCode"] == param
    staid_date_mask = (ALL_DATA["staid"].isin(staid)) & (ALL_DATA["ActivityStartDate"] >= str(start_date)) & (ALL_DATA["ActivityStartDate"] <= end_date)

    # mask = ((ALL_DATA["staid"].isin([staid])) & (ALL_DATA["ActivityStartDate"] >= str(start_date)) & (ALL_DATA["ActivityStartDate"] <= end_date) | (ALL_DATA["USGSPCode"] == param_x) | (ALL_DATA["USGSPCode"] == param_y))
    filtered_all_data = ALL_DATA.loc[staid_date_mask & pcode_mask]
    # x_data = filtered_all_data.loc[:, ["staid", "datetime", "ResultMeasureValue", "USGSPCode"]]
    return filtered_all_data.to_json()


@app.callback(
    Output("memory-scatter-plot", "data"),
    [
        Input("station_ID", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
        Input("param_select_X", "value"),
        Input("param_select_Y", "value"),
    ],
)
def filter_scatter_data(staid, start_date, end_date, param_x, param_y):
    # .isin() method needs a list for querying properly.
    if isinstance(staid, str):
        staid = [staid]
    if not staid:
        staid = pc.STATION_LIST
    pcode_mask = (ALL_DATA["USGSPCode"] == param_x) | (ALL_DATA["USGSPCode"] == param_y)
    staid_date_mask = (ALL_DATA["staid"].isin(staid)) & (ALL_DATA["ActivityStartDate"] >= str(start_date)) & (ALL_DATA["ActivityStartDate"] <= end_date)

    # mask = ((ALL_DATA["staid"].isin([staid])) & (ALL_DATA["ActivityStartDate"] >= str(start_date)) & (ALL_DATA["ActivityStartDate"] <= end_date) | (ALL_DATA["USGSPCode"] == param_x) | (ALL_DATA["USGSPCode"] == param_y))
    filtered = ALL_DATA.loc[staid_date_mask & pcode_mask]
    # filtered = ALL_DATA.loc[(ALL_DATA["staid"].isin([staid])) & (ALL_DATA["USGSPCode"] == param_x) | (ALL_DATA["USGSPCode"] == param_y)]
    # (ALL_DATA["ActivityStartDate"] >= str(start_date)) & (ALL_DATA["ActivityStartDate"] <= end_date) &
    return filtered.to_json()


@app.callback(
    Output("map-tab-graph", "children"),
    [
        Input("memory-time-plot", "data"),
        Input("param_select", "value"),
        Input("date_range", "end_date"),
    ],
)
def map_view_map(mem_data, param, end_date):
    # This is technically a secret, but anyone can request this from mapbox so I'm not concerened about it.
    MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoic2xlZXB5Y2F0IiwiYSI6ImNsOXhiZng3cDA4cmkzdnFhOWhxdDEwOHQifQ.SU3dYPdC5aFVgOJWGzjq2w"
    if mem_data is None:
        raise PreventUpdate
    mem_df = pd.read_json(mem_data)
    # mem_df = mem_df.astype({"staid": str, "dec_lat_va": float, "dec_long_va": float, "datetime": str})
    mem_df.rename(
        columns={
            "staid": "Station ID",
            "dec_lat_va": "Latitude",
            "dec_long_va": "Longitude",
            "ValueAndUnits": "Result",
        },
        inplace=True,
    )
    mem_df = mem_df[["Station ID", "datetime", "Result", "Latitude", "Longitude", "ResultMeasureValue", "ResultMeasure/MeasureUnitCode"]]
    begin_sampling_date = mem_df["datetime"].max() - pd.to_timedelta(30, "days")
    if begin_sampling_date is not pd.NaT:
        date_filtered_mem_df = mem_df.loc[mem_df["datetime"] >= begin_sampling_date].copy()
    else:
        date_filtered_mem_df = mem_df.copy()
    date_filtered_mem_df["Sample Date"] = date_filtered_mem_df["datetime"].astype(str)
    # date_filtered_mem_df[["Station ID", "Sample Date", "Result", "Latitude", "Longitude", "ResultMeasureValue", "ResultMeasure/MeasureUnitCode"]]
    # mem_df = mem_df[["Station ID", "Sample Date", "Result", "Latitude", "Longitude", "ResultMeasureValue", "ResultMeasure/MeasureUnitCode"]]
    fig1 = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,

    fig1 = px.scatter_mapbox(
        nodata_df_staids,
        lat="Latitude",
        lon="Longitude",
        color="ResultMeasureValue",
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_name="Station ID",
        hover_data={"Result": True, "Sample Date": True, "Latitude": True, "Longitude": True, "ResultMeasureValue": False},
        mapbox_style="streets",
    )

    fig2 = px.scatter_mapbox(
        date_filtered_mem_df,
        lat="Latitude",
        lon="Longitude",
        color="ResultMeasureValue",
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_name="Station ID",
        hover_data={"Result": True, "Sample Date": True, "Latitude": True, "Longitude": True, "ResultMeasureValue": False},
        mapbox_style="streets",
    )

    fig1.add_trace(fig2.data[0])
    fig1.update_traces(marker={"size": 12})
    # mem_df = mem_df.astype({"STAID": str, "Latitude": str, "Longitude": str, "Datetime": str})
    # Color bar Title, if not available, display nothing, else display units
    if len(date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].array) == 0 or date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].loc[~date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].isnull()].empty:  #  or bool(date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].isnull().array[0])
        color_bar_title = ""
    else:
        color_bar_title = date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].loc[~date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].isnull()].array[0]
    fig1.update_layout(
        # coloraxis_showscale=False,
        # overwrite=True,
        autosize=True,
        title=f"Most recent values before {end_date} for {available_param_dict.get(param)}",
        coloraxis_colorbar=dict(
            title=color_bar_title,
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

    return dcc.Graph(id="location-map", figure=fig1, className="THEGRAPH", responsive=True)


@app.callback(
    Output("scatter_plot", "figure"),
    [
        Input("memory-time-plot", "data"),
        # Input("station_ID", "value"),
        Input("param_select", "value"),
    ],
)
def plot_parameter(mem_data, param):  # , stations: List, param: str, sample_code: int = 9
    """Plots parameter as a function of time.

    Parameters
    ----------
    data : JSON
        JSON object from memory-output cache
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
    if mem_data is None:
        raise PreventUpdate
    mem_df = pd.read_json(mem_data)
    mem_df["datetime"] = pd.to_datetime(mem_df["datetime"], format="%Y-%m-%d %H:%M")

    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter(
        mem_df,
        x="datetime",
        y="ResultMeasureValue",
        color="staid",
        # hover_name="STAID",
        # hover_data=["STAID", "Datetime", param],
        hover_data=dict(
            staid=True,
            datetime=True,
            # sample_dt=False,
        ),
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        title="",
        xaxis_title="Date",
        yaxis_title=available_param_dict.get(param),  # mem_df["USGSPCode"].iloc[0]
    )
    return fig


@app.callback(
    Output("plot_X_vs_Y", "figure"),
    [
        Input("memory-scatter-plot", "data"),
        Input("param_select_X", "value"),
        Input("param_select_Y", "value"),
    ],
)
def x_vs_y(mem_data, param_x: str, param_y: str):
    mem_df = pd.read_json(mem_data)
    x_data = mem_df.loc[mem_df["USGSPCode"] == param_x]
    # x_data = x_data.loc[:,["staid", "datetime", "ResultMeasureValue", "USGSPCode"]]  # Can take out later, just helping debug now.

    y_data = mem_df.loc[mem_df["USGSPCode"] == param_y]
    # y_data = y_data.loc[:,["staid", "datetime", "ResultMeasureValue", "USGSPCode"]]  # Can take out later, just helping debug now.
    combined = pd.merge(x_data, y_data, on="datetime")
    combined.rename(columns={"staid_x": "staid"}, inplace=True)
    combined_x = combined["ResultMeasureValue_x"].array
    combined_y = combined["ResultMeasureValue_y"].array
    combined_color = "staid"
    if combined.empty:
        combined_color = array("f", [1.0])
        combined_x = array("f", [float("NaN")])
        combined_y = array("f", [float("NaN")])

    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter(
        combined,
        x=combined_x,
        y=combined_y,
        color=combined_color,
        # hover_data=dict(
        #     staid=True,
        #     datetime=True,
        # ),
    )

    x_title = str(available_param_dict.get(param_x))
    y_title = str(available_param_dict.get(param_y))
    if len(x_title) > 30:
        x_title = utils.title_wrapper(x_title)
    if len(y_title) > 30:
        y_title = utils.title_wrapper(y_title)

    fig.update_layout(
        # title=f"Station: {station}",
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


if __name__ == "__main__":
    # app.run_server()
    app.run_server(debug=True)
