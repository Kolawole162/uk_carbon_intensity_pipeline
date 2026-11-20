from datetime import date

from carbon_etl.transform import aggregate_daily, flatten


def make_region(regionid, intensity, index, gas, wind):
    return {
        "regionid": regionid,
        "shortname": f"Region {regionid}",
        "dnoregion": f"DNO {regionid}",
        "intensity": {"forecast": intensity, "index": index},
        "generationmix": [{"fuel": "gas", "perc": gas}, {"fuel": "wind", "perc": wind}],
    }


SAMPLE = [
    {"from": "2026-11-19T00:00Z",
     "regions": [make_region(1, 100, "low", 40.0, 60.0), make_region(2, 300, "high", 80.0, 20.0)]},
    {"from": "2026-11-19T00:30Z",
     "regions": [make_region(1, 200, "moderate", 50.0, 50.0), make_region(2, 300, "high", 70.0, 30.0)]},
]


def test_flatten_gives_one_record_per_region_per_interval():
    records = flatten(SAMPLE)
    assert len(records) == 4
    assert records[0]["dno"] == "DNO 1"
    assert records[0]["gas"] == 40.0


def test_aggregate_averages_each_region():
    daily = aggregate_daily(flatten(SAMPLE), target_date=date(2026, 11, 20))
    region1 = daily[daily["regionid"] == 1].iloc[0]
    assert len(daily) == 2
    assert region1["intensity"] == 150
    assert region1["gas"] == 45


def test_data_is_labelled_with_the_previous_day():
    daily = aggregate_daily(flatten(SAMPLE), target_date=date(2026, 11, 20))
    assert (daily["date_recorded"] == date(2026, 11, 19)).all()


def test_most_common_index_is_kept():
    daily = aggregate_daily(flatten(SAMPLE), target_date=date(2026, 11, 20))
    assert daily[daily["regionid"] == 2].iloc[0]["index"] == "high"


def test_missing_fuels_are_filled_with_zero():
    daily = aggregate_daily(flatten(SAMPLE), target_date=date(2026, 11, 20))
    assert (daily["coal"] == 0).all()