#!/usr/bin/env python3
import os
import json
from datetime import datetime
import requests

# Wo holen wir die Daten?
STATUS_URL = "https://api.wstw.at/gateway/WL_WIENMOBIL_API/1/station_status.json"

# Eine einzige Datei, an die wir immer anhängen
OUT_FILE = "data/bikeshare.jsonl"

# Ordner sicherstellen
os.makedirs("data", exist_ok=True)

# 1) Daten holen
r = requests.get(STATUS_URL, timeout=30)
r.raise_for_status()              # wenn Fehler, hier abbrechen
data = r.json()

# 2) Stationsliste rausziehen (probieren zwei Varianten)
stations = None
if isinstance(data, dict):
    if "data" in data and isinstance(data["data"], dict):
        stations = data["data"].get("stations")
    if stations is None and "stations" in data:
        stations = data["stations"]

if not stations:
    print("Keine Stationsdaten gefunden :(")
    raise SystemExit(1)

# 3) Zeitstempel 
fetched_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

# 4) Für jede Station eine Zeile JSON anhängen
with open(OUT_FILE, "a", encoding="utf-8") as f:
    for st in stations:
        # minimal: nur das Wichtigste, ohne Zusatzlogik
        row = {
            "fetched_at_utc": fetched_at,
            "station_id": st.get("station_id"),
            "name": st.get("name"),
            "lat": st.get("lat"),
            "lon": st.get("lon"),
            "capacity": st.get("capacity"),
            "bikes_available": st.get("num_bikes_available"),
            "docks_available": st.get("num_docks_available"),
            "is_installed": st.get("is_installed"),
            "is_renting": st.get("is_renting"),
            "last_reported": st.get("last_reported"),
        }
        # nur schreiben, wenn station_id da ist
        if row["station_id"]:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"OK: {len(stations)} Stationen nach {OUT_FILE} geschrieben (append).")
