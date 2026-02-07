# --------------------------
# manual_sensor_predict.py
# --------------------------
import pandas as pd
import joblib

# Load the trained Random Forest model
rf_model = joblib.load("../model/rf_model_time_based.joblib")  # adjust path if needed

# Initialize variables for slope and time calculations
prev_Tbreaker = None
TimeAboveRated = 0
TimeTempRising = 0
I_rated = 20  # nominal current for threshold
delta_t = 1   # time step in seconds

print("=== Manual Sensor-Based Predictor ===")
print("Enter sensor readings (Itotal and Tbreaker). Type 'exit' to quit.\n")

while True:
    # Manual input
    inp = input("Enter Itotal (A) and Tbreaker (°C) separated by a space: ")
    if inp.lower() == "exit":
        print("Exiting predictor.")
        break
    try:
        Itotal_str, Tbreaker_str = inp.split()
        Itotal = float(Itotal_str)
        Tbreaker = float(Tbreaker_str)
    except:
        print("Invalid input. Enter two numbers separated by a space.\n")
        continue

    # --- Compute derived features ---
    # Thermal slope
    if prev_Tbreaker is None:
        ThermalSlope = 0
    else:
        ThermalSlope = (Tbreaker - prev_Tbreaker) / delta_t

    # Time above rated current
    if Itotal > I_rated:
        TimeAboveRated += delta_t
    else:
        TimeAboveRated = 0

    # Time temperature rising
    if ThermalSlope > 0:
        TimeTempRising += delta_t
    else:
        TimeTempRising = 0

    # Prepare features for model
    X_input = pd.DataFrame([{
        "Itotal": Itotal,
        "Tbreaker": Tbreaker,
        "ThermalSlope": ThermalSlope,
        "TimeAboveRated": TimeAboveRated,
        "TimeTempRising": TimeTempRising
    }])

    # Predict system state
    predicted_state = rf_model.predict(X_input)[0]
    print(f">>> Predicted System State: {predicted_state}\n")

    # Update previous temperature
    prev_Tbreaker = Tbreaker
