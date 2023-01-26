import dash
from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dataretrieval.nwis as nwis
import utils.param_codes as pc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils import utils
import json
from datetime import date, datetime, timedelta

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # Include __name__, serves as reference for finding .css files.
STAID_coords = pd.read_csv("data/JHA_STAID_INFO.csv")

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
    className="navbar",
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
            ]
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
        ),
        html.Div(
            [
                "Time plot parameter: ",
                dcc.Dropdown(
                    id="param_select",
                    options=pc.param_labels,
                    value="p00400",
                    persistence=True,
                ),
            ],
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
            # style={"width": "49%", "display": "inline-block"},
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
            # style={"width": "49%", "display": "inline-block"},
        ),
        html.Br(),
        # dcc.Graph(id="sidebar-location-map", figure=create_map()),
    ],
    className="sidebar",
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
map_view = html.Div(
    id="map-tab-graph",
)

tabs = dcc.Tabs(
    [
        dcc.Tab(  # located in tabpanel tab-0 aka "Graph view"
            [
                scatter_time_container,
                scatter_params_container,
            ],
            label="Graph view",
            className="tab0-graph-view",
        ),
        dcc.Tab(  # located in tabpanel tab-1 aka "Map view"
            map_view,
            label="Map view",
        ),
    ],
    id="tabs-main-container",  # dash appends -parent to this ID and creates a parent to hold tabs-main-container child
    # parent_className="tabs-tab-container",  # Contains tabs and tab content
    className="tabs-container",  # container for Tabs buttons only
    # tabs-content Div container created by dbc.Tabs and holds the dbc.Tab objects
)

application = app.server  # Important for debugging and using Flask!

app.layout = html.Div(
    [
        dcc.Store(id="staid_coords", storage_type="memory"),
        dcc.Store(id="memory_data", storage_type="memory"),
        dcc.Store(id="combined_data_coords", storage_type="memory"),
        dcc.Store(id="STAID", storage_type="memory", data="12323840"),
        # State("map_view_cache", "data"),
        html.Div(
            [
                dcc.Location(id="url"),
                dbc.Nav(
                    navbar,
                    className="navbar-container",
                ),
                html.Div(
                    sidebar_select,
                    className="sidebar-container",
                ),
                html.Div(
                    html.Div(
                        tabs,
                        className="main-content-wrapper",
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
    Output("map-tab-graph", "children"),
    [
        Input("memory_data", "data"),
        # Input("staid_coords", "data"),
    ],
)
def create_map(mem_data):
    MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoic2xlZXB5Y2F0IiwiYSI6ImNsOXhiZng3cDA4cmkzdnFhOWhxdDEwOHQifQ.SU3dYPdC5aFVgOJWGzjq2w"
    mem_df = pd.read_json(mem_data)
    # df = pd.read_json(mem_data)

    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter_mapbox(
        mem_df,
        lat="dec_lat_va",
        lon="dec_long_va",
        # color=param,
        color_continuous_scale=px.colors.cyclical.IceFire,
        # size_max=9,
        # zoom=10,
    )

    # go.Figure(
    #     go.Scattermapbox(
    #         lat=df[lat],
    #         lon=df[long],
    #         mode="markers",
    #         marker=go.scattermapbox.Marker(size=9),
    #         color=param,
    #         color_continuous_scale=px.colors.cyclical.IceFire,
    #         text=df[["site_no"]],
    #         customdata=df["site_no"],
    #     )
    # )
    fig.update_layout(
        autosize=True,
        hovermode="closest",
        margin=dict(l=10, r=10, t=10, b=10),
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            bearing=0,
            center=dict(
                lat=43.603413,
                lon=-110.739465,
            ),
            pitch=0,
            zoom=13.25,
        ),
    )
    return dcc.Graph(id="location-map", figure=fig)


@app.callback(
    Output("staid_coords", "data"),
    Input("access_dropdown", "value"),
)
def load_local_staids(local_csv: str):
    df = pd.read_csv("data/JHA_STAID_INFO.csv")
    return df.to_json()


@app.callback(
    Output("memory_data", "data"),
    [
        # Input("station_ID", "value"),
        Input("staid_coords", "data"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
        Input("access_dropdown", "value"),
    ],
)
def get_qw_data(coord_data, start, end, access):
    coords = pd.read_json(coord_data)
    site_list = coords["STAID"].astype(str).tolist()
    df = nwis.get_record(sites=site_list, service="qwdata", start=start, end=end, access=access, datetime_index=False)  # parameterCd=99162, no "p" when querying.
    if isinstance(df.index, pd.MultiIndex):
        for station in site_list:
            df.loc[df.index.get_level_values("site_no") == station, "STAID"] = station
    else:
        df["STAID"] = df["site_no"]
    df["STAID"] = df["STAID"].astype(str)
    coords["STAID"] = coords["STAID"].astype(str)
    # df2 = df.copy()
    df = pd.merge(df, coords, on="STAID", how="left")
    return df.to_json()


@app.callback(
    Output("scatter_plot", "figure"),
    [
        Input("param_select", "value"),
        Input("memory_data", "data"),
    ],
)
def plot_parameter(param, data, sample_code=9):
    df = pd.read_json(data)
    df["STAID"] = df["STAID"].astype(str)
    df["sample_dt"] = pd.to_datetime(df["sample_dt"], format="%Y-%m-%d")
    try:
        sample_code = int(sample_code)
        df = df.loc[df["samp_type_cd"] == sample_code]
    except ValueError:
        df = df.loc[df["samp_type_cd"] == sample_code]

    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter(
        df,
        x="sample_dt",
        y=param,
        color="STAID",
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
        # Input("station_ID", "value"),
        Input("param_select_X", "value"),
        Input("param_select_Y", "value"),
        Input("memory_data", "data"),
    ],
)
def x_vs_y(param_x: str, param_y: str, data):
    df = pd.read_json(data)
    df["STAID"] = df["STAID"].astype(str)
    fig = go.Figure(layout=dict(template="plotly"))  # !important!  Solves strange plotly bug where graph fails to load on initialization,
    fig = px.scatter(
        df,
        x=param_x,
        y=param_y,
        color="STAID",
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
    app.run_server(debug=True)
