from dash import dcc, html, dash_table
from components import main_navbar, main_sidebar
from utils import data

parameter_of_interest_text = "Select a parameter of interest to populate the Time-Series and Box plots.  Only selected stations and data within the time range are displayed."
time_plot_text = "The Time-Series Plot shows the values for the Parameter of Interest for the selected stations across the selected time range."
box_plot_text = "Box plots show the distribution of data for the entire selected time range.  The longer the box, the larger the variation in the data."
scatter_x_y_text = "The scatter plot displays data from the above drop down menues on their respective axis'. Only selected stations and data within the time range are displayed."
scatter_x_y_z_text = "Plot X vs Y data with a third parameter that controls the size of the plot marker."
summary_table_text = "The Summary Table contains general information about the selected stations in the time range for the Parameter of Interest.  Stations with no data are not displayed."


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
                                                                options=data.available_param_dict,
                                                                value=data.DEFAULT_PCODE,
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
                                                                    html.H2("Scatter Y parameter"),
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
                                                                    html.H2("Scatter Y parameter"),
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
                                                                    html.H2("Bubble size parameter"),
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
