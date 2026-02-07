# --------------------------
# app.py
# --------------------------
from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

# --------------------------
# Database setup
# --------------------------
DB_DIR = os.path.join(os.path.dirname(__file__), "logs")
DB_FILE = os.path.join(DB_DIR, "system_log.db")

# Create folder if not exists
os.makedirs(DB_DIR, exist_ok=True)

# Create table if not exists
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
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
    conn.close()

init_db()  # Initialize DB on startup

# --------------------------
# Helper function to get latest readings
# --------------------------
def get_latest_readings(limit=20):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    c = conn.cursor()
    c.execute(f"SELECT * FROM system_log ORDER BY Timestamp DESC LIMIT {limit}")
    rows = c.fetchall()
    conn.close()
    return rows

# --------------------------
# Routes
# --------------------------
@app.route("/")
def dashboard():
    readings = get_latest_readings()
    # Convert to list of dicts for Jinja
    readings = [dict(r) for r in readings]
    return render_template("dashboard.html", readings=readings)

# --------------------------
# Run app
# --------------------------
if __name__ == "__main__":
    # Listen on all interfaces for Render hosting
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
