import sqlite3
import pandas as pd

conn = sqlite3.connect("data/emi_nav.db")
cur = conn.cursor()

cur.executescript("""
-- Metadaten pro Run
CREATE TABLE IF NOT EXISTS runs (
    run_id   TEXT PRIMARY KEY,
    filename TEXT,
    date     TEXT,
    notes    TEXT
);

-- IMU-Daten (accel, gyro, mag, imu_processed)
CREATE TABLE IF NOT EXISTS imu (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       TEXT,
    timestamp_ms INTEGER,
    sensor       TEXT,   -- accel, gyro, mag, imu_processed
    x            REAL,
    y            REAL,
    z            REAL,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

-- BLE RSSI Messungen
CREATE TABLE IF NOT EXISTS ble_rssi (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       TEXT,
    timestamp_ms INTEGER,
    beacon_name  TEXT,
    address      TEXT,
    rssi         REAL,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);
""")
conn.commit()
print("DB + Schema erstellt ✓")