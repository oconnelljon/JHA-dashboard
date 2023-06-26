import textwrap
import pandas as pd
from typing import List


def title_wrapper(text: str) -> str:
    split_text = textwrap.wrap(text, 30)
    return "<br>".join(split_text)


def get_meta_data(staids: List) -> pd.DataFrame:
    # staids = [433615110440001, 433600110443701, 433604110443402]
    # staids = ["USGS-12301250", "USGS-12323233", "USGS-12340500"]
    staid_str = ",".join(str(staid[5:]) for staid in staids)
    url = f"https://waterservices.usgs.gov/nwis/site/?format=rdb&sites={staid_str}&siteOutput=expanded&siteStatus=all"
    # s=requests.get(url).text
    dataframe = pd.read_csv(url, sep="\t", comment="#")
    dataframe = dataframe.drop(index=0)
    dataframe = dataframe.rename(columns={"site_no": "station_id_num"})
    dataframe["staid"] = dataframe["station_nm"].str.slice(14).str.strip().apply(pd.Series)
    dataframe["station_id_num"] = "USGS-" + dataframe["station_id_num"]
    return dataframe[["staid", "station_id_num", "dec_lat_va", "dec_long_va"]]
