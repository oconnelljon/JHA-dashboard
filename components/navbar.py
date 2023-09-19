# navbar.py

import dash_bootstrap_components as dbc
from dash import dcc, html
import dash
from utils.settings import APP_TITLE


def make_title_bar():
    return html.Div(
        [
            html.Div(),
            html.Div(
                html.H1(APP_TITLE),
                className="navbar-title-container",
            ),
            html.Div(
                [
                    dbc.Button("Download", color="primary", id="download-button", n_clicks=0),
                    dbc.Button("Info", color="primary", id="info-button", n_clicks=0),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Download Data")),
                            dbc.ModalBody(
                                [
                                    html.Div(
                                        [
                                            dbc.Button(
                                                "Download All Data",
                                                color="primary",
                                                id="download-all-button",
                                                n_clicks=0,
                                            ),
                                            dcc.Download(id="download-all-data-csv"),
                                            dbc.Button(
                                                "Download Queried Data",
                                                color="primary",
                                                id="download-query-button",
                                                n_clicks=0,
                                            ),
                                            dcc.Download(id="download-query-data-csv"),
                                            dbc.Button("Close", id="cancel-button", n_clicks=0),
                                        ],
                                        id="modal-button-container",
                                    ),
                                ],
                            ),
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
