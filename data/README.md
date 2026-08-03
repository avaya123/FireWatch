# Data

The dashboard and forecast read a single merged file: `master_merged_data.csv`.
It is **not committed** (it's a build artifact from the three sources below).
Drop your copy in this folder, or regenerate it from the notebook.

## Sources

| Source | What it provides | Where |
|---|---|---|
| EPA Daily Air Quality | Daily mean PM2.5 by monitoring site (LA County) | https://www.epa.gov/outdoor-air-quality-data/download-daily-data |
| NASA FIRMS (MODIS) | Fire detections / fire radiative power (FRP) | https://firms.modaps.eosdis.nasa.gov/download/ |
| Open-Meteo (historical) | Daily max wind speed + dominant wind direction | https://archive-api.open-meteo.com/v1/archive |

## Expected columns

After merging and resampling to a weekly series, the code expects roughly:

| Column | Meaning |
|---|---|
| `date` | week (or day) timestamp |
| `lat`, `lng` | site coordinates (dashboard heatmap) |
| `pm25` | daily/weekly mean PM2.5 concentration |
| `frp` | fire radiative power — the forecast target (`forecast.py`) |
| `wind_speed` | max wind speed (exogenous regressor) |
| `wind_dir` | dominant wind direction (exogenous regressor) |

`app.py` only needs `date`, `lat`, `lng`, `pm25`.
`forecast.py` additionally needs `frp` and, ideally, `wind_speed` / `wind_dir`.

If your column names differ, adjust the `rename_map` in `app.py` and the
column references in `forecast.py`.
