#!/usr/bin/env python3
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = "data/bikeshare.jsonl"
DOCS_DIR = "docs"

os.makedirs(DOCS_DIR, exist_ok=True)

# ---- Daten laden ----
if not os.path.exists(DATA_FILE):
    print("Keine Daten gefunden. Bitte zuerst 'python fetch_data.py' laufen lassen.")
    raise SystemExit(1)

df = pd.read_json(DATA_FILE, lines=True)
if df.empty:
    print("Datei ist leer. Erst Daten sammeln.")
    raise SystemExit(1)

# Zeitspalte und Typen säubern
df["ts"] = pd.to_datetime(df["fetched_at_utc"], utc=True, errors="coerce")
df["bikes_available"] = pd.to_numeric(df["bikes_available"], errors="coerce").fillna(0)
df["name"] = df.get("name")
df["station_id"] = df["station_id"].astype(str)  # wichtig für Labels

# ---- Plot 1: Gesamt verfügbare Räder (letzte 7 Tage) ----
cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=7)
df7 = df[df["ts"] >= cutoff].copy()

# Summe je Snapshot
total_per_ts = df7.groupby("ts", as_index=False)["bikes_available"].sum()
total_per_ts.rename(columns={"bikes_available": "total_bikes"}, inplace=True)

plt.figure()
plt.plot(total_per_ts["ts"], total_per_ts["total_bikes"])
plt.title("Gesamt verfügbare Räder (letzte 7 Tage)")
plt.xlabel("Zeit (UTC)")
plt.ylabel("Anzahl Räder")
plt.tight_layout()
out_total = os.path.join(DOCS_DIR, "total_bikes.png")
plt.savefig(out_total, dpi=150)
plt.close()
print("geschrieben:", out_total)

# ---- Plot 2: Tagesrhythmus (Ø je Stunde, UTC) ----
# erst Summe je Snapshot, dann Mittelwert je Stunde
total_per_ts["hour"] = total_per_ts["ts"].dt.hour
hourly_avg = total_per_ts.groupby("hour", as_index=False)["total_bikes"].mean()

plt.figure()
plt.plot(hourly_avg["hour"], hourly_avg["total_bikes"])
plt.title("Durchschnittlich verfügbare Räder je Stunde (UTC)")
plt.xlabel("Stunde")
plt.ylabel("Ø Räder")
plt.xticks(range(0, 24))
plt.tight_layout()
out_hour = os.path.join(DOCS_DIR, "hourly_pattern.png")
plt.savefig(out_hour, dpi=150)
plt.close()
print("geschrieben:", out_hour)

# ---- Plot 3: Top-15 Stationen im jüngsten Snapshot ----
latest_ts = df["ts"].max()
snap = df[df["ts"] == latest_ts].copy()

# Label: bevorzugt Name, sonst station_id (immer als String!)
snap["label"] = snap["name"].fillna("").astype(str)
snap.loc[snap["label"].eq(""), "label"] = snap["station_id"]

# Top 15 nach bikes_available
snap = snap.sort_values("bikes_available", ascending=False).head(15)

plt.figure(figsize=(10, 6))
plt.bar(snap["label"], snap["bikes_available"])
plt.title(f"Top-15 Stationen – Räder @ {latest_ts.strftime('%Y-%m-%d %H:%M UTC')}")
plt.xlabel("Station")
plt.ylabel("Räder verfügbar")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
out_top = os.path.join(DOCS_DIR, "top_stations_current.png")
plt.savefig(out_top, dpi=150)
plt.close()
print("geschrieben:", out_top)

# ---- Mini-Website ----
index_html = f"""<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>WienMobil Bikes – Ergebnisse</title>
    <style>
      body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; }}
      img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px; margin: 1rem 0; }}
      .note {{ color: #555; }}
      code {{ background: #f6f8fa; padding: 0.1rem 0.3rem; border-radius: 4px; }}
    </style>
  </head>
  <body>
    <h1>WienMobil Bikes – einfache Visualisierung</h1>
    <p class="note">
      Datenquelle: <code>data/bikeshare.jsonl</code> (eine Datei, Append-Only).
    </p>

    <h2>Gesamt verfügbare Räder (letzte 7 Tage)</h2>
    <img src="total_bikes.png" alt="Zeitreihe: Gesamt verfügbare Räder">

    <h2>Tagesrhythmus (Durchschnitt je Stunde, UTC)</h2>
    <img src="hourly_pattern.png" alt="Durchschnittlich verfügbare Räder je Stunde">

    <h2>Top-15 Stationen im jüngsten Snapshot</h2>
    <img src="top_stations_current.png" alt="Top-Stationen im jüngsten Snapshot">

    <p class="note">Letzter Snapshot: {latest_ts.strftime('%Y-%m-%d %H:%M UTC')}</p>
  </body>
</html>
"""
Path(os.path.join(DOCS_DIR, "index.html")).write_text(index_html, encoding="utf-8")
print("geschrieben:", os.path.join(DOCS_DIR, "index.html"))
