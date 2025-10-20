#!/usr/bin/env python3
# File: Visualization.py
# Basic viz: total bikes across all stations every hour,
# converted to Europe/Vienna time and shown on a 12-hour clock.

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

IN_FILE = "data/bikeshare.jsonl"
OUT_FILE = "data/total_bikes_over_time.png"

# Create a dataframe of from bikeshare.jsonl (from WienMobilFetchProcessStore.py -> bikeshare.jsonl)
df = pd.read_json(IN_FILE, lines=True)

# Parse UTC timestamps
df["fetched_at_utc"] = pd.to_datetime(df["fetched_at_utc"], utc=True)

# Convert to local time (Europe/Vienna)
df["fetched_at_vie"] = df["fetched_at_utc"].dt.tz_convert("Europe/Vienna")

# Sum bikes across all stations per local timestamp
totals = (
    df.groupby("fetched_at_vie")["bikes_available"]
      .sum()
      .sort_index()
)

# Draw diagram
plt.figure()
plt.plot(totals.index, totals.values, marker="o")
plt.title("Total bikes available (all stations)")
plt.xlabel("Time (Europe/Vienna)")
plt.ylabel("Total bikes")

# Hourly ticks, 12-hour labels (e.g., 10 PM). For 24h style, use "%H:%M".
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%I %p"))
plt.gcf().autofmt_xdate()

plt.tight_layout()
os.makedirs("data", exist_ok=True)
plt.savefig(OUT_FILE, dpi=150)
print(f"Saved: {OUT_FILE}")
