# from datetime import date, datetime
# import dataretrieval.nwis as nwis
# import pandas as pd
# import json
# from typing import Iterable


# # df = nwis.get_record(sites="12323840", service="qwdata", start="2020-03-01", end="2020-10-01", parameterCd="00925")
# # STAID_coord = pd.read_csv("src/data/site_data.csv")
# # pause = 2

# # pd.to_numeric(df['p00925'], errors='coerce').dtype
# sidebar = html.Div(
#     [
#         html.H1("Sidebar", className="display-4"),
#         html.Hr(),
#         html.P("A simple sidebar layout with navigation links", className="lead"),
#         html.Div(
#             [
#                 "Station ID: ",
#                 # dcc.Input(
#                 #     id="station_ID",
#                 #     value=STAID_coord["site_no"][0],
#                 #     debounce=True,
#                 #     inputMode="numeric",
#                 #     autoFocus=True,
#                 #     minLength=8,
#                 #     placeholder="enter station",
#                 #     type="text",
#                 # ),
#                 dcc.Dropdown(
#                     id="station_ID",
#                     value="433641110441501",
#                     options=pc.station_list,
#                 ),
#             ],
#         ),
#         html.Div(
#             [
#                 html.P("Select Date Range"),
#                 dcc.DatePickerRange(
#                     id="date_range",
#                     start_date=datetime.now().date() - timedelta(days=1460),
#                     end_date=datetime.now().date(),
#                     initial_visible_month=datetime.now(),
#                     style={
#                         "font-size": "6px",
#                         "display": "inline-block",
#                         "border-radius": "2px",
#                         "border": "1px solid #ccc",
#                         "color": "#333",
#                         "border-spacing": "0",
#                         "border-collapse": "separate",
#                     },
#                 ),
#             ],
#         ),
#     ],
#     style=SIDEBAR_STYLE,
# )
# station_set = {
#     "433615110440001",
#     "433604110443401",
#     "433604110443402",
#     "433604110443403",
#     "433551110443501",
#     "433600110443701",
#     "433603110443501",
#     "433603110443502",
#     "433605110443801",
#     "433613110443501",
#     "433641110441501",
#     "433630110442701",
#     "433556110441601",
#     "433558110441501",
#     "433605110441201",
#     "433602110441201",
#     "433604110441001",
#     "433607110440901",
#     "433556110441501",
#     "433606110440501",
# }


# def build_station_csv(stations: Iterable):
#     staid_info = pd.DataFrame()
#     for staid in stations:
#         temp_df = nwis.get_record(sites=staid, service="site")
#         staid_info = pd.concat([staid_info, temp_df])
#     staid_info.to_csv("src/data/JHA_STAID_INFO.csv", index=False)


# build_station_csv(station_set)
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

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

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


navbar = dbc.Navbar(
    [
        dbc.NavbarBrand("Test"),
        dbc.Nav([dbc.NavLink("Item 1"), dbc.NavLink("Item 2")]),
    ],
    sticky="top",
    color="dark",
    dark=True,
    style={"width": "100%"},
)
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": "2rem",
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
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
        html.Div(
            [
                html.P("Station ID: "),
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
    id="sidebar",
    style=SIDEBAR_STYLE,
)

content = html.Div(
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
    id="page-content",
    style=CONTENT_STYLE,
)

application = app.server

app.layout = html.Div(
    [
        # dcc.Store(id="side_click"),
        dcc.Location(id="url"),
        navbar,
        html.Div(
            [
                sidebar,
                content,
            ],
        ),
    ]
)


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return content
    elif pathname == "/page-2":
        return html.P("This is the content of page 2. Yay!")
    elif pathname == "/page-3":
        return html.P("Oh cool, this is page 3!")
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
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
