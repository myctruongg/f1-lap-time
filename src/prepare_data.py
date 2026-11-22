
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
OUTPUT_FILE = PROCESSED_DIR / "f1_2026_combined.csv"

# Find CSV files
lap_files = sorted(RAW_DIR.glob("*_2026_laps.csv"))
turn_files = sorted(PROCESSED_DIR.glob("*_2026_turns.csv"))

print(f"Found {len(lap_files)} lap files and {len(turn_files)} turn files")

# Load lap data
lap_data = []

for file in lap_files:
    df = pd.read_csv(file)
    df["RaceID"] = file.name.replace("_2026_laps.csv", "")
    lap_data.append(df)

laps = pd.concat(lap_data, ignore_index=True)

# Load turn data
turn_data = []

for file in turn_files:
    df = pd.read_csv(file)
    df["RaceID"] = file.name.replace("_2026_turns.csv", "")
    turn_data.append(df)

turns = pd.concat(turn_data, ignore_index=True)

# Calculate average turn speed and gear per sector
turn_averages = turns.groupby(
    ["RaceID", "Driver", "LapNumber", "Sector"]
)[["Speed", "Gear"]].mean()

# Convert sectors into separate columns
turn_averages = turn_averages.unstack("Sector")

turn_averages.columns = [
    f"AvgTurn{feature}S{sector}"
    for feature, sector in turn_averages.columns
]

turn_averages = turn_averages.reset_index()

# Merge lap data with sector averages
final = laps.merge(
    turn_averages,
    on=["RaceID", "Driver", "LapNumber"],
    how="inner",
    validate="one_to_one"
)

# Save combined dataset
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
final.to_csv(OUTPUT_FILE, index=False)

print(f"Total lap records: {len(laps)}")
print(f"Total turn records: {len(turns)}")
print(f"Merged laps: {len(final)}")
print(f"Saved to: {OUTPUT_FILE}")
