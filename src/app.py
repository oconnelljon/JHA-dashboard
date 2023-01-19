from datetime import date, datetime, timedelta
import dataretrieval.nwis as nwis
import utils.param_codes as pc
import dash
from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from utils import utils
import json

# import dash_bootstrap_components as dbc
STAID_coord = pd.read_csv("data/JHA_STAID_INFO.csv")
mapbox_access_token = "pk.eyJ1Ijoic2xlZXB5Y2F0IiwiYSI6ImNsOXhiZng3cDA4cmkzdnFhOWhxdDEwOHQifQ.SU3dYPdC5aFVgOJWGzjq2w"


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


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "4rem 1rem 2rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "19rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


# app = dash.Dash(
#     __name__,
#     external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
#     # these meta_tags ensure content is scaled correctly on different devices
#     # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
#     meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
# )

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.MATERIA, dbc.icons.FONT_AWESOME],
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.Button("Sidebar", outline=True, color="secondary", className="mr-1", id="btn_sidebar"),
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Brand",
    brand_href="#",
    color="dark",
    dark=True,
    fluid=True,
)

sidebar = html.Div(
    [
        html.Div(
            [
                html.H2("Auto ML", style={"color": "white"}),
            ],
            className="sidebar-header",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className="fas fa-home me-2"), html.Span("Dashboard")],
                    href="/",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-calendar-alt me-2"),
                        html.Span("Projects"),
                    ],
                    href="/projects",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-envelope-open-text me-2"),
                        html.Span("Datasets"),
                    ],
                    href="/datasets",
                    active="exact",
                ),
            ],
            vertical=True,
            pills=True,
        ),
        html.Div(
            [
                "Station ID: ",
                dcc.Dropdown(
                    id="station_ID",
                    value="433641110441501",
                    options=pc.station_list,
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
                    style={
                        "font-size": "6px",
                        "display": "inline-block",
                        "border-radius": "2px",
                        "border": "1px solid #ccc",
                        "color": "#333",
                        "border-spacing": "0",
                        "border-collapse": "separate",
                    },
                ),
            ],
        ),
    ],
    className="sidebar",
)

application = app.server

app.layout = html.Div(
    [
        navbar,
        sidebar,
        html.Div(
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
            className="content",
        ),
    ]
)


# @app.callback(Output("location_map", "figure"), Input("location_map", "ClickData"))
# def display_click_data(clickData):
#     return json.dumps(clickData, indent=2)


@app.callback(
    Output("STAID", "value"),
    Output("station_ID", "options"),
    [
        Input("location_map", "clickData"),
    ],
)
def update_STAID(clickData):
    if not clickData:
        raise PreventUpdate
    return [str(clickData["points"][0]["customdata"])]


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


# html.Div(
#     [
#         "Filter by sample type: ",
#         dcc.Dropdown(
#             id="sample_code_select",
#             options=pc.sample_codes,
#             value="9",
#         ),
#     ],
#     style={"width": "20%"},
# ),


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
