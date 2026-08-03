# FireWatch

An interactive wildfire and air-quality dashboard for **Los Angeles County**, paired with a time-series model that forecasts fire intensity from air quality and wind.

FireWatch renders a geospatial **PM2.5 heatmap** over an interactive map, filterable by date, and fits a seasonal **SARIMAX** model that projects fire radiative power (FRP) forward using PM2.5 and wind as exogenous inputs — the kind of signal an agency could use to decide where to focus monitoring and resources.

## What it does

- **Interactive map** — a date-filterable PM2.5 heatmap across LA County monitoring sites, built with Streamlit and PyDeck.
- **Fire-intensity forecast** — a `SARIMAX(1,0,0)(1,0,1,4)` model on the weekly series, with model order chosen from ADF (stationarity), ACF, and PACF diagnostics, and PM2.5 + wind as exogenous regressors.
- **Merged data** — combines three public sources into one weekly LA time series:
  - EPA daily PM2.5 air-quality data
  - NASA FIRMS (MODIS) fire detections
  - Open-Meteo historical wind (speed + dominant direction)

## Tech stack

Python · pandas · statsmodels · Streamlit · PyDeck · REST APIs (Open-Meteo)

## Running it

```bash
# 1. install deps
pip install -r requirements.txt

# 2. add the data file (see data/README.md)
#    data/master_merged_data.csv

# 3. launch the dashboard
streamlit run app.py        # opens at http://localhost:8501

# or run the forecast on its own
python forecast.py --horizon 16
```

## Repo layout

```
firewatch/
├── app.py              # Streamlit dashboard (PM2.5 heatmap)
├── forecast.py         # SARIMAX fire-intensity forecast
├── requirements.txt
├── data/
│   └── README.md       # data sources + expected schema
└── notebooks/
    └── firewatch.ipynb # original analysis / exploration
```

## Notes

The forward forecast in `forecast.py` currently reuses the most recent weeks of
wind and PM2.5 as future exogenous inputs — a reasonable baseline, but it assumes
recent conditions repeat. Swapping in forecasted exogenous values (or dropping to
a plain SARIMA) is the natural next step for real forward prediction.

Built as a data-science project exploring whether air-quality and weather signals
can anticipate wildfire intensity.
