from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from components import make_title_bar, main_sidebar
from utils import data
from utils.settings import DEFAULT_PCODE


parameter_of_interest_text = "Select a Parameter of Interest to populate the PoI plots and table. Only queried stations and data within the queried time range are displayed."
time_plot_text = "Time-Series plots show the values for the Parameter of Interest for the queried stations across the queried time range."
dumbbell_plot_text = "Dumbbell plots show a change in a parameter from the first available sample to the latest. The longer the line, the larger the change.  Arrow's indicate if the parameter increased or decreased over the queried time range."
box_plot_text = "Box plots show the distribution of data for the entire queried time range.  The longer the box, the larger the variation in the data."
scatter_x_y_text = "The scatter plot displays data from the above drop down menues on their respective axis'. Only queried stations and data within the time range are displayed."
scatter_x_y_z_text = (
    "Plot X vs Y data with a third parameter that controls the size of the plot marker."
)
summary_table_text = "The Summary Table contains general information about the queried stations in the time range for the Parameter of Interest.  Stations with no data are not displayed."

poi_div = html.Div(
    [
        html.H2("Parameter of interest"),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id="param-select",
                            options=data.available_param_dict,
                            value=DEFAULT_PCODE,
                            # persistence=True,
                            clearable=False,
                        ),
                    ],
                    id="main-parameter-dropdown",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("Time-Series Plot"),
                        dcc.Graph(id="plot_param_ts", className="scatter-plot"),
                        dbc.CardFooter(
                            time_plot_text,
                            # className="plot-text",
                        ),
                    ],
                    className="plots-wrapper",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("Dumbbell Plot"),
                        dcc.Graph(id="plot_dumbbell", className="first-last-plot"),
                        dbc.CardFooter(
                            dumbbell_plot_text,
                        ),
                    ],
                    className="plots-wrapper",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader("Box Plot"),
                        dcc.Graph(id="plot_box", className="box-plot"),
                        dbc.CardFooter(
                            box_plot_text,
                            # className="plot-text",
                        ),
                    ],
                    className="plots-wrapper",
                ),
                dbc.Card(
                    [
                        dbc.CardHeader(id="data-table-text"),
                        dash_table.DataTable(
                            id="summary-table",
                            sort_action="native",
                        ),
                        dbc.CardFooter(
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
            dcc.Store(id="memory-PoI-data", storage_type="memory"),
            dcc.Store(id="memory-time-plot-no-data", storage_type="memory"),
            dcc.Store(id="memory-xy-plot", storage_type="memory"),
            dcc.Location(id="url"),
            make_title_bar(),
            html.Div(
                [
                    main_sidebar(checklist_option=data.STATION_NMs),
                    main_div,
                ],
                className="body-container",
            ),
        ],
        className="root",
    )
