# --------------------------
# app.py
# --------------------------
from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

# Database path
DB_FILE = os.path.join(os.path.dirname(__file__), "logs", "system_log.db")

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
