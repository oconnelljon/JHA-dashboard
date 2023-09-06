# sidebar.py
from datetime import datetime, timedelta
from dash import dcc, html
import dash


def main_sidebar(checklist_option):
    return html.Aside(
        [
            html.Div(
                [
                    html.H2("Station ID"),
                    dcc.Checklist(["All"], ["All"], id="all-checklist", inline=True),
                    dcc.Checklist(
                        id="station-checklist",
                        options=checklist_option,
                        persistence=False,
                    ),
                ],
                className="sidebar-sub-container",
                id="station-select-container",
            ),
            html.Div(
                [
                    html.H2("Query Range"),
                    dcc.DatePickerRange(
                        id="date-range",
                        start_date=datetime.now().date() - timedelta(days=1460),
                        end_date=datetime.now().date(),
                        initial_visible_month=datetime.now(),
                        persistence=True,
                        style={
                            "color": "#333",
                        },
                    ),
                ],
                className="sidebar-sub-container",
                id="daterange-container",
            ),
            html.Img(src=dash.get_asset_url("fort-peck-icon-150x175.png"), id="coop-img-container"),
        ],
        className="sidebar-container",
    )
