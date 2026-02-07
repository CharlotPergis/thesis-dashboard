# --------------------------
# train_random_forest.py
# --------------------------
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# 1️⃣ Load the dataset
df = pd.read_csv("synthetic_data_time_based.csv")

# 2️⃣ Features and target
# Using time-based features + raw measurements
X = df[["Itotal", "Tbreaker", "ThermalSlope", "TimeAboveRated", "TimeTempRising"]]
y = df["State"]

# 3️⃣ Split into train/test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4️⃣ Train Random Forest
rf_model = RandomForestClassifier(
    n_estimators=200,       # number of trees
    max_depth=10,           # limit depth to prevent overfitting
    random_state=42
)
rf_model.fit(X_train, y_train)

# 5️⃣ Evaluate model
y_pred = rf_model.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 6️⃣ Save the model for Flask use
joblib.dump(rf_model, "rf_model_time_based.joblib")
print("Random Forest model saved as rf_model_time_based.joblib")
