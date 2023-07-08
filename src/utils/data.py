import io
import requests
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


def get_qwp_data(staid_list, start_lo, start_hi):
# Query QWP for data
    response = requests.post(
        url="https://www.waterqualitydata.us/data/Result/search?",
        data={
            "siteid": [staid_list],
            "startDateLo": start_lo,
            "startDateHi": start_hi,
            "service": "results",
        },
        headers={"user-agent": "python"},
    )

    # Load and scrub QWP data
    decode_response = io.StringIO(response.content.decode("utf-8"))
    dataframe = pd.read_csv(decode_response, dtype={"USGSPCode": str})
    dataframe["USGSPCode"] = "p" + dataframe["USGSPCode"]
    dataframe.rename(columns={"MonitoringLocationIdentifier": "staid"}, inplace=True)
    dataframe["datetime"] = dataframe["ActivityStartDate"] + " " + dataframe["ActivityStartTime/Time"]
    dataframe["ValueAndUnits"] = dataframe["ResultMeasureValue"].astype(str) + " " + dataframe["ResultMeasure/MeasureUnitCode"].astype(str)
    dataframe.loc[dataframe["ValueAndUnits"] == "nan nan", "ValueAndUnits"] = "No Value"
    dataframe.loc[(dataframe["ValueAndUnits"] == "No Value") & (dataframe["ResultDetectionConditionText"] == "Not Detected"), "ValueAndUnits"] = "Not Detected"
    dataframe = dataframe.loc[(dataframe["ActivityTypeCode"] == "Sample-Routine")]
    dataframe["ResultMeasure/MeasureUnitCode"] = dataframe["ResultMeasure/MeasureUnitCode"].str.replace("asNO2", "as NO2")
    dataframe["ResultMeasure/MeasureUnitCode"] = dataframe["ResultMeasure/MeasureUnitCode"].str.replace("asNO3", "as NO3")
    dataframe["ResultMeasure/MeasureUnitCode"] = dataframe["ResultMeasure/MeasureUnitCode"].str.replace("asPO4", "as PO4")
    dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"].str.replace("asNO2", "as NO2")
    dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"].str.replace("asNO3", "as NO3")
    dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"].str.replace("asPO4", "as PO4")
    dataframe["param_label"] = dataframe["CharacteristicName"] + ", " + dataframe["ResultSampleFractionText"].fillna("") + ", " + dataframe["ResultMeasure/MeasureUnitCode"].fillna("")
    dataframe["param_label"] = dataframe["param_label"].str.replace(", , ", ", ")
    dataframe["param_label"] = dataframe["param_label"].str.replace("deg C, deg C", "deg C")
    dataframe["param_label"] = dataframe["param_label"].str.rstrip(", ")
    return dataframe