#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime

# URL Wienmobil-API
STATUS_URL = "https://api.wstw.at/gateway/WL_WIENMOBIL_API/1/station_status.json"
# Output file
OUT_FILE = "data/bikeshare.jsonl"

# Creates directory if not already there
os.makedirs("data", exist_ok=True)

# fetch data and write to variable r
r = requests.get(STATUS_URL)

# save data in json form
data = r.json()

# create stations list from data
stations = data["data"]["stations"]

# fetch time in fetched_at
fetched_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

# 
with open(OUT_FILE, "a", encoding="utf-8") as f:
    for st in stations:
        row = {
            "fetched_at_utc": fetched_at,
            "station_id": st["station_id"],
            "bikes_available": st["num_bikes_available"],
            "docks_available": st["num_docks_available"]
        }
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"OK: {len(stations)} Einträge in {OUT_FILE} gespeichert.")