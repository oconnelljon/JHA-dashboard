# Load environment and configuration variables
import configparser
import os
from dotenv import load_dotenv

load_dotenv()
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")
PORT = os.getenv("PORT")
ADDRESS = os.getenv("ADDRESS")

# load configuration variables
config = configparser.ConfigParser()
config.read("config.cfg")

# Set defaults, load local data
APP_TITLE = config["DEFAULTS"]["APP_TITLE"]
DEFAULT_PCODE = config["DEFAULTS"]["DEFAULT_PCODE"]
MAPBOX_BASELAYER_STYLE = config["DEFAULTS"]["MAPBOX_BASELAYER_STYLE"]
default_start_date_lo = config["DEFAULTS"]["default_start_date_lo"]
default_start_date_hi = config["DEFAULTS"]["default_start_date_hi"]
staid_metadata_path = config["DEFAULTS"]["staid_metadata_path"]
# default_start_date = pd.Timestamp.today().strftime("%m-%d-%Y")
