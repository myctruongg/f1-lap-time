# F1 Predictor

F1 Predictor is a hackathon project that uses Formula 1 timing and telemetry
to make race predictions. The first goal is to predict a driver's lap time
from the circuit's corner and sector profiles. Estimating a driver's probability
of winning a race is a possible follow-up.

## Run the React website

From the repository root, install the frontend dependencies and start Vite.

```sh
npm --prefix web ci
npm --prefix web run dev
```

Open the local URL Vite prints and choose **Lap Time** from the feature menu.
Select a track, driver, and weather condition,
then choose **Calculate lap time**. The website uses React and Tailwind CSS.
Its demo formula uses illustrative driver offsets and a weather adjustment
that varies with the circuit's mix of corners and straights. The model
integration point is [`predictLap`](web/src/prediction.js).

For VS Code Live Server, run `npm --prefix web run build` from the repository
root and open `web/dist/index.html` with Live Server. For automatic updates as
you edit, open the Vite URL in the VS Code browser. Vite processes the JSX and
Tailwind used by the source entry point in `web/index.html`.

## Planned telemetry-based lap predictor

1. **Profile each corner.** Use FastF1 circuit markers as approximate corner
   locations and align them with speed and gear telemetry by lap distance.
   Define repeatable entry, apex, and exit sampling points around each marker.
   Average the speed measurements from representative historical laps and
   summarize the typical gear at each point.
2. **Group corners by speed.** Standardize the corner features and fit
   K-means with three clusters. Label the clusters slow, medium, and fast
   by their typical apex speed. Map corners to the official timing sectors
   and summarize each sector by its mix of corner types. Show a dominant
   type in the demo when a sector has one, and retain the full mix for
   modeling. Include sector length to capture distance between corners.
3. **Predict sector times.** Start with the historical median time for each
   sector. Then train a regression model on measured sector times using the
   corner profiles and inputs available before the predicted lap, such as
   tire compound, tire age, and track temperature. Build the corner profiles
   from training laps so telemetry from the predicted lap stays out of its
   inputs.
4. **Add the three sector estimates.** Predict total lap time as Sector 1 +
   Sector 2 + Sector 3, in seconds. Hold out whole races when enough sessions
   are available. Report mean absolute error for both sectors and laps and
   compare against the median baseline and the existing lap-level model.

The modeling stack uses FastF1 for timing and telemetry, pandas and NumPy
for processing, and scikit-learn for clustering and regression. The React
website is the frontend for the new predictor.

- [FastF1 data reference](https://github.com/theOehrly/Fast-F1/blob/main/docs/data_reference/index.rst)
- [scikit-learn K-means reference](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)

## Train the Python baseline

The Bahrain random forest provides a lap-level benchmark for the planned
sector model. From the repository root, set up Python and train it.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/extract_data.py
python src/train_rf.py
```

The extractor requests Bahrain Grand Prix timing and weather for 2021 and
2022 and writes usable laps to `artifacts/laps.csv`. Pass `--years` followed
by the race years to try other editions. At least two usable races are needed.
Training evaluates on the latest available race, prints the model and median
baseline error, and writes `artifacts/bahrain_model.joblib`. The React demo
runs independently of these Python artifacts.
