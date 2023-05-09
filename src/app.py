import dash
from dash import html, dcc, Input, Output, State, dash_table, callback_context
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dataretrieval.nwis as nwis

import utils.qwpretreival as qwp
import utils.param_codes as pc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils import utils
from collections import OrderedDict
import requests
import io
from datetime import date, datetime, timedelta
from typing import List
from array import array

# Initialize App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # Include __name__, serves as reference for finding .css files.
app.title = "JHA-USGS Dashboard"

# Set defaults, load local data
# STAID_COORDS = pd.read_csv("src/data/JHA_STAID_INFO.csv")
DEFAULT_PCODE = "p00400"
DEFAULT_STAID = "USGS-433615110440001"
# default_start_year = datetime.today().date() - timedelta(days=365)
default_start_date = pd.Timestamp.today().strftime("%m-%d-%Y")

staid_coords = pd.read_csv("src/data/JHA_STAID_INFO.csv")
staid_coords["staid"] = "USGS-" + staid_coords["staid"].astype(str)  # Need to concat "USGS-" to the start of the staid for qwp query
staid_list = staid_coords["staid"].to_list()

# Query QWP for data
response = requests.post(
    url="https://www.waterqualitydata.us/data/Result/search?",
    data={
        "siteid": [staid_list],
        "startDateLo": "01-01-2020",
        "startDateHi": default_start_date,
        "service": "results",
    },
    headers={"user-agent": "python"},
)

# Load and scrub QWP data
decode_response = io.StringIO(response.content.decode("utf-8"))
dataframe = pd.read_csv(decode_response, dtype={"USGSPCode": str})
dataframe["USGSPCode"] = "p" + dataframe["USGSPCode"]
dataframe.rename(columns={"MonitoringLocationIdentifier": "staid"}, inplace=True)
dataframe["datetime"] = dataframe["ActivityStartDate"] + " " + dataframe["ActivityStartTime/Time"]
dataframe["ValueAndUnits"] = dataframe["ResultMeasureValue"].astype(str) + " " + dataframe["ResultMeasure/MeasureUnitCode"].astype(str)
dataframe.loc[dataframe["ValueAndUnits"] == "nan nan", "ValueAndUnits"] = "No Value"
dataframe.loc[(dataframe["ValueAndUnits"] == "No Value") & (dataframe["ResultDetectionConditionText"] == "Not Detected"), "ValueAndUnits"] = "Not Detected"
dataframe = dataframe.loc[(dataframe["ActivityTypeCode"] == "Sample-Routine")]
dataframe["ResultMeasure/MeasureUnitCode"] = dataframe["ResultMeasure/MeasureUnitCode"].str.replace("asNO2", "as NO2")
dataframe["ResultMeasure/MeasureUnitCode"] = dataframe["ResultMeasure/MeasureUnitCode"].str.replace("asNO3", "as NO3")
dataframe["ResultMeasure/MeasureUnitCode"] = dataframe["ResultMeasure/MeasureUnitCode"].str.replace("asPO4", "as PO4")
dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"].str.replace("asNO2", "as NO2")
dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"].str.replace("asNO3", "as NO3")
dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"].str.replace("asPO4", "as PO4")
dataframe["param_label"] = dataframe["CharacteristicName"] + ", " + dataframe["ResultSampleFractionText"].fillna("") + ", " + dataframe["ResultMeasure/MeasureUnitCode"].fillna("")
dataframe["param_label"] = dataframe["param_label"].str.replace(", , ", ", ")
dataframe["param_label"] = dataframe["param_label"].str.replace("deg C, deg C", "deg C")
dataframe["param_label"] = dataframe["param_label"].str.rstrip(", ")

