from datetime import date, datetime
import dataretrieval.nwis as nwis
import pandas as pd
import json


# df = nwis.get_record(sites="12323840", service="qwdata", start="2020-03-01", end="2020-10-01", parameterCd="00925")
STAID_coord = pd.read_csv("src/data/site_data.csv")
pause = 2

# pd.to_numeric(df['p00925'], errors='coerce').dtype
