# app.py
"""
This is the entry point of the web application. The program needs to import the callbacks 
to the main application for dash to find them in the global environment.  The callbacks rely on data.
That data is downloaded at the start of the program when callbacks is imported.  Data is imported when the callbacks
module imports the data module.  
"""
import dash
import dash_bootstrap_components as dbc
import flask

from utils.settings import PORT, ADDRESS, APP_TITLE
import utils.data
import utils.callbacks
from components.layout import make_layout


f_app = flask.Flask(__name__)
# Initialize App
app = dash.Dash(__name__, assets_folder="assets", external_stylesheets=[dbc.themes.SPACELAB], title=APP_TITLE, server=f_app)  # type: ignore  # pylance doesn't think f_app is suitable.
# server = app.server  # Important for debugging and using Flask!
app.layout = make_layout()

if __name__ == "__main__":
    app.run_server(debug=False, port=PORT, host=ADDRESS)
