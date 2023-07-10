# Load environment variables
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

# default_start_date = pd.Timestamp.today().strftime("%m-%d-%Y")
