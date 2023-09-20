# sidebar.py
from datetime import datetime, timedelta

# import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

location_map_text = (
    "The location map will only show the most recent available sample value per station."
)
#TODO fix height
#TODO move map somewhere else
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
                        labelClassName="checkbox-label",
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
            # Map
            dbc.Card(
                [
                    dbc.CardHeader(html.P(id="map-text")),
                    # html.H3(html.P(id="map-text")),
                    html.P(
                        id="graph-text-param", style={"font-weight": "bold", "text-align": "center"}
                    ),
                    dcc.Graph(id="map-view-graph", className="map-view-container", responsive=True),
                    dbc.CardFooter(html.P(location_map_text)),
                ],
                className="map-container",
            ),
        ],
        className="sidebar-container",
    )
