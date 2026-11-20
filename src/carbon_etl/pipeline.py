"""Run the pipeline for one day.

Usage (from the repo root):  python -m carbon_etl.pipeline [YYYY-MM-DD]
"""
import sys
from datetime import date, timedelta
from pathlib import Path

from carbon_etl.db import get_engine
from carbon_etl.extract import fetch_day
from carbon_etl.load import load_day
from carbon_etl.transform import aggregate_daily, flatten, keep_day


def run(target_date: date):
    day = target_date - timedelta(days=1)
    data = keep_day(fetch_day(target_date), day)
    print(f"Kept {len(data)} intervals for {day}")
    daily = aggregate_daily(flatten(data), target_date)

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"carbon_daily_{daily['date_recorded'].iloc[0]}.csv"
    daily.to_csv(out_file, index=False)
    print(f"Saved {len(daily)} regions to {out_file}")

    load_day(daily, get_engine())
    return daily


if __name__ == "__main__":
    target = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    run(target)