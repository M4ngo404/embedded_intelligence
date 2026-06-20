# Database — emi_nav.db

SQLite-Datenbank mit allen Sensordaten aus den Testläufen im EMI-Gebäude.

---

## Tabellen

### `runs`
Metadaten pro Messlauf.

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `run_id` | TEXT (PK) | z.B. `R1`, `R2`, `R3` |
| `filename` | TEXT | Originaler CSV-Dateiname |
| `date` | TEXT | Aufnahmedatum (YYYY-MM-DD) |
| `notes` | TEXT | Optionale Anmerkungen |

---

### `imu`
IMU-Sensordaten (Accelerometer, Gyroskop, Magnetometer, gefilterte IMU).

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | INTEGER (PK) | Auto-ID |
| `run_id` | TEXT (FK) | Verweis auf `runs` |
| `timestamp_ms` | INTEGER | Unix-Zeit in ms |
| `sensor` | TEXT | `accel` / `gyro` / `mag` / `imu_processed` |
| `x` | REAL | X-Achse |
| `y` | REAL | Y-Achse |
| `z` | REAL | Z-Achse |

**Sensortypen:**
- `accel` — Beschleunigung in m/s² → Step Detection
- `gyro` — Winkelgeschwindigkeit in rad/s → Richtungsänderungen
- `mag` — Magnetfeld in µT → Kompassorientierung
- `imu_processed` — gefilterte Fusion der Android-App

---

### `ble_rssi`
BLE-Signalstärkemessungen der Beacons.

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | INTEGER (PK) | Auto-ID |
| `run_id` | TEXT (FK) | Verweis auf `runs` |
| `timestamp_ms` | INTEGER | Unix-Zeit in ms |
| `beacon_name` | TEXT | z.B. `arrive_emi3` |
| `address` | TEXT | MAC-Adresse des Beacons |
| `rssi` | REAL | Signalstärke in dBm |

---

## Beziehungen

```
runs
 ├──► imu       (Bewegungsdaten)
 └──► ble_rssi  (Positionsdaten)
```

Verknüpfung über `run_id` + Synchronisation über `timestamp_ms`.

---

## Importlogik

Quelle: CSV-Exporte der Android-App (`source`-Spalte entscheidet den Ziel-Table).

| CSV `source` | → Tabelle | Bemerkung |
|---|---|---|
| `imu` | `imu` | Alle Sensordaten |
| `ble_rssi` | `ble_rssi` | Gefilterte BLE-Messungen |
| `beacon` | *(ignoriert)* | Duplikat mit rohem Protokoll-Overhead |

---

## Verfügbare Runs

| Run | Datei | Datum |
|-----|-------|-------|
| R1 | R1_pickup_export_20260616_141816.csv | 2026-06-16 |
| R2 | R2_pickup_export_20260616_150505.csv | 2026-06-16 |
| R3 | R3_pickup_export_20260616_151247.csv | 2026-06-16 |
