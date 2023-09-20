import textwrap
from itertools import cycle, islice
from typing import List

import pandas as pd


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
    dataframe["staid"] = (
        dataframe["station_nm"].str.slice(14).str.strip().apply(pd.Series)
    )
    dataframe["station_id_num"] = "USGS-" + dataframe["station_id_num"]
    return dataframe[["staid", "station_id_num", "dec_lat_va", "dec_long_va"]]


def add_xline(fig, smcl):
    if smcl != "p00300":
        fig.add_vline(
            x=smcl,
            annotation_text=f"EPA SDWR: {smcl}",
        )
    else:
        fig.add_vline(
            x=0.5,  # 0.5 mg/L is Anoxic
            annotation_text="Anoxic: 0.5",
        )
    return fig


def add_yline(fig, smcl):
    if smcl != "p00300":
        fig.add_hline(
            y=smcl,
            annotation_text=f"EPA SDWR: {smcl}",
        )
    else:
        fig.add_hline(
            y=0.5,  # 0.5 mg/L is Anoxic
            annotation_text="Anoxic: 0.5",
        )
    return fig


def filter_x_data(data, station_nm, start_date, end_date, param_x):
    # .isin() method needs a list for querying properly.
    if isinstance(station_nm, str):
        station_nm = [station_nm]

    pcode_mask = data["USGSPCode"] == param_x
    staid_date_mask = (
        (data["station_nm"].isin(station_nm))
        & (data["ActivityStartDate"] >= str(start_date))
        & (data["ActivityStartDate"] <= end_date)
    )
    return data.loc[staid_date_mask & pcode_mask]


def filter_xy_data(data, station_nm, start_date, end_date, param_x, param_y):
    if isinstance(station_nm, str):
        station_nm = [station_nm]

    pcode_mask = (data["USGSPCode"] == param_x) | (data["USGSPCode"] == param_y)
    staid_date_mask = (
        (data["station_nm"].isin(station_nm))
        & (data["ActivityStartDate"] >= str(start_date))
        & (data["ActivityStartDate"] <= end_date)
    )
    return data.loc[staid_date_mask & pcode_mask]


def filter_xyz_data(data, station_nm, start_date, end_date, param_x, param_y, param_z):
    if isinstance(station_nm, str):
        station_nm = [station_nm]

    pcode_mask = (
        (data["USGSPCode"] == param_x)
        | (data["USGSPCode"] == param_y)
        | (data["USGSPCode"] == param_z)
    )
    staid_date_mask = (
        (data["station_nm"].isin(station_nm))
        & (data["ActivityStartDate"] >= str(start_date))
        & (data["ActivityStartDate"] <= end_date)
    )
    return data.loc[staid_date_mask & pcode_mask]


def filter_nondetect_data(data: pd.DataFrame) -> pd.DataFrame | None:
    """Find nondetect values in dataframe and return them as a stand alone dataframe

    Parameters
    ----------
    data : pd.DataFrame
        Input data to be check for nondetects

    Returns
    -------
    pd.DataFrame | None
        Dataframe of nondetect values.
    """
    non_detect_df = data.loc[data["ResultDetectionConditionText"] == "Not Detected"]
    return None if non_detect_df.empty else non_detect_df


def filter_nodata_data(
    no_data: pd.DataFrame, staids: str | list, checklist: str | list
) -> pd.DataFrame | None:
    """Find stations with no data and return a no_data dataframe

    Parameters
    ----------
    no_data : pd.DataFrame
        Dataframe containing no_data representations of all stations
    station_nm : str | list
        String or list of station names to check for no data

    Returns
    -------
    pd.DataFrame | None
        Dataframe containing no_data representation of stations without valid data
    """
    if isinstance(staids, str):
        staids = [staids]
    if isinstance(checklist, str):
        checklist = [checklist]

    no_data_df = no_data.loc[
        ~no_data["staid"].isin(staids) & no_data["station_nm"].isin(checklist)
    ]
    return None if no_data_df.empty else no_data_df


def make_nodata_df(station_nms, staid_metadata):
    # Setup a dataframe to handle missing values when plotting on the map.
    # Every well should plot, and if no data is found, display a black marker and Result = No Data when hovering.
    nodata_df = pd.DataFrame(
        {
            "station_nm": station_nms,
            "datetime": ["1970-01-01 00:00:00" for _ in station_nms],
            "ResultMeasureValue": [float("NaN") for _ in station_nms],
            "Result": ["No Data" for _ in station_nms],
        }
    )
    nodata_df_staids = pd.merge(nodata_df, staid_metadata, on="station_nm", how="left")
    return nodata_df_staids.loc[
        :,
        [
            "station_nm",
            "staid",
            "datetime",
            "Result",
            "ResultMeasureValue",
            "dec_lat_va",
            "dec_long_va",
        ],
    ]


# return nodata_df_staids.rename(
#     columns={
#         "station_nm": "Station Name",
#         "staid": "Station ID",
#         "dec_lat_va": "Latitude",
#         "dec_long_va": "Longitude",
#         "datetime": "Sample Date",
#     }
# )


def roundrobin(*iterables):
    """
    Notes
    -----
    Source: https://docs.python.org/3/library/itertools.html#itertools-recipes
    Can be installed: python -m pip install more-itertools
    """
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    num_active = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while num_active:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            # Remove the iterator we just exhausted from the cycle.
            num_active -= 1
            nexts = cycle(islice(nexts, num_active))
