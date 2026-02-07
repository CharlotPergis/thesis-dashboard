import numpy as np
import pandas as pd

# --------------------------
# CONFIGURATION
# --------------------------
np.random.seed(42)
num_samples = 1000         # total time steps
In = 20                     # nominal current
Tambient = 40               # ambient temperature
delta_t = 1                 # seconds between measurements

# --------------------------
# ARRAYS TO STORE DATA
# --------------------------
currents = np.zeros(num_samples)
temperatures = np.zeros(num_samples)
thermal_slopes = np.zeros(num_samples)
time_above_I = np.zeros(num_samples)
time_temp_rising = np.zeros(num_samples)
states = []

# --------------------------
# INITIAL VALUES
# --------------------------
currents[0] = np.random.uniform(0, 20)
temperatures[0] = Tambient + np.random.uniform(0, 30)
thermal_slopes[0] = 0
time_above_I[0] = 0
time_temp_rising[0] = 0

# --------------------------
# GENERATE SEQUENTIAL DATA
# --------------------------
for i in range(1, num_samples):
    # 1️⃣ Simulate main current
    if np.random.rand() < 0.7:
        # mostly normal load
        currents[i] = np.random.uniform(0, 20)
    else:
        # occasional overload
        currents[i] = np.random.uniform(21, 30)

    # 2️⃣ Compute thermal slope based on previous temperature
    # small random fluctuation + effect of current
    slope = max(0, 0.05 * (currents[i] - In) + np.random.uniform(0, 1))
    thermal_slopes[i] = slope

    # 3️⃣ Update temperature
    temperatures[i] = temperatures[i-1] + slope * delta_t

    # 4️⃣ Update time-based features
    time_above_I[i] = time_above_I[i-1] + delta_t if currents[i] > In else 0
    time_temp_rising[i] = time_temp_rising[i-1] + delta_t if slope > 0 else 0

    # 5️⃣ Assign system state based on thresholds & persistence
    if currents[i] <= In and slope < 0.5:
        state = "Normal"
    elif currents[i] <= In and slope >= 0.5:
        state = "Overheating (Loose Terminal)"
    elif In < currents[i] < 26 and slope > 0.5:
        if currents[i] < 23:
            state = "Potential Overload"
        else:
            state = "High Risk Potential Overload"
    elif currents[i] >= 26:
        state = "Overload"
    else:
        state = "Normal"

    states.append(state)

# Add first state manually
states = ["Normal"] + states

# --------------------------
# CREATE DATAFRAME & SAVE
# --------------------------
df = pd.DataFrame({
    "Itotal": currents,
    "Tbreaker": temperatures,
    "ThermalSlope": thermal_slopes,
    "TimeAboveRated": time_above_I,
    "TimeTempRising": time_temp_rising,
    "State": states
})

df.to_csv("synthetic_data_time_based.csv", index=False)
print("Time-based synthetic dataset generated: synthetic_data_time_based.csv")
