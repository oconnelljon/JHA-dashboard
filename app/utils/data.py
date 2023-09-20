# data.py


import io

import pandas as pd
import requests
import utils.common as com
import utils.settings as configs
from natsort import natsorted

# def get_meta_data(staids: List) -> pd.DataFrame:
#     # staids = [433615110440001, 433600110443701, 433604110443402]
#     staid_str = ",".join(str(staid) for staid in staids)
#     url = f"https://waterservices.usgs.gov/nwis/site/?format=rdb&sites={staid_str}&siteOutput=expanded&siteStatus=all"
#     # s=requests.get(url).text
#     dataframe = pd.read_csv(url, sep="\t", comment="#")
#     dataframe = dataframe.drop(index=0)
#     dataframe = dataframe.rename(columns={"site_no": "staid"})
#     dataframe[["station_str", "station_name"]] = dataframe["station_nm"].str.split(" ").apply(pd.Series)
#     return dataframe[["staid", "station_name", "dec_lat_va", "dec_long_va"]]


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
    if dataframe.empty is True:
        print("No data from qwp!")
        raise SystemExit
    dataframe["USGSPCode"] = "p" + dataframe["USGSPCode"]
    dataframe.rename(columns={"MonitoringLocationIdentifier": "staid"}, inplace=True)
    dataframe["datetime"] = (
        dataframe["ActivityStartDate"] + " " + dataframe["ActivityStartTime/Time"]
    )
    dataframe["ValueAndUnits"] = (
        dataframe["ResultMeasureValue"].astype(str)
        + " "
        + dataframe["ResultMeasure/MeasureUnitCode"].astype(str)
    )
    dataframe.loc[dataframe["ValueAndUnits"] == "nan nan", "ValueAndUnits"] = "No Value"
    dataframe.loc[
        (dataframe["ValueAndUnits"] == "No Value")
        & (dataframe["ResultDetectionConditionText"] == "Not Detected"),
        "ValueAndUnits",
    ] = "Not Detected"
    dataframe = dataframe.loc[(dataframe["ActivityTypeCode"] == "Sample-Routine")]
    dataframe["ResultMeasure/MeasureUnitCode"] = dataframe[
        "ResultMeasure/MeasureUnitCode"
    ].str.replace("asNO2", "as NO2")
    dataframe["ResultMeasure/MeasureUnitCode"] = dataframe[
        "ResultMeasure/MeasureUnitCode"
    ].str.replace("asNO3", "as NO3")
    dataframe["ResultMeasure/MeasureUnitCode"] = dataframe[
        "ResultMeasure/MeasureUnitCode"
    ].str.replace("asPO4", "as PO4")
    dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = dataframe[
        "DetectionQuantitationLimitMeasure/MeasureUnitCode"
    ].str.replace("asNO2", "as NO2")
    dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = dataframe[
        "DetectionQuantitationLimitMeasure/MeasureUnitCode"
    ].str.replace("asNO3", "as NO3")
    dataframe["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = dataframe[
        "DetectionQuantitationLimitMeasure/MeasureUnitCode"
    ].str.replace("asPO4", "as PO4")
    dataframe["param_label"] = (
        dataframe["CharacteristicName"]
        + ", "
        + dataframe["ResultSampleFractionText"].fillna("")
        + ", "
        + dataframe["ResultMeasure/MeasureUnitCode"].fillna("")
    )
    dataframe["param_label"] = dataframe["param_label"].str.replace(", , ", ", ")
    dataframe["param_label"] = dataframe["param_label"].str.replace(
        "deg C, deg C", "deg C"
    )
    dataframe["param_label"] = dataframe["param_label"].str.rstrip(", ")
    return dataframe


# Read in station meta data
staid_meta_data = pd.read_csv(configs.staid_metadata_path)
STAID_LIST = list(staid_meta_data["staid"])
STATION_NMs = natsorted(list(staid_meta_data["station_nm"]))
NODATA_DF = com.make_nodata_df(STATION_NMs, staid_meta_data)

# Create dictionary of parameter labels and values for the App to display
qwp_download = get_qwp_data(
    staid_list=STAID_LIST,
    start_lo=configs.default_start_date_lo,
    start_hi=configs.default_start_date_hi,
)
available_parameters = qwp_download.drop_duplicates("param_label")
available_parameters = available_parameters.sort_values(
    by="param_label", key=lambda col: col.str.lower()
)
available_param_dict = dict(
    zip(available_parameters["USGSPCode"], available_parameters["param_label"])
)
available_param_labels = [
    {"label": label, "value": pcode}
    for label, pcode in zip(
        available_parameters["param_label"], available_parameters["USGSPCode"]
    )
]

# Query all data at the start of the App, then sort intermediates to pass to Callbacks
ALL_DATA_DF = pd.merge(qwp_download, staid_meta_data, on="staid", how="left")
ALL_DATA_DF.sort_values(by="datetime", ascending=True, inplace=True)
ALL_DATA_DF = ALL_DATA_DF.loc[
    :,
    [
        "ActivityStartDate",
        "ActivityStartTime/Time",
        "staid",
        "station_nm",
        "ResultDetectionConditionText",
        "CharacteristicName",
        "ResultSampleFractionText",
        "ResultMeasureValue",
        "ResultMeasure/MeasureUnitCode",
        "USGSPCode",
        "DetectionQuantitationLimitTypeName",
        "DetectionQuantitationLimitMeasure/MeasureValue",
        "DetectionQuantitationLimitMeasure/MeasureUnitCode",
        "datetime",
        "ValueAndUnits",
        "param_label",
        "dec_lat_va",
        "dec_long_va",
    ],
]
