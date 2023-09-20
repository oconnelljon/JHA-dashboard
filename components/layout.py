import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from components import main_sidebar, make_title_bar
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
about_tab_text = "This is the Jackson Hole Airport data review dashboard!  \nHi Peter!"
learn_tab_text = "Put things to learn more about here!"
disclaimer_tab_text1 = "This software has been approved for release by the U.S. Geological Survey (USGS). Although the software has been subjected to review, the USGS reserves the right to update the software as needed pursuant to further analysis and review. No warranty, expressed or implied, is made by the USGS or the U.S. Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. Furthermore, the software is released on condition that neither the USGS nor the U.S. Government shall be held liable for any damages resulting from its authorized or unauthorized use. \n"
disclaimer_tab_text2 = "Unless otherwise stated, all data, metadata and related materials are considered to satisfy the quality standards relative to the purpose for which the data were collected. Some data presented may be preliminary and is subject to revision; it is being provided for timely best science. The information is provided on the condition that neither the U.S. Geological Survey nor the U.S. Government shall be held liable for any damages resulting from the authorized and unauthorized use of the information."

poi_div = html.Div(
    [
        dbc.Button(
            "Parameter of Interest",
            color="primary",
            id="poi-collapse-button",
            className="collapse-button",
            n_clicks=0,
        ),
        dbc.Collapse(
            [
                # html.H2("Parameter of interest"),
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
            id="poi-tile",
            is_open=True,
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

comp_plots = html.Div(
    [
        dbc.Button(
            "Compartative Plots",
            color="primary",
            id="comp-collapse-button",
            className="collapse-button",
            n_clicks=0,
        ),
        dbc.Collapse(
            [
                comp_xy_div,
                comp_xyz_div,
            ],
            className="sub-tile-wrapper",
            id="comp-tile",
            is_open=True,
        ),
    ],
    className="tile-container",
)

# TODO make collapsable containers for map and plots but leave PoI
main_div = html.Div(
    [
        html.Main(
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
    id="main-wrapper",
)


about_tab = dbc.Card(
    dbc.CardBody(
        [
            html.P(about_tab_text, className="card-text"),
        ]
    ),
    className="about-tab",
)

learn_tab = dbc.Card(
    dbc.CardBody(
        [
            html.P(learn_tab_text, className="card-text"),
        ]
    ),
    className="learn-tab",
)

disclaimer_tab = dbc.Card(
    dbc.CardBody(
        [
            html.P(disclaimer_tab_text1, className="card-text1"),
            html.Br(),
            html.P(disclaimer_tab_text2, className="card-text2"),
        ]
    ),
    className="disclaimer-tab",
)

info_tabs = dbc.Tabs(
    [
        dbc.Tab(about_tab, label="About"),
        dbc.Tab(learn_tab, label="Learn more"),
        dbc.Tab(disclaimer_tab, label="Disclaimer"),
    ],
)

# TODO spash modal on startup
info_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Welcome!")),
        dbc.ModalBody(info_tabs),
        # dbc.ModalFooter(),
    ],
    id="info-modal",
    is_open=True,
    # is_open=False,
    # centered=True,
)


def make_layout():
    return html.Div(
        [
            dcc.Store(id="memory-PoI-data", storage_type="memory"),
            dcc.Store(id="memory-time-plot-no-data", storage_type="memory"),
            dcc.Store(id="memory-xy-plot", storage_type="memory"),
            dcc.Location(id="url"),
            info_modal,
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
