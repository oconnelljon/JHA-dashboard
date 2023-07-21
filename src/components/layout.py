from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from components import main_navbar, main_sidebar
from utils import data
from utils.settings import DEFAULT_PCODE

parameter_of_interest_text = "Select a parameter of interest to populate the Time-Series and Box plots.  Only selected stations and data within the time range are displayed."
time_plot_text = "The Time-Series Plot shows the values for the Parameter of Interest for the selected stations across the selected time range."
box_plot_text = "Box plots show the distribution of data for the entire selected time range.  The longer the box, the larger the variation in the data."
scatter_x_y_text = "The scatter plot displays data from the above drop down menues on their respective axis'. Only selected stations and data within the time range are displayed."
scatter_x_y_z_text = "Plot X vs Y data with a third parameter that controls the size of the plot marker."
summary_table_text = "The Summary Table contains general information about the selected stations in the time range for the Parameter of Interest.  Stations with no data are not displayed."
location_map_text = "The location map will only show the most recent available sample value per station."

poi_div = html.Div(
    [
        html.H2("Parameter of interest"),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id="param_select",
                            options=data.available_param_dict,
                            value=DEFAULT_PCODE,
                            persistence=True,
                            clearable=False,
                        ),
                    ],
                    id="main-parameter-dropdown",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("Time-Series Plot"),
                        dcc.Graph(id="plot_param_ts", className="scatter-plot"),
                        dbc.CardHeader(
                            time_plot_text,
                            # className="plot-text",
                        ),
                    ],
                    className="plots-wrapper",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("Box Plot"),
                        dcc.Graph(id="plot_box", className="box-plot"),
                        dbc.CardHeader(
                            box_plot_text,
                            # className="plot-text",
                        ),
                    ],
                    className="plots-wrapper",
                ),
                # Map
                dbc.Card(
                    [
                        dbc.CardHeader(html.P(id="map-text")),
                        # html.H3(html.P(id="map-text")),
                        html.P(id="graph-text-param", style={"font-weight": "bold", "text-align": "center"}),
                        html.Div(id="map-tab-graph", className="map-view-container"),
                        dbc.CardHeader(html.P(location_map_text)),
                    ],
                    className="table-container",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader(id="data-table-text"),
                        dash_table.DataTable(
                            id="summary-table",
                            sort_action="native",
                        ),
                        dbc.CardHeader(
                            summary_table_text,
                            # className="plot-text",
                        ),
                    ],
                    className="table-container",
                ),
            ],
            className="sub-tile-wrapper",
        ),
    ],
    className="tile-container",
)

comp_xy_div = dbc.Card(
    [
        html.Div(
            [
                dbc.CardHeader("Scatter X parameter"),
                dcc.Dropdown(
                    id="param_select_x",
                    options=data.available_param_dict,
                    value="p00400",
                    clearable=False,
                ),
            ],
            className="main-content-dropdown",
            id="select-x-container",
        ),
        html.Div(
            [
                dbc.CardHeader("Scatter Y parameter"),
                dcc.Dropdown(
                    id="param_select_y",
                    options=data.available_param_dict,
                    value="p00300",
                    clearable=False,
                ),
            ],
            className="main-content-dropdown",
            id="select-y-container",
        ),
        dcc.Graph(id="plot_xy"),
        dbc.CardHeader(
            scatter_x_y_text,
            # className="plot-text",
        ),
    ],
    className="plots-wrapper",
)

comp_xyz_div = dbc.Card(
    [
        html.Div(
            [
                dbc.CardHeader("Scatter X parameter"),
                dcc.Dropdown(
                    id="param_select_xx",
                    options=data.available_param_dict,
                    value="p00400",
                    clearable=False,
                ),
            ],
            className="main-content-dropdown",
            id="select-xx-container",
        ),
        html.Div(
            [
                dbc.CardHeader("Scatter Y parameter"),
                dcc.Dropdown(
                    id="param_select_yy",
                    options=data.available_param_dict,
                    value="p00300",
                    clearable=False,
                ),
            ],
            className="main-content-dropdown",
            id="select-yy-container",
        ),
        html.Div(
            [
                dbc.CardHeader("Bubble size parameter"),
                dcc.Dropdown(
                    id="param_select_zz",
                    options=data.available_param_dict,
                    value="p00095",
                    clearable=False,
                ),
            ],
            className="main-content-dropdown",
            id="select-zz-container",
        ),
        dcc.Graph(id="plot_xyz"),
        dbc.CardHeader(
            scatter_x_y_z_text,
            # className="plot-text",
        ),
    ],
    className="plots-wrapper",
)

main_div = html.Div(
    [
        html.Main(
            [
                html.Div(
                    [
                        poi_div,
                        html.Div(
                            [
                                html.H2("Comparative Plots"),
                                html.Div(
                                    [
                                        comp_xy_div,
                                        comp_xyz_div,
                                    ],
                                    className="sub-tile-wrapper",
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
    id="main-wrapper",
)


def make_layout():
    return html.Div(
        [
            dcc.Store(id="memory-PoI-data", storage_type="memory"),  # Holds plotting data for map
            dcc.Store(id="memory-time-plot-no-data", storage_type="memory"),  # Holds plotting data for map if no data found
            dcc.Store(id="memory-xy-plot", storage_type="memory"),  # Holds scatter plot x-y data
            html.Div(
                [
                    dcc.Location(id="url"),
                    main_navbar(),
                    html.Div(
                        [
                            main_sidebar(checklist_option=data.STATION_NMs),
                            main_div,
                        ],
                        className="body-container",
                    ),
                ],
                className="page-container",
            ),
        ],
        className="root",
    )