# Create dictionary of parameter labels and values for the App to display
available_parameters = dataframe.drop_duplicates("param_label")
available_parameters = available_parameters.sort_values(by="param_label", key=lambda col: col.str.lower())
available_param_dict = dict(zip(available_parameters["USGSPCode"], available_parameters["param_label"]))
available_param_labels = [{"label": label, "value": pcode} for label, pcode in zip(available_parameters["param_label"], available_parameters["USGSPCode"])]
# This is all the available data for all the stations.  Hopefully.
# Query all data at the start of the App, then sort intermediates to pass to Callbacks
ALL_DATA = pd.merge(dataframe, staid_coords, on="staid", how="left")
ALL_DATA.sort_values(by="datetime", ascending=True, inplace=True)
ALL_DATA = ALL_DATA.loc[
    :,
    [
        "ActivityStartDate",
        "ActivityStartTime/Time",
        "staid",
        "ResultDetectionConditionText",
        "CharacteristicName",
        "ResultSampleFractionText",
        "ResultMeasureValue",
        "ResultMeasure/MeasureUnitCode",
        "USGSPCode",
        "DetectionQuantitationLimitTypeName",
        "DetectionQuantitationLimitMeasure/MeasureValue",
        "DetectionQuantitationLimitMeasure/MeasureUnitCode",
        "datetime",
        "ValueAndUnits",
        "param_label",
        "dec_lat_va",
        "dec_long_va",
    ],
]

# Setup a dataframe to handle missing values when plotting on the map.
# Every well should plot, and if no data is found, display a black marker and Result = No Data when hovering.
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
        ),
    ],
    className="navbar-container",
)

