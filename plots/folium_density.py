import pydeck as pdk
import numpy as np
import pandas as pd


def pydeck_density_data(df):
    # Example latitude and longitude data from DataFrame
    latitude = df['lat']
    longitude = df['lng']
    df['Demand'] = pd.to_numeric(df['Demand'], errors='coerce')

    # Create a pydeck map centered on the average location
    center_lat, center_lon = latitude.mean(), longitude.mean()

    # Normalize the demand values between 0 and 1
    normalized_demand = (df['Demand'] - df['Demand'].min()) / \
        (df['Demand'].max() - df['Demand'].min())
    df['NormalizedDemand'] = normalized_demand

    # Create data for pydeck Layer
    data = [{"lat": lat, "lon": lon, "weight": weight}
            for lat, lon, weight in zip(latitude, longitude, normalized_demand)]

    # Create the pydeck Layer
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=data,
        get_position=["lon", "lat"],
        get_weight="weight",
        opacity=0.5,
    )

    scatterplot_layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position=["lon", "lat"],
        get_fill_color=[0, 0, 255],  # Blue points
        get_radius=1000,  # Radius is in meters
    )

    # Create the pydeck Deck object
    deck = pdk.Deck(
        layers=[heatmap_layer, scatterplot_layer],
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=6,
            pitch=0,
            bearing=0
        ),
        map_style="mapbox://styles/mapbox/light-v10"  # Use a lighter map style
    )

    # Return the deck object
    return deck
