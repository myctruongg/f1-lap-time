
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler

INPUT_FILE = Path("data/processed/f1_2026_cleaned.csv")
OUTPUT_FILE = Path("data/processed/f1_2026_normalized.csv")

# Load cleaned data
df = pd.read_csv(INPUT_FILE)

# Features to normalize relative to each circuit
circuit_features = [
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

# Step 1: Normalize each feature by its circuit median
relative_features = []

for feature in circuit_features:
    median = df.groupby("RaceID")[feature].transform("median")

    new_column = f"Rel{feature}"
    df[new_column] = df[feature] / median

    relative_features.append(new_column)

# Step 2: Standardize numerical features
model_features = relative_features + ["TyreLife"]

scaler = StandardScaler()

df[model_features] = scaler.fit_transform(df[model_features])

# Save normalized dataset
df.to_csv(OUTPUT_FILE, index=False)

print("Total laps:", len(df))
print("Features standardized:", len(model_features))
print("Saved to:", OUTPUT_FILE)

print("\nNormalized feature sample:")
print(df[model_features].head())
