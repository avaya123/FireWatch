"""
FireWatch — fire-intensity forecasting.

Fits a seasonal SARIMAX model to weekly fire radiative power (FRP) for
Los Angeles, using PM2.5 and wind as exogenous regressors, and produces a
multi-week forward forecast. Model order was selected using ADF (stationarity),
ACF, and PACF diagnostics on the weekly series.

This is a cleaned, script-form version of the analysis in
notebooks/firewatch.ipynb. It expects the merged weekly dataset described in
data/README.md.
"""

import argparse

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def load_weekly(path: str) -> pd.DataFrame:
    """Load the merged dataset and collapse to a weekly time series."""
    df = pd.read_csv(path, engine="python")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")

    weekly = (
        df.set_index("date")
        .resample("W")
        .mean(numeric_only=True)
        .dropna()
    )
    return weekly


def fit_and_forecast(weekly: pd.DataFrame, horizon: int = 16):
    """
    Fit SARIMAX(1,0,0)(1,0,1,4) on fire intensity with PM2.5 + wind exogenous
    regressors, and forecast `horizon` weeks ahead.

    Column names are expected to be: 'fire_frp_sum' (summed fire radiative
    power / intensity), 'pm25', 'wind_speed', 'wind_dir'.
    """
    endog = weekly["fire_frp_sum"]
    exog_cols = [c for c in ["pm25", "wind_speed", "wind_dir"] if c in weekly.columns]
    exog = weekly[exog_cols] if exog_cols else None

    model = SARIMAX(
        endog,
        exog=exog,
        order=(1, 0, 0),
        seasonal_order=(1, 0, 1, 4),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    fit = model.fit(disp=False)

    # For a true forward forecast you need future exogenous values. As a simple
    # baseline this reuses the most recent `horizon` weeks of exog; swap in
    # forecasted inputs (or drop to a plain SARIMA) for production use.
    future_exog = exog.iloc[-horizon:] if exog is not None else None
    forecast = fit.forecast(steps=horizon, exog=future_exog)
    return fit, forecast


def main() -> None:
    parser = argparse.ArgumentParser(description="FireWatch SARIMAX forecast")
    parser.add_argument(
        "--data", default="data/master_merged_data.csv", help="path to merged CSV"
    )
    parser.add_argument("--horizon", type=int, default=16, help="weeks to forecast")
    args = parser.parse_args()

    weekly = load_weekly(args.data)
    if "fire_frp_sum" not in weekly.columns:
        raise SystemExit(
            "Expected a 'fire_frp_sum' (fire radiative power) column. "
            "Check data/README.md for the expected schema."
        )

    fit, forecast = fit_and_forecast(weekly, horizon=args.horizon)
    print(fit.summary())
    print("\nForecast (next {} weeks):".format(args.horizon))
    print(forecast.to_string())


if __name__ == "__main__":
    main()
