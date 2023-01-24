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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

application = app.server

app.layout = html.Div(
    id="report-container",
    children=[
        dcc.Graph(id="main-graph-container"),
        dcc.Graph(id="related-graph"),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
