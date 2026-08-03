"""
FireWatch — interactive wildfire / air-quality dashboard for Los Angeles County.

Renders a geospatial PM2.5 heatmap over an interactive map, filterable by date.
Data is a weekly merge of EPA air quality, NASA FIRMS/MODIS fire detections,
and Open-Meteo wind history (see data/README.md and notebooks/).
"""

import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="FireWatch", layout="wide")

DATA_PATH = "data/master_merged_data.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load the merged dataset and normalize the columns the app relies on."""
    df = pd.read_csv(path, engine="python")

    # The EPA export uses long column names; rename to short, map-friendly ones.
    rename_map = {
        "latitude": "lat",
        "longitude": "lng",
        "Site Latitude": "lat",
        "Site Longitude": "lng",
        "Daily Mean PM2.5 Concentration": "pm25",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "lat", "lng", "pm25"])
    return df


def main() -> None:
    st.title("FireWatch — Air Quality & Wildfire Spatial Analysis")
    st.caption(
        "Interactive PM2.5 heatmap for Los Angeles County, built from EPA, "
        "NASA FIRMS/MODIS, and Open-Meteo data."
    )

    try:
        df = load_data(DATA_PATH)
    except FileNotFoundError:
        st.error(
            f"Could not find `{DATA_PATH}`. Add the merged dataset there — "
            "see data/README.md for how to generate it."
        )
        st.stop()

    # ---- Sidebar controls ----
    st.sidebar.subheader("Filter")

    min_date = df["date"].min().to_pydatetime()
    max_date = df["date"].max().to_pydatetime()
    selected_date = st.sidebar.slider(
        "Date", min_value=min_date, max_value=max_date, value=min_date
    )

    with st.sidebar.expander("About"):
        st.markdown(
            "**FireWatch** visualizes historical air quality and wildfire "
            "activity across Los Angeles County, and pairs the dashboard with "
            "a SARIMAX model that forecasts fire intensity (radiative power) "
            "from PM2.5 and wind. Built to help agencies see where to focus "
            "monitoring and resources.\n\n"
            "**Data:** EPA daily PM2.5, NASA FIRMS (MODIS) fire detections, "
            "and Open-Meteo historical wind."
        )

    # ---- Filter to the selected day ----
    day = df[df["date"] == pd.Timestamp(selected_date)]
    if day.empty:
        st.warning("No readings for that date — try another.")
        st.stop()

    # ---- Heatmap ----
    layer = pdk.Layer(
        "HeatmapLayer",
        day,
        get_position=["lng", "lat"],
        get_weight="pm25",
        radius_pixels=50,
    )
    view_state = pdk.ViewState(
        latitude=day["lat"].mean(),
        longitude=day["lng"].mean(),
        zoom=8,
        pitch=45,
    )
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "PM2.5: {pm25}"},
        )
    )
    st.caption(
        f"{selected_date:%B %d, %Y} — {len(day)} site readings"
    )


if __name__ == "__main__":
    main()
