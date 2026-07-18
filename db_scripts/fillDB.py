import sqlite3, pandas as pd
from pathlib import Path

conn = sqlite3.connect("../data/emi_nav.db")
cur = conn.cursor()

runs_meta = [
    ("TR1", "T3_pickup_export_20251128_062231.csv", "2026-07-17", ""),
    ("TR2", "T2_pickup_export_20251128_062333.csv", "2026-07-17", ""),
    ("TR3", "T1_pickup_export_20251206_230839.csv", "2026-06-16", ""),
]
cur.executemany("INSERT OR IGNORE INTO runs VALUES (?,?,?,?)", runs_meta)
conn.commit()
print("Runs eingetragen ✓")

files = {
    "TR1": "../data/raw_files/T3_pickup_export_20251128_062231.csv",
    "TR2": "../data/raw_files/T2_pickup_export_20251128_062333.csv",
    "RR3": "../data/raw_files/T1_pickup_export_20251206_230839.csv",
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