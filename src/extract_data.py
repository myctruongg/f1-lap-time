
import fastf1
from pathlib import Path

# Where our CSV files will be saved
raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

# Get the official 2026 F1 event schedule
schedule = fastf1.get_event_schedule(2026)

# Keep only conventional Grand Prix race weekends
races = schedule[
    (schedule["EventFormat"] != "testing") &
    (schedule["EventFormat"] != "testing1") &
    (schedule["EventFormat"] != "testing2") &
    (schedule["EventFormat"] != "testing3") &
    (schedule["RoundNumber"] > 0)
]

# Loop through each race
for _, race in races.iterrows():

    round_number = int(race["RoundNumber"])
    event_name = race["EventName"]

    print(f"\nLoading Round {round_number}: {event_name}")

    try:
        # Load this race's data
        session = fastf1.get_session(2026, round_number, "R")

        session.load(
            laps=True,
            telemetry=False,
            weather=True,
            messages=False
        )

        # Skip sessions without lap data
        if session.laps.empty:
            print(f"Skipping {event_name}: no lap data")
            continue

        # Generate a filename from the event name
        race_name = (
            event_name.lower()
            .replace(" grand prix", "")
            .replace(" ", "_")
            .replace("-", "_")
        )

        # Save lap data
        laps_file = raw_dir / f"{race_name}_2026_laps.csv"

        session.laps.to_csv(
            laps_file,
            index=False
        )

        print(f"Saved: {laps_file}")

        # Save weather data
        if session.weather_data is not None and not session.weather_data.empty:

            weather_file = raw_dir / f"{race_name}_2026_weather.csv"

            session.weather_data.to_csv(
                weather_file,
                index=False
            )

            print(f"Saved: {weather_file}")

        else:
            print(f"No weather data for {event_name}")

    except Exception as e:
        print(f"Failed to load {event_name}: {e}")
        continue

print("\nFinished processing available 2026 races!")
