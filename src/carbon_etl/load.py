"""Load: write one day of data into PostgreSQL. Safe to re-run for the same day."""
import pandas as pd
from sqlalchemy import text

from carbon_etl.transform import FUELS


def load_day(daily: pd.DataFrame, engine) -> None:
    day = daily["date_recorded"].iloc[0]

    regions = [
        {"regionid": int(r.regionid), "shortname": str(r.shortname), "dno": str(r.dno)}
        for r in daily.itertuples()
    ]
    intensity = daily[["regionid", "date_recorded", "intensity", "index"]].rename(
        columns={"index": "intensity_index"}
    )
    mix = daily[["regionid", "date_recorded", *FUELS]]

    # One transaction: if any step fails, nothing is saved (all or nothing)
    with engine.begin() as conn:
        # 1. Add new regions, or update names of existing ones
        conn.execute(
            text("""
                INSERT INTO carbon.dim_region (regionid, shortname, dno)
                VALUES (:regionid, :shortname, :dno)
                ON CONFLICT (regionid) DO UPDATE
                SET shortname = EXCLUDED.shortname, dno = EXCLUDED.dno
            """),
            regions,
        )
        # 2. Remove any earlier rows for this day, so a re-run replaces them
        for table in ("fact_carbon_intensity", "fact_generation_mix"):
            conn.execute(text(f"DELETE FROM carbon.{table} WHERE date_recorded = :day"), {"day": day})

        # 3. Insert today's rows
        intensity.to_sql("fact_carbon_intensity", conn, schema="carbon", if_exists="append", index=False)
        mix.to_sql("fact_generation_mix", conn, schema="carbon", if_exists="append", index=False)

    print(f"Loaded {len(daily)} regions for {day} (any earlier rows for that day were replaced)")