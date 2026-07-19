import sqlite3, pandas as pd
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

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

GROUNDTRUTH_INPUT = [
    # run_id, tuer_id, timestamp_ms
    ("R1", "H01", "2026-06-16 14:16:04"),
    ("R1", "H02", "2026-06-16 14:16:11"),
    ("R1", "T022", "2026-06-16 14:16:32"),
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

SCALE = 0.2  # Meter pro Pixel

# ---------------------------------------------------------------
# Tür-Positionen (Pixel → Meter)
# ---------------------------------------------------------------
DOOR_DATA = [
    ("H01",   600, 60, 0),
    ("H02",   587, 31, 0),
    ("H03",   396, 30, 0),
    ("T016",  626, 17, 0),
    ("T021",  508, 22, 0),
    ("T022",  475, 22, 0),
    ("H11",   600, 60, 1),
    ("H12",   587, 31, 1),
    ("H13",   396, 30, 1),
    ("T109c", 480, 40, 1),
    ("T125",  325, 33, 1),
]

cur.executescript("""
    CREATE TABLE IF NOT EXISTS door_positions (
        tuer_id  TEXT PRIMARY KEY,
        x_m      REAL NOT NULL,
        y_m      REAL NOT NULL,
        floor    INTEGER NOT NULL
    );
""")

cur.executemany("""
    INSERT OR REPLACE INTO door_positions (tuer_id, x_m, y_m, floor)
    VALUES (?, ?, ?, ?)
""", [(tid, x * SCALE, y * SCALE, f) for tid, x, y, f in DOOR_DATA])

# ---------------------------------------------------------------
# Beacon-Positionen (Pixel → Meter)
# ---------------------------------------------------------------
BEACON_DATA = [
    ("arrive_emi1", 370.0, 47.0, 1),
    ("arrive_emi2", 445.0, 40.0, 1),
    ("arrive_emi3", 588.0, 20.0, 1),
    ("arrive_emi4", 590.0, 20.0, 0),
    ("arrive_emi8", 370.0, 50.0, 0),
    ("arrive_emi10", 510.0, 40.0, 0),
]

cur.executescript("""
    CREATE TABLE IF NOT EXISTS beacon_positions (
        beacon_name  TEXT PRIMARY KEY,
        x_m          REAL NOT NULL,
        y_m          REAL NOT NULL,
        floor        INTEGER NOT NULL
    );
""")

cur.executemany("""
    INSERT OR REPLACE INTO beacon_positions (beacon_name, x_m, y_m, floor)
    VALUES (?, ?, ?, ?)
""", [(name, x * SCALE, y * SCALE, f) for name, x, y, f in BEACON_DATA])

conn.commit()
print("Door & Beacon Positionen eingetragen ✓")

conn.close()