import dash
from dash import html, dcc, callback, Input, Output
from datetime import date
import dataretrieval.nwis as nwis


# @callback(
#     Output("memory_data", "data"),
#     [
#         Input("station_ID", "value"),
#         Input("date_range", "start_date"),
#         Input("date_range", "end_date"),
#     ],
# )
# def get_qw_data(site, start, end):
#     df = nwis.get_record(sites=site, service="qwdata", start=start, end=end, access="3")
#     return df.to_json()
