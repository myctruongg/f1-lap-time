"""Train on earlier races and score on the latest full race."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
CATEGORIES = ["driver", "compound"]
NUMERIC = ["tire_age", "race_lap", "track_temp"]
FEATURES = CATEGORIES + NUMERIC


def train(laps):
    holdout_year = int(laps["year"].max())
    training = laps.loc[laps["year"] < holdout_year]
    test = laps.loc[laps["year"] == holdout_year]
    if training.empty or test.empty:
        raise ValueError("Training requires at least two race years.")

    preprocessing = ColumnTransformer(
        [("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORIES)],
        remainder="passthrough",
    )
    model = make_pipeline(
        preprocessing,
        RandomForestRegressor(n_estimators=160, min_samples_leaf=5, random_state=42),
    )
    model.fit(training[FEATURES], training["lap_seconds"])
    predicted = model.predict(test[FEATURES])
    medians = training.groupby("compound")["lap_seconds"].median()
    baseline = test["compound"].map(medians).fillna(training["lap_seconds"].median())

    return {
        "model": model,
        "features": FEATURES,
        "drivers": sorted(training["driver"].unique()),
        "compounds": sorted(training["compound"].unique()),
        "bounds": {feature: (training[feature].min(), training[feature].max())
                   for feature in NUMERIC},
        "training_years": sorted(training["year"].unique()),
        "holdout_year": holdout_year,
        "model_mae": mean_absolute_error(test["lap_seconds"], predicted),
        "baseline_mae": mean_absolute_error(test["lap_seconds"], baseline),
        "evaluation": test[["driver", "race_lap", "lap_seconds"]].assign(predicted=predicted),
    }


def main():
    bundle = train(pd.read_csv(ARTIFACTS / "laps.csv"))
    output = ARTIFACTS / "bahrain_model.joblib"
    temporary = output.with_suffix(".tmp")
    joblib.dump(bundle, temporary)
    temporary.replace(output)
    print(f'{bundle["holdout_year"]} MAE: {bundle["model_mae"]:.3f} s '
          f'(compound baseline: {bundle["baseline_mae"]:.3f} s)')


if __name__ == "__main__":
    main()
