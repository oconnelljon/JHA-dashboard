# callbacks.py
from array import array

import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import utils.epa_codes as pc
from dash import Input, Output, State, callback_context, dash, dcc
from dash.exceptions import PreventUpdate
from natsort import index_natsorted, natsorted
from utils import common, data
from utils.settings import MAPBOX_ACCESS_TOKEN, MAPBOX_BASELAYER_STYLE


@dash.callback(
    [
        Output("summary-table", "data"),
        Output("data-table-text", "children"),
    ],
    [
        Input("memory-PoI-data", "data"),
        Input("param-select", "value"),
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

    table_min = group_staid["ResultMeasureValue"].min().round(3)
    table_min = table_min.rename("Min Value")

    table_max = group_staid["ResultMeasureValue"].max().round(3)
    table_max = table_max.rename("Max Value")

    last_sample = group_staid["ActivityStartDate"].max()
    last_sample = last_sample.rename("Latest Sample")

    first_sample = group_staid["ActivityStartDate"].min()
    first_sample = first_sample.rename("First Sample")

    my_data = pd.concat(
        [
            station_nms,
            total_samples,
            non_detects,
            table_median,
            table_min,
            table_max,
            first_sample,
            last_sample,
        ],
        axis=1,
    )

    my_data["Station ID"] = my_data.index
    my_data = my_data[
        [
            "Station Name",
            "Station ID",
            "Latest Sample",
            "First Sample",
            "Sample Count",
            "Not Detected",
            "Median Value",
            "Min Value",
            "Max Value",
        ]
    ]
    my_data = my_data.sort_values(
        by="Station Name",
        key=lambda x: np.argsort(
            index_natsorted(my_data["Station Name"]),
        ),
    )
    return (
        my_data.to_dict("records"),
        f"Summary Table for data from {group_staid['ActivityStartDate'].min().min()} to {group_staid['ActivityStartDate'].max().max()} for {data.available_param_dict[param]}",
    )


@dash.callback(
    Output("station-checklist", "value"),
    Output("all-checklist", "value"),
    Input("station-checklist", "value"),
    Input("all-checklist", "value"),
)
def sync_checklists(staids_selected, all_selected):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "station-checklist":
        all_selected = (
            ["Select All"] if set(staids_selected) == set(data.STATION_NMs) else []
        )
    else:
        staids_selected = data.STATION_NMs if all_selected else []
    return staids_selected, all_selected


@dash.callback(
    Output("download-query-data-csv", "data"),
    [
        Input("memory-PoI-data", "data"),
        Input("download-query-button", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def user_all_data_download(mem_data, _):
    mem_df = pd.read_json(mem_data)
    return dcc.send_data_frame(mem_df.to_csv, "You_data.csv")


@dash.callback(
    Output("download-all-data-csv", "data"),
    Input("download-all-button", "n_clicks"),
    prevent_initial_call=True,
)
def user_queried_data_download(_):
    return dcc.send_data_frame(data.ALL_DATA_DF.to_csv, "You_data.csv")


@dash.callback(
    Output("download-modal-container", "is_open"),
    [Input("download-button", "n_clicks"), Input("cancel-button", "n_clicks")],
    [State("download-modal-container", "is_open")],
)
def toggle_download_modal(n1, n2, is_open):
    return not is_open if n1 or n2 else is_open


@dash.callback(
    Output("info-modal", "is_open"),
    [Input("info-button", "n_clicks"), Input("cancel-button", "n_clicks")],
    [State("info-modal", "is_open")],
)
def toggle_info_modal(n1, n2, is_open):
    return not is_open if n1 or n2 else is_open


@dash.callback(
    Output("poi-tile", "is_open"),
    [Input("poi-collapse-button", "n_clicks")],
    [State("poi-tile", "is_open")],
)
def poi_toggle_collapse(n, is_open):
    return not is_open if n else is_open


@dash.callback(
    Output("comp-tile", "is_open"),
    [Input("comp-collapse-button", "n_clicks")],
    [State("comp-tile", "is_open")],
)
def comp_toggle_collapse(n, is_open):
    return not is_open if n else is_open


@dash.callback(
    Output("memory-PoI-data", "data"),
    [
        Input("station-checklist", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("param-select", "value"),
    ],
)
def filter_x_data(station_nm, start_date, end_date, param_x):
    """Provides filtered data for PoI and mapbox plots"""
    if isinstance(station_nm, str):
        station_nm = [station_nm]
    pcode_mask = data.ALL_DATA_DF["USGSPCode"] == param_x
    staid_date_mask = (
        (data.ALL_DATA_DF["station_nm"].isin(station_nm))
        & (data.ALL_DATA_DF["ActivityStartDate"] >= str(start_date))
        & (data.ALL_DATA_DF["ActivityStartDate"] <= end_date)
    )
    filtered_all_data = data.ALL_DATA_DF.loc[staid_date_mask & pcode_mask]
    return filtered_all_data.to_json()


@dash.callback(
    [
        Output("memory-xy-plot", "data"),
        Output("memory-time-plot-no-data", "data"),
    ],
    [
        Input("station-checklist", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("param_select_x", "value"),
        Input("param_select_y", "value"),
    ],
)
def filter_scatter_data(station_nm, start_date, end_date, param_x, param_y):
    """Filter all and no data dataframes based on station selection, start date,
    end date, and two parameters

    Parameters
    ----------
    station_nm : _type_
        List of stadion id's in the format USGS-XXXXXXXX
    start_date : _type_
        _description_
    end_date : _type_
        _description_
    param_x : _type_
        _description_
    param_y : _type_
        _description_

    Returns
    -------
    tuple(json, json)
        tuple of filtered data and no data dataframes
    """
    if isinstance(station_nm, str):
        station_nm = [station_nm]

    pcode_mask = (data.ALL_DATA_DF["USGSPCode"] == param_x) | (
        data.ALL_DATA_DF["USGSPCode"] == param_y
    )
    staid_date_mask = (
        (data.ALL_DATA_DF["station_nm"].isin(station_nm))
        & (data.ALL_DATA_DF["ActivityStartDate"] >= str(start_date))
        & (data.ALL_DATA_DF["ActivityStartDate"] <= end_date)
    )

    filtered = data.ALL_DATA_DF.loc[staid_date_mask & pcode_mask]
    if station_nm is None:
        return filtered.to_json(), data.NODATA_DF.to_json()
    return (
        filtered.to_json(),
        data.NODATA_DF.loc[data.NODATA_DF["staid"].isin(station_nm)].to_json(),
    )


@dash.callback(
    [
        Output("map-view-graph", "figure"),
        Output("map-text", "children"),
        Output("graph-text-param", "children"),
    ],
    [
        Input("memory-PoI-data", "data"),
        Input("station-checklist", "value"),
        Input("param-select", "value"),
        Input("date-range", "end_date"),
    ],
)
def map_view_map(mem_data, checklist, param, end_date):
    # This is technically a secret, but anyone can request
    # this from mapbox so I'm not concerened about it.
    mem_df = pd.read_json(mem_data)
    mem_df = mem_df.sort_values(by="datetime")
    mem_df = mem_df.drop_duplicates(subset="staid", keep="last")
    nondetects = common.filter_nondetect_data(mem_df)
    no_data = common.filter_nodata_data(
        data.NODATA_DF, staids=list(mem_df["staid"]), checklist=checklist
    )
    mem_df = mem_df.loc[mem_df["ValueAndUnits"] != "Not Detected"]
    mem_df["Sample Date"] = mem_df["datetime"].astype(str).copy()

    # Debugging helper lines.
    # date_filtered_mem_df[["Station ID", "Sample Date", "Result", "Latitude", "Longitude", "ResultMeasureValue", "ResultMeasure/MeasureUnitCode"]]
    # mem_df = mem_df[["Station ID", "Sample Date", "Result", "Latitude", "Longitude", "ResultMeasureValue", "ResultMeasure/MeasureUnitCode"]]

    # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig1 = go.Figure(layout=dict(template="plotly"))

    fig1 = px.scatter_mapbox(
        mem_df,
        lat="dec_lat_va",
        lon="dec_long_va",
        color="ResultMeasureValue",
        color_continuous_scale=px.colors.sequential.Sunset,
        labels={
            "station_nm": "Station Name",
            "staid": "Station ID",
            "dec_lat_va": "Latitude",
            "dec_long_va": "Longitude",
            "ValueAndUnits": "Result",
            "datetime": "Sample Date",
        },
        hover_name="station_nm",
        hover_data={
            "ValueAndUnits": True,
            "datetime": True,
            "dec_lat_va": True,
            "dec_long_va": True,
            "ResultMeasureValue": False,
        },
        mapbox_style=MAPBOX_BASELAYER_STYLE,
    )

    fig1.update_traces(
        marker=dict(
            size=12,
        ),
    )

    if nondetects is not None:
        fig2 = px.scatter_mapbox(
            nondetects,
            lat="dec_lat_va",
            lon="dec_long_va",
            color="ValueAndUnits",
            color_discrete_map={"Not Detected": "green"},
            labels={
                "station_nm": "Station Name",
                "dec_lat_va": "Latitude",
                "dec_long_va": "Longitude",
                "ValueAndUnits": "Result",
                "datetime": "Sample Date",
            },
            hover_name="station_nm",
            hover_data={
                "ValueAndUnits": True,
                "datetime": True,
                "dec_lat_va": True,
                "dec_long_va": True,
                "ResultMeasureValue": False,
            },
        )
        fig2.update_traces(
            marker=dict(
                size=10,
            ),
        )
        fig1.add_trace(fig2.data[0])

    if no_data is not None:
        fig3 = px.scatter_mapbox(
            no_data,
            lat="dec_lat_va",
            lon="dec_long_va",
            color="Result",
            color_discrete_map={"No Data": "black"},
            labels={
                "station_nm": "Station Name",
                "dec_lat_va": "Latitude",
                "dec_long_va": "Longitude",
                "ValueAndUnits": "Result",
                "datetime": "Sample Date",
            },
            hover_name="station_nm",
            hover_data={
                "Result": True,
                "datetime": True,
                "dec_lat_va": True,
                "dec_long_va": True,
                "ResultMeasureValue": False,
            },
        )
        fig3.update_traces(marker={"size": 10})
        fig1.add_trace(fig3.data[0])

    # Color bar Title, if not available, display nothing, else display units
    if (
        len(mem_df["ResultMeasure/MeasureUnitCode"].array) == 0
        or mem_df["ResultMeasure/MeasureUnitCode"]
        .loc[~mem_df["ResultMeasure/MeasureUnitCode"].isnull()]
        .empty
    ):
        color_bar_title = ""
    else:
        color_bar_title = (
            mem_df["ResultMeasure/MeasureUnitCode"]
            .loc[~mem_df["ResultMeasure/MeasureUnitCode"].isnull()]
            .array[0]
        )

    fig1.update_layout(
        coloraxis_colorbar=dict(
            title=color_bar_title,
        ),
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=5, r=0, t=0, b=1),
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            bearing=0,
            pitch=0,
            zoom=13,
        ),
    )

    return (
        fig1,
        f"Location Map -- Most recent values before {end_date} for:",
        f"{data.available_param_dict.get(param)}",
    )


@dash.callback(
    Output("plot_param_ts", "figure"),
    [
        Input("memory-PoI-data", "data"),
        Input("param-select", "value"),
    ],
)
def plot_param_ts(mem_data, param):
    """Plots parameter as a function of time.

    Parameters
    ----------
    data : JSON
        JSON object from memory-output cache
    param : str
        Parameter code, e.g. p00400 from param-select dropdown

    Returns
    -------
    px.scatter() figure to scatter_plot location
    """
    if mem_data is None:
        raise PreventUpdate
    mem_df = pd.read_json(mem_data)
    # mem_df["datetime"] = pd.to_datetime(mem_df["datetime"], format="%Y-%m-%d %H:%M")
    mem_df = mem_df.dropna(subset=["ResultMeasureValue"])

    fig = go.Figure(
        layout=dict(template="plotly")
    )  # !important!  Solves strange plotly bug where graph fails to load on initialization,
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
        category_orders={"station_nm": natsorted(list(mem_df["station_nm"]))},
    )

    fig.update_layout(
        margin=dict(l=5, r=5, t=30, b=5),
        xaxis_title="Sample Date",
        yaxis_title=data.available_param_dict.get(param),
    )

    try:
        smcl_name = mem_df.loc[mem_df["USGSPCode"] == param][
            "CharacteristicName"
        ].unique()[0]
        smcl = pc.SMCL_DICT.get(smcl_name, False)
        if smcl and smcl_name != "Nitrate" and smcl_name != "Manganese":
            fig.add_hline(
                y=smcl,
                annotation_text=f"EPA SDWR: {smcl}",
            )
        if param == "p00300":
            fig.add_hline(
                y=0.5,  # 0.5 mg/L is Anoxic
                annotation_text="Anoxic: 0.5",
            )
        if mcl := pc.MCL_DICT.get(smcl_name, False):
            fig.add_hline(
                y=mcl,
                # annotation_text=f"EPA DWR: {mcl}",
            )
        if smcl_name in ["Nitrate", "Manganese"]:
            fig.update_yaxes(type="log")
    except IndexError:
        print("Invalid index, no worries")

    return fig


@dash.callback(
    Output("plot_dumbbell", "figure"),
    [
        Input("memory-PoI-data", "data"),
        Input("param-select", "value"),
    ],
)
def plot_dumbbell(mem_data, param):
    df = pd.read_json(mem_data)
    min_df = df[
        df["ActivityStartDate"]
        == df.groupby("staid")["ActivityStartDate"].transform(min)
    ].sort_values(by="staid")
    max_df = df[
        df["ActivityStartDate"]
        == df.groupby("staid")["ActivityStartDate"].transform(max)
    ].sort_values(by="staid")

    first_values = list(min_df["ResultMeasureValue"].array)
    last_values = list(max_df["ResultMeasureValue"].array)
    staids = list(min_df["station_nm"].array)

    short_nones = [None] * len(first_values)
    line_data_x = list(common.roundrobin(first_values, last_values, short_nones))

    long_nones = [None] * len(line_data_x)
    line_data_y = list(common.roundrobin(staids, staids, long_nones))
    plotting_df = pd.DataFrame(
        {
            "ResultMeasureValue_first": first_values,
            "ResultMeasureValue_last": last_values,
            "station_nm": staids,
        },
    )
    plotting_df = pd.merge(plotting_df, min_df, on="station_nm")
    plotting_df = pd.merge(plotting_df, max_df, on="station_nm")
    start_custom_data = np.stack(
        (
            plotting_df["station_nm"],
            plotting_df["ActivityStartDate_x"],
            plotting_df["staid_x"],
            plotting_df["ValueAndUnits_x"],
        ),
        axis=-1,
    )
    end_custom_data = np.stack(
        (
            plotting_df["station_nm"],
            plotting_df["ActivityStartDate_y"],
            plotting_df["staid_y"],
            plotting_df["ValueAndUnits_y"],
        ),
        axis=-1,
    )
    hover_template = "Station Name: %{customdata[0]}<br>Datetime: %{customdata[1]}<br>Station ID: %{customdata[2]}<br>Result: %{customdata[3]}<br><extra></extra>"

    fig = go.Figure(
        data=[
            go.Scatter(
                x=plotting_df["ResultMeasureValue_first"],
                y=plotting_df["station_nm"],
                name="First sample",
                mode="markers",
                marker=dict(
                    color="#B2D0EF",
                    size=16,
                ),
                customdata=start_custom_data,
                hovertemplate=hover_template,
            ),
            go.Scatter(
                x=plotting_df["ResultMeasureValue_last"],
                y=plotting_df["station_nm"],
                name="Last sample",
                mode="markers",
                marker=dict(
                    color="#3283D6",
                    size=16,
                ),
                customdata=end_custom_data,
                hovertemplate="Station Name: %{customdata[0]}<br>"
                + "Datetime: %{customdata[1]}<br>"
                + "Station ID: %{customdata[2]}<br>"
                + "Result: %{customdata[3]}<br>"
                + "<extra></extra>",
            ),
            # # Plot lines and arrows
            go.Scatter(
                x=line_data_x,
                y=line_data_y,
                mode="markers+lines",
                showlegend=False,
                hoverinfo="skip",
                marker=dict(
                    symbol="arrow",
                    color="black",
                    size=16,
                    angleref="previous",
                ),
            ),
        ]
    )
    fig.update_layout(
        xaxis_title=data.available_param_dict.get(param),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=5, r=5, t=0, b=1),
    )
    return fig


@dash.callback(
    Output("plot_box", "figure"),
    [
        Input("memory-PoI-data", "data"),
        Input("param-select", "value"),
    ],
)
def plot_box(mem_data, param):
    mem_df = pd.read_json(mem_data)
    mem_df["datetime"] = pd.to_datetime(mem_df["datetime"], format="%Y-%m-%d %H:%M")
    mem_df = mem_df.dropna(subset=["ResultMeasureValue"])

    fig = px.box(
        mem_df,
        labels={
            "station_nm": "Station Name",
            "datetime": "Sample Date",
            "staid": "Station ID",
            "ResultMeasureValue": "Result",
        },
        x="station_nm",
        y="ResultMeasureValue",
        color="station_nm",
        category_orders={"station_nm": natsorted(list(mem_df["station_nm"]))},
    )

    try:
        smcl_name = mem_df.loc[mem_df["USGSPCode"] == param][
            "CharacteristicName"
        ].unique()[0]
        smcl = pc.SMCL_DICT.get(smcl_name, False)
        if smcl and smcl_name != "Nitrate" and smcl_name != "Manganese":
            fig.add_hline(
                y=smcl,
                annotation_text=f"EPA SDWR: {smcl}",
            )
        if param == "p00300":
            fig.add_hline(
                y=0.5,  # 0.5 mg/L is Anoxic
                annotation_text="Anoxic: 0.5",
            )
        if mcl := pc.MCL_DICT.get(smcl_name, False):
            fig.add_hline(
                y=mcl,
                # annotation_text=f"EPA DWR: {mcl}",
            )
        if smcl_name in ["Nitrate", "Manganese"]:
            fig.update_yaxes(type="log")
    except IndexError:
        print("Invalid index, no worries")

    fig.update_layout(
        yaxis_title=str(data.available_param_dict.get(param)),
        margin=dict(l=5, r=5, t=30, b=5),
    )
    return fig


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
    combined = pd.merge(x_data, y_data, on="datetime")
    combined = combined.dropna(subset=["ResultMeasureValue_x", "ResultMeasureValue_y"])
    combined.rename(columns={"staid_x": "staid"}, inplace=True)
    combined.rename(columns={"station_nm_x": "station_nm"}, inplace=True)

    # !important!  Solves strange plotly bug where graph fails to load on initialization
    fig = go.Figure(layout=dict(template="plotly"))
    fig = px.scatter(
        combined,
        x="ResultMeasureValue_x",
        y="ResultMeasureValue_y",
        color="station_nm",
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
        category_orders={"station_nm": natsorted(list(mem_df["station_nm"]))},
    )

    try:
        if smcl := pc.SMCL_DICT.get(
            mem_df.loc[mem_df["USGSPCode"] == param_x]["CharacteristicName"].unique()[
                0
            ],
            False,
        ):
            fig = common.add_xline(fig=fig, smcl=smcl)
    except IndexError:
        print("Invalid index, no worries")

    try:
        if smcl := pc.SMCL_DICT.get(
            mem_df.loc[mem_df["USGSPCode"] == param_y]["CharacteristicName"].unique()[
                0
            ],
            False,
        ):
            fig = common.add_yline(fig=fig, smcl=smcl)
    except IndexError:
        print("Invalid index, no worries")

    x_title = str(data.available_param_dict.get(param_x))
    y_title = str(data.available_param_dict.get(param_y))
    if len(x_title) > 30:
        x_title = common.title_wrapper(x_title)
    if len(y_title) > 30:
        y_title = common.title_wrapper(y_title)

    fig.update_layout(
        margin=dict(l=5, r=5, t=30, b=5),
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


@dash.callback(
    Output("plot_xyz", "figure"),
    [
        Input("station-checklist", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("param_select_xx", "value"),
        Input("param_select_yy", "value"),
        Input("param_select_zz", "value"),
    ],
)
def plot_xyz(checklist, start_date, end_date, param_x: str, param_y: str, param_z: str):
    mem_df = common.filter_xyz_data(
        data.ALL_DATA_DF, checklist, start_date, end_date, param_x, param_y, param_z
    )
    x_data = mem_df.loc[mem_df["USGSPCode"] == param_x]
    x_data = x_data.rename(columns={"ResultMeasureValue": "ResultMeasureValue_x"})
    y_data = mem_df.loc[mem_df["USGSPCode"] == param_y]
    y_data = y_data.rename(columns={"ResultMeasureValue": "ResultMeasureValue_y"})
    z_data = mem_df.loc[mem_df["USGSPCode"] == param_z]
    z_data = z_data.rename(columns={"ResultMeasureValue": "ResultMeasureValue_z"})
    # y_data = y_data.loc[:,["staid", "datetime", "ResultMeasureValue", "USGSPCode"]]  # Can take out later, just helping debug now.
    combined = x_data.merge(y_data, on="datetime").merge(z_data, on="datetime")
    combined = combined[
        [
            "datetime",
            "ResultMeasureValue_x",
            "ResultMeasureValue_y",
            "ResultMeasureValue_z",
            "station_nm_x",
            "staid_x",
        ]
    ]
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

    fig = go.Figure(
        layout=dict(template="plotly")
    )  # !important!  Solves strange plotly bug where graph fails to load on initialization,
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
        category_orders={"station_nm_x": natsorted(list(combined["station_nm_x"]))},
    )

    try:
        if smcl := pc.SMCL_DICT.get(
            mem_df.loc[mem_df["USGSPCode"] == param_x]["CharacteristicName"].unique()[
                0
            ],
            False,
        ):
            fig = common.add_xline(fig=fig, smcl=smcl)
    except IndexError:
        print("Invalid index, no worries")

    try:
        if smcl := pc.SMCL_DICT.get(
            mem_df.loc[mem_df["USGSPCode"] == param_y]["CharacteristicName"].unique()[
                0
            ],
            False,
        ):
            fig = common.add_yline(fig=fig, smcl=smcl)
    except IndexError:
        print("Invalid index, no worries")

    x_title = str(data.available_param_dict.get(param_x))
    y_title = str(data.available_param_dict.get(param_y))
    z_title = str(data.available_param_dict.get(param_z))
    if len(x_title) > 30:
        x_title = common.title_wrapper(x_title)
    if len(y_title) > 30:
        y_title = common.title_wrapper(y_title)
    if len(z_title) > 30:
        z_title = common.title_wrapper(z_title)

    fig.update_layout(
        # title="Comparative Parameter Plot",
        margin=dict(l=5, r=5, t=30, b=5),
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
