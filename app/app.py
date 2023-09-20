# app.py
"""
This is the entry point of the web application. The program needs to import the callbacks
to the main application for dash to find them in the global environment.
The callbacks rely on data. That data is downloaded at the start of
the program when callbacks is imported. Data is imported when the callbacks
module imports the data module.
"""
import dash
import dash_bootstrap_components as dbc
import flask
import utils.data
import utils.callbacks
from components.index import index_string
from components.layout import make_layout
from utils.settings import ADDRESS, APP_TITLE, PORT

CSS = [
    dbc.themes.SPACELAB,
    # "assets/css/common.css",
    # "assets/css/custom.css",
    # "assets/css/03_style.css",
    # # "assets/uswds/dist/css/uswds.css"
]

# f_app = flask.Flask(__name__)
# Initialize App
app = dash.Dash(
    __name__,
    assets_folder="assets",
    external_stylesheets=CSS,
    title=APP_TITLE,
    # server=f_app,
)  # type: ignore  # pylance doesn't think f_app is suitable.
# server = app.server  # Important for debugging and using Flask!
app.index_string = index_string

app.layout = make_layout()

if __name__ == "__main__":
    app.run_server(
        debug=False,
        port=PORT,
        host=ADDRESS,
        threaded=True,
    )
