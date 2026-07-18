import sqlite3, pandas as pd
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

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

GROUNDTRUTH_INPUT = [
    # run_id, tuer_id, timestamp_ms
    ("R1", "H01", "2026-06-16 14:16:04"),
    ("R1", "H02", "2026-06-16 14:16:11"),
    ("R1", "T022", "2026-06-16 14:16:11"),
    ("R1", "H03", "2026-06-16 14:16:46"),
    #R2
    ("R2", "H03", "2026-06-16 15:02:18"),
    ("R2", "H13", "2026-06-16 15:02:52"),
    ("R2", "H12", "2026-06-16 15:03:18"),
    ("R2", "H11", "2026-06-16 15:03:33"),
    ("R2", "H01", "2026-06-16 15:03:56"),
    ("R2", "H02", "2026-06-16 15:04:03"),
    #R3
    ("R3", "T125", "2026-06-16 15:08:05"),
    ("R3", "H13", "2026-06-16 15:08:16"),
    ("R3", "T109c", "2026-06-16 15:08:40"),
    ("R3", "H12", "2026-06-16 15:09:10"),
    ("R3", "H11", "2026-06-16 15:09:28"),
    ("R3", "H01", "2026-06-16 15:09:49"),
    ("R3", "T016", "2026-06-16 15:10:07"),
    ("R3", "H02", "2026-06-16 15:10:18"),
    ("R3", "T021", "2026-06-16 15:10:38"),
    ("R3", "H03", "2026-06-16 15:11:09"),
    #R4
]

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

def datetime_to_timestamp_ms(datetime_str):
    """
    Wandelt 'YYYY-MM-DD HH:MM:SS' in Unixzeit in Millisekunden um.

    Beispiel:
    '2026-06-16 14:19:12' -> timestamp_ms
    """
    local_dt = datetime.strptime(
        datetime_str,
        "%Y-%m-%d %H:%M:%S",
    ).replace(tzinfo=ZoneInfo("Europe/Berlin"))

    return int(local_dt.timestamp() * 1000)

GROUNDTRUTH_DATA = [
    (
        run_id,
        tuer_id,
        datetime_to_timestamp_ms(datetime_str),
    )
    for run_id, tuer_id, datetime_str in GROUNDTRUTH_INPUT
]

# Ground Truth in Datenbank schreiben
cur.executemany("""
    INSERT OR IGNORE INTO groundtruth (run_id, tuer_id, timestamp_ms)
    VALUES (?, ?, ?)
""", GROUNDTRUTH_DATA)

conn.commit()

print(f"{len(GROUNDTRUTH_DATA)} Ground-Truth-Punkte verarbeitet ✓")

conn.close()