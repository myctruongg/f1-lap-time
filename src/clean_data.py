
import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/processed/f1_2026_combined.csv")
OUTPUT_FILE = Path("data/processed/f1_2026_cleaned.csv")

# Load combined dataset
df = pd.read_csv(INPUT_FILE)

print("Original rows:", len(df))

# Convert lap and sector times into seconds
time_columns = [
    "LapTime",
    "Sector1Time",
    "Sector2Time",
    "Sector3Time"
]

for col in time_columns:
    df[col] = pd.to_timedelta(
        df[col], errors="coerce"
    ).dt.total_seconds()

# Keep accurate, non-deleted laps without pit entry/exit
df = df[
    (df["IsAccurate"] == True) &
    (df["Deleted"] != True) &
    (df["PitInTime"].isna()) &
    (df["PitOutTime"].isna())
].copy()

# Select columns needed for modeling and interpretation
columns = [
    "RaceID",
    "Driver",
    "LapNumber",
    "LapTime",
    "Sector1Time",
    "Sector2Time",
    "Sector3Time",
    "AvgTurnSpeedS1",
    "AvgTurnSpeedS2",
    "AvgTurnSpeedS3",
    "AvgTurnGearS1",
    "AvgTurnGearS2",
    "AvgTurnGearS3",
    "Compound",
    "TyreLife",
    "FreshTyre"
]

df = df[columns]

# Remove rows with missing essential values
df = df.dropna()

# Remove duplicate driver laps
df = df.drop_duplicates(
    subset=["RaceID", "Driver", "LapNumber"]
)

# Convert lap number to integer
df["LapNumber"] = df["LapNumber"].astype(int)

# Round numerical features for readability
numeric_columns = [
    "LapTime",
    "Sector1Time",
    "Sector2Time",
    "Sector3Time",
    "AvgTurnSpeedS1",
    "AvgTurnSpeedS2",
    "AvgTurnSpeedS3",
    "AvgTurnGearS1",
    "AvgTurnGearS2",
    "AvgTurnGearS3"
]

df[numeric_columns] = df[numeric_columns].round(3)

# Save cleaned dataset
df.to_csv(OUTPUT_FILE, index=False)

print("Cleaned rows:", len(df))
print("Removed rows:", len(pd.read_csv(INPUT_FILE)) - len(df))
print("Saved to:", OUTPUT_FILE)

print("\nSample cleaned data:")
print(df.head())