sidebar_select = html.Aside(
    [
        html.Div(
            [
                html.H1("Station ID"),
                dcc.Checklist(["All"], ["All"], id="all-checklist", inline=True),
                dcc.Checklist(
                    id="station-checklist",
                    options=pc.STATION_LIST,
                    persistence=False,
                ),
            ],
            className="sidebar-sub-container",
            id="station-select-container",
        ),
        html.Div(
            [
                html.H1("Select Date Range"),
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
        # Map
        html.Div(
            [
                html.H1("Location Map"),
                html.P(id="graph-text"),
                html.P(id="graph-text-param", style={"font-weight": "bold", "text-align": "center"}),
                html.Div(id="map-tab-graph", className="map-view-container"),
            ],
            id="sidebar-map-container",
            className="sidebar-sub-container",
        ),
    ],
    className="sidebar-container",
)

scatter_time_container = html.Div(
    [
        html.H1("Time-Series Plot"),
        dcc.Graph(id="scatter_plot", className="scatter-plot"),
    ],
    className="scatter-time-container",
)

scatter_params_container = html.Div(
    [
        html.H1("Comparative Plot"),
        dcc.Graph(id="plot_X_vs_Y"),
    ],
    className="scatter-params-container",
)


application = app.server  # Important for debugging and using Flask!

app.layout = html.Div(
    [
        dcc.Store(id="memory-time-plot", storage_type="memory"),  # Holds plotting data for map
        dcc.Store(id="memory-time-plot-no-data", storage_type="memory"),  # Holds plotting data for map if no data found
        dcc.Store(id="memory-scatter-plot", storage_type="memory"),  # Holds scatter plot x-y data
        html.Div(
            [
                dcc.Location(id="url"),
                navbar,
                html.Main(
                    [
                        sidebar_select,
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H1("Parameter of interest"),
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
                                        html.Div(
                                            [
                                                scatter_time_container,
                                            ],
                                            className="plots-wrapper",
                                        ),
                                        html.Div(
                                            [
                                                html.H1(id="data-table-text"),
                                                dash_table.DataTable(
                                                    id="summary-table",
                                                ),
                                            ],
                                            id="table-container",
                                        ),
                                    ],
                                    className="time-graph-container",
                                ),
                                html.Div(
                                    [
                                        scatter_params_container,
                                        html.Div(
                                            [
                                                html.H1("Scatter X parameter"),
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
                                                html.H1("Scatter Y parameter"),
                                                dcc.Dropdown(
                                                    id="param_select_Y",
                                                    options=available_param_dict,
                                                    value=DEFAULT_PCODE,
                                                ),
                                            ],
                                            className="sidebar-sub-container",
                                            id="select-y-container",
                                        ),
                                    ],
                                    className="plots-wrapper",
                                ),
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
    [
        Output("summary-table", "data"),
        Output("data-table-text", "children"),
    ],
    [
        Input("memory-time-plot", "data"),
        # Input("param_select", "value"),
    ],
)
def summarize_data(mem_data):
    mem_df = pd.read_json(mem_data)
    group_staid = mem_df.groupby(["staid"])
    total_samples = group_staid["dec_lat_va"].count()
    non_detects = group_staid["ResultDetectionConditionText"].count()
    table_median = group_staid["ResultMeasureValue"].median()
    most_recent_sample = group_staid["ActivityStartDate"].max()
    temp_df = pd.merge(total_samples, non_detects, left_index=True, right_index=True)
    temp_df2 = pd.merge(temp_df, table_median, left_index=True, right_index=True)
    my_data = pd.merge(temp_df2, most_recent_sample, left_index=True, right_index=True)

    my_data = my_data.rename(
        columns={
            "ResultMeasureValue": "Median Value",
            "dec_lat_va": "Sample Count",
            "ResultDetectionConditionText": "Not Detected",
            "ActivityStartDate": "Last Sample",
        },
    ).round(3)
    my_data["Station ID"] = my_data.index
    my_data = my_data[["Station ID", "Sample Count", "Not Detected", "Median Value", "Last Sample"]]
    return my_data.to_dict("records"), "Summary Table"


@app.callback(
    Output("station-checklist", "value"),
    Output("all-checklist", "value"),
    Input("station-checklist", "value"),
    Input("all-checklist", "value"),
)
def sync_checklists(staids_selected, all_selected):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "station-checklist":
        all_selected = ["Select All"] if set(staids_selected) == set(pc.STATION_LIST) else []
    else:
        staids_selected = pc.STATION_LIST if all_selected else []
    return staids_selected, all_selected


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
        Input("station-checklist", "value"),
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
    [
        Output("memory-scatter-plot", "data"),
        Output("memory-time-plot-no-data", "data"),
    ],
    [
        Input("station-checklist", "value"),
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
    if staid is None:
        return filtered.to_json(), nodata_df_staids.to_json()
    return filtered.to_json(), nodata_df_staids.loc[nodata_df_staids["Station ID"].isin(staid)].to_json()


@app.callback(
    [
        Output("map-tab-graph", "children"),
        Output("graph-text", "children"),
        Output("graph-text-param", "children"),
    ],
    [
        Input("memory-time-plot", "data"),
        Input("memory-time-plot-no-data", "data"),
        Input("param_select", "value"),
        Input("date_range", "end_date"),
    ],
)
def map_view_map(mem_data, no_data, param, end_date):
    # This is technically a secret, but anyone can request this from mapbox so I'm not concerened about it.
    MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoic2xlZXB5Y2F0IiwiYSI6ImNsOXhiZng3cDA4cmkzdnFhOWhxdDEwOHQifQ.SU3dYPdC5aFVgOJWGzjq2w"
    mem_df = pd.read_json(mem_data)
    no_data = pd.read_json(no_data)
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

    #  Only plot the most recent data on the map.  Since sampling may not occur on the same day,
    #  select the previous 30 days of data to plot.  This should yield 1 point for each well to plot if data is available.

    temp_df = mem_df.groupby("Station ID")["datetime"].max()
    date_filtered_mem_df = mem_df.loc[mem_df["datetime"].isin(list(temp_df.values))]

    # begin_sampling_date = mem_df["datetime"].max() - pd.to_timedelta(30, "days")
    # if begin_sampling_date is not pd.NaT:
    #     date_filtered_mem_df = mem_df.loc[mem_df["datetime"] >= begin_sampling_date].copy()
    # else:
    #     date_filtered_mem_df = mem_df.copy()

    date_filtered_mem_df["Sample Date"] = date_filtered_mem_df["datetime"].astype(str).copy()

    # Debugging helper lines.
    # date_filtered_mem_df[["Station ID", "Sample Date", "Result", "Latitude", "Longitude", "ResultMeasureValue", "ResultMeasure/MeasureUnitCode"]]
    # mem_df = mem_df[["Station ID", "Sample Date", "Result", "Latitude", "Longitude", "ResultMeasureValue", "ResultMeasure/MeasureUnitCode"]]

    fig1 = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,

    # Create figure 1 plot
    fig1 = px.scatter_mapbox(
        no_data,
        lat="Latitude",
        lon="Longitude",
        color="ResultMeasureValue",
        color_continuous_scale=px.colors.sequential.Sunset,
        hover_name="Station ID",
        hover_data={"Result": True, "Sample Date": True, "Latitude": True, "Longitude": True, "ResultMeasureValue": False},
        mapbox_style="streets",
    )

    # Create figure 2 plot
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

    fig1.add_trace(fig2.data[0])  # Overlay real data over No data plot

    # Update marker sizes
    fig1.update_traces(marker={"size": 12})
    fig2.update_traces(marker={"size": 11})

    # Color bar Title, if not available, display nothing, else display units
    if len(date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].array) == 0 or date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].loc[~date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].isnull()].empty:  #  or bool(date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].isnull().array[0])
        color_bar_title = ""
    else:
        color_bar_title = date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].loc[~date_filtered_mem_df["ResultMeasure/MeasureUnitCode"].isnull()].array[0]

    fig1.update_layout(
        autosize=True,
        # title=f"{available_param_dict.get(param)}",
        coloraxis_colorbar=dict(
            title=color_bar_title,
        ),
        hovermode="closest",
        margin=dict(l=5, r=5, t=5, b=5),
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            bearing=0,
            center=dict(
                lat=43.61,
                lon=-110.737,
            ),
            pitch=0,
            zoom=14,
        ),
    )

    return (
        dcc.Graph(id="location-map", figure=fig1, className="THEGRAPH", responsive=True),
        f"Most recent values before {end_date} for:",
        f"{available_param_dict.get(param)}",
    )


@app.callback(
    Output("scatter_plot", "figure"),
    [
        Input("memory-time-plot", "data"),
        Input("param_select", "value"),
    ],
)
def plot_parameter(mem_data, param):
    """Plots parameter as a function of time.

    Parameters
    ----------
    data : JSON
        JSON object from memory-output cache
    param : str
        Parameter code, e.g. p00400 from param_select dropdown

    Returns
    -------
    px.scatter() figure to scatter_plot location
    """
    if mem_data is None:
        raise PreventUpdate
    mem_df = pd.read_json(mem_data)
    mem_df["datetime"] = pd.to_datetime(mem_df["datetime"], format="%Y-%m-%d %H:%M")
    mem_df = mem_df.dropna(subset=["ResultMeasureValue"])

    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter(
        mem_df,
        x="datetime",
        y="ResultMeasureValue",
        color="staid",
        hover_data=dict(
            staid=True,
            datetime=True,
        ),
    )

    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        # title="Time-Series Plot",
        xaxis_title="Sample Date",
        yaxis_title=available_param_dict.get(param),
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
    combined = combined.dropna(subset=["ResultMeasureValue_x", "ResultMeasureValue_y"])
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
        # title="Comparative Parameter Plot",
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


if __name__ == "__main__":
    app.run_server(debug=True)



# 43,36,42.6,-110,44,14.0
# 43,36,14.55,-110,44,2.31
# 43,36,04.2,-110,44,33.5
# 43,36,04.25,-110,44,33.58
# 43,36,04.2,-110,44,33.5
# 43,35,50.69,-110,44,37.54
# 43,35,59.8,-110,44,37.5
# 43,36,2.92,-110,44,37.31
# 43,36,2.65,-110,44,37.45
# 43,36,04.97,-110,44,37.57
# 43,36,12.48,-110,44,37.70
# 43,35,55.94,-110,44,18.76
# 43,36,29.45,-110,44,30.02
# 43,36,3.36,-110,44,12.81
# 43,36,5.64,-110,44,7.94
# 43,36,4.93,-110,44,14.51
# 43,36,2.01,-110,44,14.50
# 43,35,57.57,-110,44,17.43
# 43,36,06.4,-110,44,11.94

# 43.611833333,-110.737222222
# 43.604041667,-110.733975
# 43.601166667,-110.742638889
# 43.601180556,-110.742661111
# 43.601166667,-110.742638889
# 43.597413889,-110.743761111
# 43.599944444,-110.74375
# 43.600811111,-110.743697222
# 43.600736111,-110.743736111
# 43.601380556,-110.743769444
# 43.603466667,-110.743805556
# 43.598872222,-110.738544444
# 43.608180556,-110.741672222
# 43.600933333,-110.736891667
# 43.601566667,-110.735538889
# 43.601369444,-110.737363889
# 43.600558333,-110.737361111
# 43.599325,-110.738175
# 43.601777778,-110.73665
# °
