# --------------------------
# test_rf_model_extended.py
# --------------------------
import pandas as pd
import numpy as np
import joblib

# Load the trained model
rf_model = joblib.load("../model/rf_model_time_based.joblib")

# Load synthetic dataset
df = pd.read_csv("synthetic_data_time_based.csv")

# --------------------------
# 1️⃣ Example: Single sample test
# --------------------------
single_sample = pd.DataFrame([{
    "Itotal": 26.5,
    "Tbreaker": 85.0,
    "ThermalSlope": 1.5,
    "TimeAboveRated": 3,
    "TimeTempRising": 4
}])

pred_state = rf_model.predict(single_sample)[0]
print(f"Single Sample Prediction -> Itotal={single_sample['Itotal'][0]}, "
      f"Tbreaker={single_sample['Tbreaker'][0]} => State: {pred_state}\n")

# --------------------------
# 2️⃣ Batch prediction test (CSV)
# --------------------------
X_batch = df[["Itotal", "Tbreaker", "ThermalSlope", "TimeAboveRated", "TimeTempRising"]]
y_pred = rf_model.predict(X_batch)

df["Predicted_State"] = y_pred

print("First 10 predictions from synthetic dataset:")
print(df[["Itotal", "Tbreaker", "State", "Predicted_State"]].head(10))

# --------------------------
# 3️⃣ Simulate real-time sequence (time-accumulated)
# --------------------------
print("\nSimulating real-time sequence of 20 readings...\n")

# Initialize previous values
prev_Tbreaker = df["Tbreaker"].iloc[0]
TimeAboveRated = 0
TimeTempRising = 0
I_rated = 20
delta_t = 1  # seconds

for i in range(20):
    # pick synthetic reading
    Itotal = df["Itotal"].iloc[i]
    Tbreaker = df["Tbreaker"].iloc[i]

    # compute slope
    ThermalSlope = (Tbreaker - prev_Tbreaker) / delta_t

    # update time features
    if Itotal > I_rated:
        TimeAboveRated += delta_t
    else:
        TimeAboveRated = 0

    if ThermalSlope > 0:
        TimeTempRising += delta_t
    else:
        TimeTempRising = 0

    # predict state
    X_input = pd.DataFrame([{
        "Itotal": Itotal,
        "Tbreaker": Tbreaker,
        "ThermalSlope": ThermalSlope,
        "TimeAboveRated": TimeAboveRated,
        "TimeTempRising": TimeTempRising
    }])
    state = rf_model.predict(X_input)[0]

    print(f"Reading {i+1:02d}: Itotal={Itotal:.1f}, Tbreaker={Tbreaker:.1f}, "
          f"Slope={ThermalSlope:.2f}, TimeAboveRated={TimeAboveRated}, "
          f"TimeTempRising={TimeTempRising} => Predicted State: {state}")

    prev_Tbreaker = Tbreaker
