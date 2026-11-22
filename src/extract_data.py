"""Download clean, dry Bahrain race laps and attach track temperature."""

from argparse import ArgumentParser
from pathlib import Path

import fastf1
import pandas as pd
from fastf1.exceptions import DataNotLoadedError

ROOT = Path(__file__).resolve().parents[1]
YEARS = (2021, 2022)
COMPOUNDS = ("SOFT", "MEDIUM", "HARD")


def extract_race(year):
    race = fastf1.get_session(year, "Bahrain Grand Prix", "R", exact_match=True)
    race.load(telemetry=False, messages=True)
    laps = race.laps
    clean = laps.loc[
        laps["IsAccurate"].eq(True)
        & ~laps["Deleted"].eq(True)
        & laps["TrackStatus"].eq("1")
        & laps["PitInTime"].isna()
        & laps["PitOutTime"].isna()
        & laps["LapNumber"].gt(1)
        & laps["Compound"].isin(COMPOUNDS)
    ].reset_index(drop=True)
    weather = clean.get_weather_data().reset_index(drop=True)
    data = pd.DataFrame({
        "year": year,
        "driver": clean["Driver"],
        "compound": clean["Compound"],
        "tire_age": clean["TyreLife"],
        "race_lap": clean["LapNumber"],
        "track_temp": weather["TrackTemp"],
        "lap_seconds": clean["LapTime"].dt.total_seconds(),
    })
    return data.loc[weather["Rainfall"].eq(False)].dropna()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--years", nargs="+", type=int, default=YEARS)
    args = parser.parse_args()
    cache = ROOT / ".cache" / "fastf1"
    cache.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache))
    frames = []
    for year in sorted(set(args.years)):
        try:
            laps = extract_race(year)
        except DataNotLoadedError as error:
            print(f"Skipping {year} Bahrain GP: {error}")
            continue
        if laps.empty:
            print(f"Skipping {year} Bahrain GP: no usable laps.")
            continue
        print(f"{year} Bahrain GP: {len(laps)} clean laps")
        frames.append(laps)
    if len(frames) < 2:
        raise RuntimeError("Need at least two Bahrain races with usable laps.")
    output = ROOT / "artifacts" / "laps.csv"
    output.parent.mkdir(exist_ok=True)
    pd.concat(frames, ignore_index=True).to_csv(output, index=False)


if __name__ == "__main__":
    main()
