# app.py
import dash
import dash_bootstrap_components as dbc

import utils.data
import utils.callbacks
from components.layout import make_layout

# Initialize App
app = dash.Dash(__name__, assets_folder="assets", external_stylesheets=[dbc.themes.SPACELAB], title="JHA Dashboard")  # Include __name__, serves as reference for finding .css files.
server = app.server  # Important for debugging and using Flask!
app.layout = make_layout()

if __name__ == "__main__":
    app.run_server(debug=False)
