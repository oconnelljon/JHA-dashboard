import io
import configparser
from array import array
from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dash import Input, Output, State, callback_context, dash, dash_table, dcc, html
from dash.exceptions import PreventUpdate

import utils.param_codes as pc
from utils import utils

config = configparser.ConfigParser()
config.read("config.cfg")

# Initialize App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # Include __name__, serves as reference for finding .css files.
app.title = "JHA Dashboard"

# Set defaults, load local data
DEFAULT_PCODE = config["DEFAULTS"]["DEFAULT_PCODE"]
default_start_date_lo = config["DEFAULTS"]["default_start_date_lo"]
default_start_date_hi = config["DEFAULTS"]["default_start_date_hi"]
# default_start_date = pd.Timestamp.today().strftime("%m-%d-%Y")

staid_meta_data = pd.read_csv(config["DEFAULTS"]["staid_metadata"])
STAID_LIST = list(staid_meta_data["staid"])
STATION_NMs = list(staid_meta_data["station_nm"])
# STATION_NMs.sort()
# staid_coords["staid"] = "USGS-" + staid_coords["staid"].astype(str)  # Need to concat "USGS-" to the start of the staid for qwp query
# staid_list = staid_coords["staid"].to_list()

# Query QWP for data
response = requests.post(
    url="https://www.waterqualitydata.us/data/Result/search?",
    data={
        "siteid": [STAID_LIST],
        "startDateLo": default_start_date_lo,
        "startDateHi": default_start_date_hi,
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
ALL_DATA = pd.merge(dataframe, staid_meta_data, on="staid", how="left")
ALL_DATA.sort_values(by="datetime", ascending=True, inplace=True)
ALL_DATA = ALL_DATA.loc[
    :,
    [
        "ActivityStartDate",
        "ActivityStartTime/Time",
        "staid",
        "station_nm",
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

nodata_df_staids =  utils.make_nodata_df(STATION_NMs, staid_meta_data)

parameter_of_interest_text = "Select a parameter of interest to populate the Time-Series and Box plots.  Only selected stations and data within the time range are displayed."
time_plot_text = "The Time-Series Plot shows the values for the Parameter of Interest for the selected stations across the selected time range."
box_plot_text = "Box plots show the distribution of data for the entire selected time range.  The longer the box, the larger the variation in the data."
scatter_x_y_text = "The scatter plot displays data from the above drop down menues on their respective axis'. Only selected stations and data within the time range are displayed."
scatter_x_y_z_text = "Plot X vs Y data with a third parameter that controls the size of the plot marker."
summary_table_text = "The Summary Table contains general information about the selected stations in the time range for the Parameter of Interest.  Stations with no data are not displayed."

navbar = html.Div(
    [
        html.Div(
            # html.Div("USGS"),
            html.Img(src=app.get_asset_url("usgs-logo.png")),
            className="navbar-brand-container",
        ),
        # html.Img(src=app.get_asset_url('jh-airport-logo.svg')),
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
                                        dbc.Button("Close", id="cancel-button", n_clicks=0),
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
            className="navbar-download-container",
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
                    options=STATION_NMs,
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
                html.H2("Location Map"),
                html.P(id="map-text"),
                html.P(id="graph-text-param", style={"font-weight": "bold", "text-align": "center"}),
                html.Div(id="map-tab-graph", className="map-view-container"),
            ],
            id="sidebar-map-container",
            className="sidebar-sub-container",
        ),
    ],
    className="sidebar-container",
)

application = app.server  # Important for debugging and using Flask!

app.layout = html.Div(
    [
        dcc.Store(id="memory-PoI-data", storage_type="memory"),  # Holds plotting data for map
        dcc.Store(id="memory-time-plot-no-data", storage_type="memory"),  # Holds plotting data for map if no data found
        dcc.Store(id="memory-xy-plot", storage_type="memory"),  # Holds scatter plot x-y data
        html.Div(
            [
                dcc.Location(id="url"),
                navbar,
                html.Div(
                    [
                        sidebar_select,
                        html.Main(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H1("Parameter of interest"),
                                                html.Div(
                                                    [
                                                        dcc.Dropdown(
                                                            id="param_select",
                                                            options=available_param_dict,
                                                            value=DEFAULT_PCODE,
                                                            persistence=True,
                                                            clearable=False,
                                                        ),
                                                    ],
                                                    id="main-parameter-dropdown",
                                                ),
                                                html.Div(
                                                    [
                                                        html.H2("Time-Series Plot"),
                                                        dcc.Graph(id="plot_param_ts", className="scatter-plot"),
                                                        html.P(
                                                            time_plot_text,
                                                            className="plot-text",
                                                        ),
                                                    ],
                                                    className="plots-wrapper",
                                                ),
                                                html.Div(
                                                    [
                                                        html.H2("Box Plot"),
                                                        dcc.Graph(id="plot_box", className="box-plot"),
                                                        html.P(
                                                            box_plot_text,
                                                            className="plot-text",
                                                        ),
                                                    ],
                                                    className="plots-wrapper",
                                                ),
                                                html.Div(
                                                    [
                                                        html.H2(id="data-table-text"),
                                                        dash_table.DataTable(
                                                            id="summary-table",
                                                            sort_action="native",
                                                        ),
                                                        html.P(
                                                            summary_table_text,
                                                            className="plot-text",
                                                        ),
                                                    ],
                                                    className="table-container",
                                                ),
                                            ],
                                            className="tile-container",
                                        ),
                                        html.Div(
                                            [
                                                html.H1("Comparative Plots"),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.H2("Scatter X parameter"),
                                                                dcc.Dropdown(
                                                                    id="param_select_x",
                                                                    options=available_param_dict,
                                                                    value="p00400",
                                                                    clearable=False,
                                                                ),
                                                            ],
                                                            className="main-content-dropdown",
                                                            id="select-x-container",
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.H2("Scatter Y parameter"),
                                                                dcc.Dropdown(
                                                                    id="param_select_y",
                                                                    options=available_param_dict,
                                                                    value="p00300",
                                                                    clearable=False,
                                                                ),
                                                            ],
                                                            className="main-content-dropdown",
                                                            id="select-y-container",
                                                        ),
                                                        dcc.Graph(id="plot_xy"),
                                                        html.P(
                                                            scatter_x_y_text,
                                                            className="plot-text",
                                                        ),
                                                    ],
                                                    className="plots-wrapper",
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.H2("Scatter X parameter"),
                                                                dcc.Dropdown(
                                                                    id="param_select_xx",
                                                                    options=available_param_dict,
                                                                    value="p00400",
                                                                    clearable=False,
                                                                ),
                                                            ],
                                                            className="main-content-dropdown",
                                                            id="select-xx-container",
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.H2("Scatter Y parameter"),
                                                                dcc.Dropdown(
                                                                    id="param_select_yy",
                                                                    options=available_param_dict,
                                                                    value="p00300",
                                                                    clearable=False,
                                                                ),
                                                            ],
                                                            className="main-content-dropdown",
                                                            id="select-yy-container",
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.H2("Bubble size parameter"),
                                                                dcc.Dropdown(
                                                                    id="param_select_zz",
                                                                    options=available_param_dict,
                                                                    value="p00095",
                                                                    clearable=False,
                                                                ),
                                                            ],
                                                            className="main-content-dropdown",
                                                            id="select-zz-container",
                                                        ),
                                                        dcc.Graph(id="plot_xyz"),
                                                        html.P(
                                                            scatter_x_y_z_text,
                                                            className="plot-text",
                                                        ),
                                                    ],
                                                    className="plots-wrapper",
                                                ),
                                            ],
                                            className="tile-container",
                                        ),
                                    ],
                                    className="main-content-container",
                                ),
                            ],
                            className="main-body-container",
                        ),
                    ],
                    className="body-container",
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
        Input("memory-PoI-data", "data"),
        Input("param_select", "value"),
    ],
)
def summarize_data(mem_data, param) -> tuple:
    """Summarizes selected data into descriptive table

    Parameters
    ----------
    mem_data : _type_
        memory data input from Dash

    Returns
    -------
    tuple
        Tuple of summary data to be placed in Dash table and summary text
    """
    mem_df = pd.read_json(mem_data)
    group_staid = mem_df.groupby(["staid"])

    station_nms = group_staid["station_nm"].first()
    station_nms = station_nms.rename("Station Name")

    total_samples = group_staid["dec_lat_va"].count()
    total_samples = total_samples.rename("Sample Count")

    non_detects = group_staid["ResultDetectionConditionText"].count()
    non_detects = non_detects.rename("Not Detected")

    table_median = group_staid["ResultMeasureValue"].median().round(3)
    table_median = table_median.rename("Median Value")

    last_sample = group_staid["ActivityStartDate"].max()
    last_sample = last_sample.rename("Latest Sample")

    first_sample = group_staid["ActivityStartDate"].min()
    first_sample = first_sample.rename("First Sample")

    my_data = pd.concat([station_nms, total_samples, non_detects, table_median, first_sample, last_sample], axis=1)

    my_data["Station ID"] = my_data.index
    my_data = my_data[["Station Name", "Station ID", "Latest Sample", "First Sample", "Sample Count", "Not Detected", "Median Value"]]
    return my_data.to_dict("records"), f"Summary Table for data from {group_staid['ActivityStartDate'].min().min()} to {group_staid['ActivityStartDate'].max().max()} for {available_param_dict[param]}"


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
        all_selected = ["Select All"] if set(staids_selected) == set(STATION_NMs) else []
    else:
        staids_selected = STATION_NMs if all_selected else []
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
    Output("memory-PoI-data", "data"),
    [
        Input("station-checklist", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
        Input("param_select", "value"),
    ],
)
def filter_PoI_data(station_nm, start_date, end_date, param):
    # .isin() method needs a list for querying properly.
    if isinstance(station_nm, str):
        station_nm = [station_nm]
    # if not staid:
    #     staid = pc.STATION_LIST
    # filtered = ALL_DATA.loc[(ALL_DATA["ActivityStartDate"] >= str(start_date)) & (ALL_DATA["ActivityStartDate"] <= str(end_date)) & (ALL_DATA["staid"].isin([staid])) & (ALL_DATA["USGSPCode"] == param)]
    pcode_mask = ALL_DATA["USGSPCode"] == param
    staid_date_mask = (ALL_DATA["station_nm"].isin(station_nm)) & (ALL_DATA["ActivityStartDate"] >= str(start_date)) & (ALL_DATA["ActivityStartDate"] <= end_date)

    # mask = ((ALL_DATA["staid"].isin([staid])) & (ALL_DATA["ActivityStartDate"] >= str(start_date)) & (ALL_DATA["ActivityStartDate"] <= end_date) | (ALL_DATA["USGSPCode"] == param_x) | (ALL_DATA["USGSPCode"] == param_y))
    filtered_all_data = ALL_DATA.loc[staid_date_mask & pcode_mask]
    # x_data = filtered_all_data.loc[:, ["staid", "datetime", "ResultMeasureValue", "USGSPCode"]]
    return filtered_all_data.to_json()


