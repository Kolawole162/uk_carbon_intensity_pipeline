"""Transform: flatten the API response and aggregate it to one row per region per day."""
from datetime import date, timedelta

import pandas as pd

FUELS = ["biomass", "coal", "imports", "gas", "nuclear", "other", "hydro", "solar", "wind"]


def flatten(data: list) -> list:
    """Turn nested API intervals into one flat record per region per half-hour."""
    records = []
    for interval in data:
        for region in interval["regions"]:
            row = {
                "regionid": region["regionid"],
                "shortname": region["shortname"],
                "dno": region["dnoregion"],
                "intensity": region["intensity"]["forecast"],
                "index": region["intensity"]["index"],
            }
            for fuel in region["generationmix"]:
                row[fuel["fuel"]] = fuel["perc"]
            records.append(row)
    return records


def aggregate_daily(records: list, target_date: date) -> pd.DataFrame:
    """Average each region's half-hour values into one daily row.

    The API's pt24h endpoint returns the 24 hours BEFORE target_date,
    so the data belongs to the previous day.
    """
    df = pd.DataFrame(records)
    for fuel in FUELS:  # a fuel the API didn't report counts as 0%
        if fuel not in df.columns:
            df[fuel] = 0.0

    rules = {"shortname": "first", "dno": "first", "intensity": "mean",
             "index": lambda s: s.mode().iloc[0]}
    rules.update({fuel: "mean" for fuel in FUELS})

    daily = df.groupby("regionid").agg(rules).reset_index()
    daily["date_recorded"] = target_date - timedelta(days=1)
    return daily.round(2)