import pandas as pd
from typing import List


def get_meta_data(staids: List) -> pd.DataFrame:
    # staids = [433615110440001, 433600110443701, 433604110443402]
    staid_str = ",".join(str(staid) for staid in staids)
    url = f"https://waterservices.usgs.gov/nwis/site/?format=rdb&sites={staid_str}&siteOutput=expanded&siteStatus=all"
    # s=requests.get(url).text
    dataframe = pd.read_csv(url, sep="\t", comment="#")
    dataframe = dataframe.drop(index=0)
    dataframe = dataframe.rename(columns={"site_no": "staid"})
    dataframe[["station_str", "station_name"]] = dataframe["station_nm"].str.split(" ").apply(pd.Series)
    return dataframe[["staid", "station_name", "dec_lat_va", "dec_long_va"]]