@app.callback(
    [
        Output("memory-xy-plot", "data"),
        Output("memory-time-plot-no-data", "data"),
    ],
    [
        Input("station-checklist", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
        Input("param_select_x", "value"),
        Input("param_select_y", "value"),
    ],
)
def filter_scatter_data(station_nm, start_date, end_date, param_x, param_y):
    # .isin() method needs a list for querying properly.
    if isinstance(station_nm, str):
        station_nm = [station_nm]

    pcode_mask = (ALL_DATA["USGSPCode"] == param_x) | (ALL_DATA["USGSPCode"] == param_y)
    staid_date_mask = (ALL_DATA["station_nm"].isin(station_nm)) & (ALL_DATA["ActivityStartDate"] >= str(start_date)) & (ALL_DATA["ActivityStartDate"] <= end_date)

    filtered = ALL_DATA.loc[staid_date_mask & pcode_mask]
    if station_nm is None:
        return filtered.to_json(), nodata_df_staids.to_json()
    return filtered.to_json(), nodata_df_staids.loc[nodata_df_staids["Station Name"].isin(station_nm)].to_json()


@app.callback(
    [
        Output("map-tab-graph", "children"),
        Output("map-text", "children"),
        Output("graph-text-param", "children"),
    ],
    [
        Input("memory-PoI-data", "data"),
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
            "station_nm": "Station Name",
            "dec_lat_va": "Latitude",
            "dec_long_va": "Longitude",
            "ValueAndUnits": "Result",
        },
        inplace=True,
    )
    mem_df = mem_df[["Station Name", "datetime", "Result", "Latitude", "Longitude", "ResultMeasureValue", "ResultMeasure/MeasureUnitCode"]]

    #  Only plot the most recent data on the map.  Since sampling may not occur on the same day,
    #  select the previous 30 days of data to plot.  This should yield 1 point for each well to plot if data is available.

    temp_df = mem_df.groupby("Station Name")["datetime"].max()
    date_filtered_mem_df = mem_df.loc[mem_df["datetime"].isin(list(temp_df.values))]
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
        hover_name="Station Name",
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
        hover_name="Station Name",
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
                lat=43.609,
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
    Output("plot_param_ts", "figure"),
    [
        Input("memory-PoI-data", "data"),
        Input("param_select", "value"),
    ],
)
def plot_param_ts(mem_data, param):
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
    # mem_df["datetime"] = pd.to_datetime(mem_df["datetime"], format="%Y-%m-%d %H:%M")
    mem_df = mem_df.dropna(subset=["ResultMeasureValue"])

    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter(
        mem_df,
        x="datetime",
        y="ResultMeasureValue",
        color="station_nm",
        labels={
            "station_nm": "Station Name",
            "datetime": "Sample Date",
            "staid": "Station ID",
            "ValueAndUnits": "Result",
        },
        hover_data=dict(
            station_nm=True,
            staid=True,
            datetime=True,
            ValueAndUnits=True,
            ResultMeasureValue=False,
        ),
    )

    try:
        if smcl := pc.SMCL_DICT.get(mem_df.loc[mem_df["USGSPCode"] == param]["CharacteristicName"].unique()[0], False):
            fig.add_hline(
                y=smcl,
                annotation_text=f"EPA SDWR: {smcl}",
            )
        if param == "p00300":
            fig.add_hline(
                y=0.5,  # 0.5 mg/L is Anoxic
                annotation_text="Anoxic: 0.5",
            )
    except IndexError:
        print("Invalid index, no worries")

    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        xaxis_title="Sample Date",
        yaxis_title=available_param_dict.get(param),
    )
    return fig


