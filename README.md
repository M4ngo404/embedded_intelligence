# embedded_intelligence
Project for MKI
# Datenbank
Die Sensordaten aller Testläufe sind in einer SQLite-Datenbank (data/emi_nav.db) gespeichert.
Details zum Schema und Aufbau: DATABASE.md

Verbindung im Notebook:

python
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/emi_nav.db")

# Beispiel: alle BLE-Messungen von Run 1
df = pd.read_sql("SELECT * FROM ble_rssi WHERE run_id = 'R1'", conn)

Beim ersten Start muss die Datenbank einmalig befüllt werden.
Dazu datein in db_scripts ausführen