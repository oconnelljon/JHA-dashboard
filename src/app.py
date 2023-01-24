import dash
from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dataretrieval.nwis as nwis
import utils.param_codes as pc
import plotly.graph_objects as go
import pandas as pd
from utils import utils
import json
from datetime import date, datetime, timedelta

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # Include __name__, serves as reference for finding .css files.

STAID_coord = pd.read_csv("data/JHA_STAID_INFO.csv")
mapbox_access_token = "pk.eyJ1Ijoic2xlZXB5Y2F0IiwiYSI6ImNsOXhiZng3cDA4cmkzdnFhOWhxdDEwOHQifQ.SU3dYPdC5aFVgOJWGzjq2w"

# Define how to create the location map.  Need here to use for initial map in content.
def create_map(lat="dec_lat_va", long="dec_long_va"):
    fig = go.Figure(
        go.Scattermapbox(
            lat=STAID_coord[lat],
            lon=STAID_coord[long],
            mode="markers",
            marker=go.scattermapbox.Marker(size=9),
            text=STAID_coord[["site_no"]],
            customdata=STAID_coord["site_no"],
        )
    )
    fig.update_layout(
        autosize=True,
        hovermode="closest",
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=STAID_coord[lat].median(),
                lon=STAID_coord[long].median(),
            ),
            pitch=0,
            zoom=10,
        ),
    )
    return fig


navbar = html.Div(
    [
        html.Div(
            html.H5("USGS"),
            className="navbar-brand-container",
        ),
        html.Div(
            html.H5("Jackson Hole Airport"),
            className="navbar-JHA-container",
        ),
        html.Div(
            html.Ul(
                [html.Li(dbc.NavLink("Item 1")), html.Li(dbc.NavLink("Item 2"))],
                className="navlink-list",
            ),
            className="navbar-link-container",
        ),
    ],
    className="navbar",
)

sidebar_select = html.Aside(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P("A simple sidebar layout with navigation links", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/page-1", id="page-1-link"),
                dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                dbc.NavLink("Page 3", href="/page-3", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Br(),
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
                        # "font-size": "inherit",
                        # "display": "inline-block",
                        # "border": "1px solid #ccc",
                        "color": "#333",
                        # "border-collapse": "separate",
                        # "display": "flex",
                    },
                ),
            ],
        ),
    ],
    className="sidebar",
)

content = html.Main(
    [
        html.H1(
            id="H1",
            children="The QCinator, it's coming for your data!",
            style={"textAlign": "center", "marginTop": 40, "marginBottom": 40},
        ),
        dcc.Graph(id="location_map", figure=create_map()),
        html.Div(
            [
                "Select parameter by name: ",
                dcc.Dropdown(
                    id="param_select",
                    options=pc.param_labels,
                    value="p00400",
                    persistence=True,
                ),
            ],
            style={"width": "49%", "display": "inline-block"},
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
        dcc.Store(id="STAID", storage_type="memory", data="12323840"),
    ],
    className="main-content",
)

application = app.server  # Important for debugging and using Flask!

app.layout = html.Div(
    [
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
                    content,
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
        Input("station_ID", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
        Input("access_dropdown", "value"),
    ],
)
def get_qw_data(site, start, end, access):
    df = nwis.get_record(sites=site, service="qwdata", start=start, end=end, access=access)
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
    app.run_server(debug=True)