@app.callback(
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


@app.callback(
    Output("plot_xyz", "figure"),
    [
        Input("station-checklist", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
        Input("param_select_xx", "value"),
        Input("param_select_yy", "value"),
        Input("param_select_zz", "value"),
    ],
)
def plot_xyz(checklist, start_date, end_date, param_x: str, param_y: str, param_z: str):
    mem_df = utils.filter_scatter(ALL_DATA, checklist, start_date, end_date, param_x, param_y, param_z)
    x_data = mem_df.loc[mem_df["USGSPCode"] == param_x]
    x_data = x_data.rename(columns={"ResultMeasureValue": "ResultMeasureValue_x"})
    y_data = mem_df.loc[mem_df["USGSPCode"] == param_y]
    y_data = y_data.rename(columns={"ResultMeasureValue": "ResultMeasureValue_y"})
    z_data = mem_df.loc[mem_df["USGSPCode"] == param_z]
    z_data = z_data.rename(columns={"ResultMeasureValue": "ResultMeasureValue_z"})
    # y_data = y_data.loc[:,["staid", "datetime", "ResultMeasureValue", "USGSPCode"]]  # Can take out later, just helping debug now.
    combined = x_data.merge(y_data, on="datetime").merge(z_data, on="datetime")
    combined = combined[["datetime", "ResultMeasureValue_x", "ResultMeasureValue_y", "ResultMeasureValue_z", "station_nm_x", "staid_x"]]
    # combined = combined.rename(columns={"station_nm_x": "Station Name", "staid_x": "staid"})
    combined_x = combined["ResultMeasureValue_x"].array
    combined_y = combined["ResultMeasureValue_y"].array
    combined_z = combined["ResultMeasureValue_z"].fillna(0)
    combined_z = combined_z.array
    combined_color = "station_nm_x"
    if combined.empty:
        combined_color = array("f", [1.0])
        combined_x = array("f", [float("NaN")])
        combined_y = array("f", [float("NaN")])
        combined_z = array("f", [1])

    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter(
        combined,
        x=combined_x,
        y=combined_y,
        size=combined_z,
        color=combined_color,
        labels={
            "station_nm_x": "Station Name",
            "datetime": "Sample Date",
            "staid_x": "Station ID",
        },
        hover_data=dict(
            station_nm_x=True,
            staid_x=True,
            datetime=True,
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
    z_title = str(available_param_dict.get(param_z))
    if len(x_title) > 30:
        x_title = utils.title_wrapper(x_title)
    if len(y_title) > 30:
        y_title = utils.title_wrapper(y_title)
    if len(z_title) > 30:
        z_title = utils.title_wrapper(z_title)

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


@app.callback(
    Output("plot_box", "figure"),
    [
        Input("memory-PoI-data", "data"),
        Input("param_select", "value"),
    ],
)
def plot_box(mem_data, param):
    mem_df = pd.read_json(mem_data)
    mem_df["datetime"] = pd.to_datetime(mem_df["datetime"], format="%Y-%m-%d %H:%M")
    mem_df = mem_df.dropna(subset=["ResultMeasureValue"])
    mem_df = mem_df.rename(
        columns={
            "station_nm": "Station Name",
        },
    )
    fig = px.box(mem_df, x="Station Name", y="ResultMeasureValue", color="Station Name")

    fig.update_layout(yaxis_title=str(available_param_dict.get(param)))

    try:
        if smcl := pc.SMCL_DICT.get(mem_df.loc[mem_df["USGSPCode"] == param]["CharacteristicName"].unique()[0], False):
            fig = utils.add_yline(fig=fig, smcl=smcl)
    except IndexError:
        print("Invalid index, no worries")

    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
    )
    return fig


if __name__ == "__main__":
        app.run_server(debug=False)