# --------------------------
# sensors/sensor_reader.py
# --------------------------

import time
import random
import pandas as pd
import joblib
from datetime import datetime
import sqlite3
import os

# --------------------------
# Load trained Random Forest model
# --------------------------
MODEL_FILE = "../model/rf_model_time_based.joblib"
rf_model = joblib.load(MODEL_FILE)

# --------------------------
# System parameters
# --------------------------
I_RATED = 20.0
INTERVAL = 1.0  # seconds between readings

# --------------------------
# Database setup
# --------------------------
DB_FILE = "../logs/system_log.db"
os.makedirs("../logs", exist_ok=True)

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Create table if it doesn't exist
c.execute("""
CREATE TABLE IF NOT EXISTS system_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Timestamp TEXT,
    Itotal REAL,
    Tbreaker REAL,
    ThermalSlope REAL,
    TimeAboveRated INTEGER,
    TimeTempRising INTEGER,
    PredictedState TEXT
)
""")
conn.commit()

# --------------------------
# Initial values for memory
# --------------------------
prev_temp = 60.0
TimeAboveRated = 0
TimeTempRising = 0

print("\nStarting continuous sensor reading and ML prediction...\n")

# --------------------------
# Sensor reading functions
# --------------------------
def read_current_sensor():
    """Replace this with actual current sensor reading."""
    return round(random.uniform(5, 30), 2)  # simulated for now

def read_temperature_sensor():
    """Replace this with actual temperature sensor reading."""
    global prev_temp
    if read_current_sensor() > I_RATED:
        temp = prev_temp + random.uniform(0.3, 1.5)
    else:
        temp = prev_temp + random.uniform(-0.5, 0.3)
    return round(temp, 2)

# --------------------------
# Continuous loop
# --------------------------
try:
    while True:
        # --------------------------
        # Read sensors
        # --------------------------
        Itotal = read_current_sensor()
        Tbreaker = read_temperature_sensor()

        # --------------------------
        # Compute derived features
        # --------------------------
        ThermalSlope = round((Tbreaker - prev_temp) / INTERVAL, 2)

        if Itotal > I_RATED:
            TimeAboveRated += 1
        else:
            TimeAboveRated = 0

        if Tbreaker > prev_temp:
            TimeTempRising += 1
        else:
            TimeTempRising = 0

        # --------------------------
        # Predict system state
        # --------------------------
        X_live = pd.DataFrame([{
            "Itotal": Itotal,
            "Tbreaker": Tbreaker,
            "ThermalSlope": ThermalSlope,
            "TimeAboveRated": TimeAboveRated,
            "TimeTempRising": TimeTempRising
        }])
        predicted_state = rf_model.predict(X_live)[0]

        # --------------------------
        # Log to SQLite
        # --------------------------
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""
        INSERT INTO system_log (Timestamp, Itotal, Tbreaker, ThermalSlope, TimeAboveRated, TimeTempRising, PredictedState)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, Itotal, Tbreaker, ThermalSlope, TimeAboveRated, TimeTempRising, predicted_state))
        conn.commit()

        # --------------------------
        # Display
        # --------------------------
        print(f"[{timestamp}] Itotal={Itotal:5.2f} A | Tbreaker={Tbreaker:6.2f} °C | STATE → {predicted_state}")

        prev_temp = Tbreaker
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\nMonitoring stopped by user.")
    conn.close()
