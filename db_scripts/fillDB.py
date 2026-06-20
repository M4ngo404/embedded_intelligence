import sqlite3, pandas as pd
from pathlib import Path

conn = sqlite3.connect("data/emi_nav.db")
cur = conn.cursor()

runs_meta = [
    ("R1", "R1_pickup_export_20260616_141816.csv", "2026-06-16", ""),
    ("R2", "R2_pickup_export_20260616_150505.csv", "2026-06-16", ""),
    ("R3", "R3_pickup_export_20260616_151247.csv", "2026-06-16", ""),
]
cur.executemany("INSERT OR IGNORE INTO runs VALUES (?,?,?,?)", runs_meta)
conn.commit()
print("Runs eingetragen ✓")

files = {
    "R1": "data/raw_files/R1_pickup_export_20260616_141816.csv",
    "R2": "data/raw_files/R2_pickup_export_20260616_150505.csv",
    "R3": "data/raw_files/R3_pickup_export_20260616_151247.csv",
}

for run_id, path in files.items():
    df = pd.read_csv(path)
    
    # --- IMU ---
    imu_df = df[df["source"] == "imu"][["timestamp_ms", "id", "x", "y", "z"]].copy()
    imu_df.columns = ["timestamp_ms", "sensor", "x", "y", "z"]
    imu_df["run_id"] = run_id
    imu_df.to_sql("imu", conn, if_exists="append", index=False)
    
    # --- BLE RSSI ---
    ble_df = df[df["source"] == "ble_rssi"][["timestamp_ms", "id", "address", "rssi"]].copy()
    ble_df.columns = ["timestamp_ms", "beacon_name", "address", "rssi"]
    ble_df["run_id"] = run_id
    ble_df.to_sql("ble_rssi", conn, if_exists="append", index=False)
    
    print(f"{run_id}: {len(imu_df)} IMU-Zeilen, {len(ble_df)} BLE-Messungen importiert ✓")