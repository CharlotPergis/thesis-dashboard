import time
import random
import pandas as pd
import joblib
from datetime import datetime
import os

# --------------------------
# Load trained model
# --------------------------
rf_model = joblib.load("../model/rf_model_time_based.joblib")

# --------------------------
# System parameters
# --------------------------
I_RATED = 20.0
INTERVAL = 1.0  # seconds

# --------------------------
# Logging setup
# --------------------------
LOG_DIR = "../logs"
LOG_FILE = os.path.join(LOG_DIR, "system_log.csv")

os.makedirs(LOG_DIR, exist_ok=True)

# Create CSV header if file does not exist
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=[
        "Timestamp",
        "Itotal",
        "Tbreaker",
        "ThermalSlope",
        "TimeAboveRated",
        "TimeTempRising",
        "PredictedState"
    ]).to_csv(LOG_FILE, index=False)

# --------------------------
# Initial values (memory)
# --------------------------
prev_temp = 60.0
TimeAboveRated = 0
TimeTempRising = 0

print("\nStarting real-time monitoring with ML prediction + logging...\n")

# --------------------------
# Real-time loop
# --------------------------
for t in range(1, 31):
    Itotal = round(random.uniform(5, 30), 2)

    if Itotal > I_RATED:
        Tbreaker = prev_temp + random.uniform(0.3, 1.5)
    else:
        Tbreaker = prev_temp + random.uniform(-0.5, 0.3)

    Tbreaker = round(Tbreaker, 2)

    ThermalSlope = round((Tbreaker - prev_temp) / INTERVAL, 2)

    if Itotal > I_RATED:
        TimeAboveRated += 1
    else:
        TimeAboveRated = 0

    if Tbreaker > prev_temp:
        TimeTempRising += 1
    else:
        TimeTempRising = 0

    # ML input
    X_live = pd.DataFrame([{
        "Itotal": Itotal,
        "Tbreaker": Tbreaker,
        "ThermalSlope": ThermalSlope,
        "TimeAboveRated": TimeAboveRated,
        "TimeTempRising": TimeTempRising
    }])

    predicted_state = rf_model.predict(X_live)[0]

    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log entry
    log_row = pd.DataFrame([{
        "Timestamp": timestamp,
        "Itotal": Itotal,
        "Tbreaker": Tbreaker,
        "ThermalSlope": ThermalSlope,
        "TimeAboveRated": TimeAboveRated,
        "TimeTempRising": TimeTempRising,
        "PredictedState": predicted_state
    }])

    log_row.to_csv(LOG_FILE, mode="a", header=False, index=False)

    # Display
    print(
        f"[{timestamp}] "
        f"Itotal={Itotal:5.2f} A | "
        f"Tbreaker={Tbreaker:6.2f} °C | "
        f"STATE → {predicted_state}"
    )

    prev_temp = Tbreaker
    time.sleep(INTERVAL)

print("\nMonitoring finished. Data saved to logs/system_log.csv")
