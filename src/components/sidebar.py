# sidebar.py
from datetime import datetime, timedelta
from dash import dcc, html


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
                    html.H2("Select Date Range"),
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
                className="sidebar-sub-container",
                id="daterange-container",
            ),
            # Map
            html.Div(
                [
                    html.H3("Location Map"),
                    html.P(id="map-text"),
                    html.P(id="graph-text-param", style={"font-weight": "bold", "text-align": "center"}),
                    html.Div(id="map-tab-graph", className="map-view-container"),
                ],
                id="sidebar-map-container",
                className="sidebar-sub-container",
            ),
        ],
        className="sidebar-container",
    )
