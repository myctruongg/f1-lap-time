
import fastf1
import pandas as pd
from pathlib import Path

YEAR = 2026

output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

# Get the 2026 race schedule
schedule = fastf1.get_event_schedule(YEAR)
races = schedule[schedule["RoundNumber"] > 0]

for _, race in races.iterrows():
    round_number = int(race["RoundNumber"])
    event_name = race["EventName"]

    race_name = (
        event_name.lower()
        .replace(" grand prix", "")
        .replace(" ", "_")
        .replace("-", "_")
    )

    output_file = output_dir / f"{race_name}_{YEAR}_turns.csv"

    print(f"\nProcessing Round {round_number}: {event_name}")

    try:
        # Load race data and telemetry
        session = fastf1.get_session(YEAR, round_number, "R")
        session.load(
            laps=True,
            telemetry=True,
            weather=False,
            messages=False
        )

        # Get circuit corner markers
        circuit = session.get_circuit_info()

        if circuit is None or circuit.corners.empty:
            print("Skipping: no corner data")
            continue

        corners = circuit.corners

        # Filter usable laps
        laps = session.laps[
            (session.laps["IsAccurate"] == True) &
            (session.laps["PitInTime"].isna()) &
            (session.laps["PitOutTime"].isna()) &
            (session.laps["Sector1Time"].notna()) &
            (session.laps["Sector2Time"].notna()) &
            (session.laps["Sector3Time"].notna())
        ]

        rows = []

        for _, lap in laps.iterlaps():
            try:
                telemetry = lap.get_telemetry()

                if telemetry.empty:
                    continue

                # Find sector boundaries
                s1 = lap["Sector1Time"].total_seconds()
                s2 = lap["Sector2Time"].total_seconds()

                times = telemetry["Time"].dt.total_seconds()

                s1_end = telemetry.iloc[
                    (times - s1).abs().argmin()
                ]["Distance"]

                s2_end = telemetry.iloc[
                    (times - (s1 + s2)).abs().argmin()
                ]["Distance"]

                # Extract turn measurements
                for _, corner in corners.iterrows():
                    corner_distance = corner["Distance"]

                    closest = telemetry.iloc[
                        (telemetry["Distance"] - corner_distance)
                        .abs().argmin()
                    ]

                    if corner_distance < s1_end:
                        sector = 1
                    elif corner_distance < s2_end:
                        sector = 2
                    else:
                        sector = 3

                    rows.append({
                        "Race": event_name,
                        "Driver": lap["Driver"],
                        "LapNumber": int(lap["LapNumber"]),
                        "Turn": int(corner["Number"]),
                        "Sector": sector,
                        "Speed": round(float(closest["Speed"]), 2),
                        "Gear": int(closest["nGear"])
                    })

            except Exception as e:
                print(
                    f"Skipping {lap['Driver']} "
                    f"lap {lap['LapNumber']}: {e}"
                )

        if not rows:
            print("No usable turn measurements")
            continue

        # Save one CSV per race
        turns_df = pd.DataFrame(rows)
        turns_df.to_csv(output_file, index=False)

        print(
            f"Saved {len(turns_df)} turn measurements "
            f"to {output_file}"
        )

    except Exception as e:
        print(f"Skipping {event_name}: {e}")

print("\nFinished processing available 2026 races!")
