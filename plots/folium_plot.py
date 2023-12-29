import pydeck as pdk

def calculate_color(demand, min_demand, max_demand):
    # Normalize the demand value to a range between 0 and 1
    normalized_demand = (demand - min_demand) / (max_demand - min_demand)

    # Linearly interpolate between green and red
    red = int(255 * normalized_demand)
    green = int(255 * (1 - normalized_demand))

    # Return the color as an array of [red, green, blue, alpha]
    return [red, green, 0, 128]


def pydeck_plot_data(df):
    # Extract latitude, longitude, and demand data from DataFrame
    latitude = df['lat']
    longitude = df['lng']
    demand = df['Demand']

    # Create a pydeck map centered on the average location
    center_lat, center_lon = latitude.mean(), longitude.mean()

    # Get the min and max demand values for color calculation and height normalization
    min_demand, max_demand = df['Demand'].min(), df['Demand'].max()

    # Create data for pydeck Layer
    data = [{"lat": lat, "lon": lon, "elevation": ((demand - min_demand) / (max_demand - min_demand)) * 100000, "color": calculate_color(demand, min_demand, max_demand)}
            for lat, lon, demand in zip(latitude, longitude, demand)]

    # Create the pydeck Layer
    layer = pdk.Layer(
        "ColumnLayer",
        data=data,
        get_position=["lon", "lat"],
        get_elevation="elevation",
        get_fill_color="color",
        radius=1000,  # Radius of column
        elevation_scale=1,
        pickable=True,
        auto_highlight=True,
        get_tooltip=["lat", "lon", "elevation"]  # Add tooltip here
    )

    # Create the pydeck Deck object
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=6,
            pitch=45,
            bearing=0
        ),
        map_style="mapbox://styles/mapbox/light-v10"  # Use a lighter map style
    )

    return deck

    