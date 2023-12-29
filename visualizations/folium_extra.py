import folium
import branca.colormap as cm
from branca.element import Template, MacroElement
import streamlit as st
from folium.features import DivIcon
import streamlit_folium as st_folium
from sklearn.preprocessing import MinMaxScaler

col_hex = ['#440154', '#4169E1', '#32CD32', '#FF4500', '#9ACD32', '#4682B4', '#8B0000', '#2E8B57', '#FFD700', '#EE82EE',
           '#FF6347', '#6B8E23', '#FFA500', '#ADFF2F', '#FF1493', '#00BFFF', '#20B2AA', '#7CFC00', '#DB7093', '#00FA9A']

# Function to create a 'numbered' icon


def number_DivIcon(color, number):
    """ Create a 'numbered' icon

    """
    icon = DivIcon(
        icon_size=(150, 36),
        icon_anchor=(9, 37),
        html="""
                <div style="font-size: 12pt; text-align: center;">
                    <!-- The circle that will wrap the number -->
                    <div style="border: 2px solid {color}; border-radius: 50%; width: 24px; height: 24px; line-height: 24px;">
                        <!-- The number -->
                        <strong style="color: {color};">
                            {number:02d}
                        </strong>
                    </div>
                </div>""".format(color=color, number=number)
    )
    return icon


def folium_extra(df, cluster_labels, centroids):
    coordinates = df[['lat', 'lng']]
    df['Cluster'] = cluster_labels
    lat_mean = df['lat'].mean()
    lng_mean = df['lng'].mean()
    map = folium.Map(location=[lat_mean, lng_mean], zoom_start=6)

    cluster_demands = df.groupby('Cluster')['Demand'].sum().reset_index()
    scaler = MinMaxScaler(feature_range=(1, 10))
    scaled_demand = scaler.fit_transform(cluster_demands[['Demand']])
    scaled_demand = scaled_demand.flatten().tolist()
    cluster_demands['Scaled_Demand'] = scaled_demand

    for idx, centroid in enumerate(centroids):
        lat, long = centroid[:2]
        demand = cluster_demands.loc[cluster_demands['Cluster']
                                     == idx, 'Demand'].values[0]
        scaled_demand_value = cluster_demands.loc[cluster_demands['Cluster']
                                                  == idx, 'Scaled_Demand'].values[0]

        folium.Marker(location=[lat, long],
                      icon=folium.Icon(color='white', icon_color='white')).add_to(map)
        folium.Marker(location=[lat, long],
                      icon=number_DivIcon(
                          col_hex[(idx + 1) % len(col_hex)], idx + 1),
                      popup=f'Cluster Centroid {idx+1}, Demand: {demand}'
                      ).add_to(map)
        folium.Circle(
            location=[lat, long],
            radius=scaled_demand_value*5000,
            color=col_hex[(idx + 1) % len(col_hex)],
            fill=True,
            fill_color=col_hex[(idx + 1) % len(col_hex)],
            fill_opacity=0.3,
        ).add_to(map)

    st_folium.folium_static(map, width=1300, height=500)
