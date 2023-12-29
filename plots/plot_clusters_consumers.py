import streamlit as st
import folium
from folium import plugins
from folium.features import DivIcon
import math
import numpy as np
import streamlit_folium as st_folium

# List of colours for each cluster in hex format
col_hex = ['#440154', '#4169E1', '#32CD32', '#FF4500', '#9ACD32', '#4682B4', '#8B0000', '#2E8B57', '#FFD700', '#EE82EE',
           '#FF6347', '#6B8E23', '#FFA500', '#ADFF2F', '#FF1493', '#00BFFF', '#20B2AA', '#7CFC00', '#DB7093', '#00FA9A']


def number_DivIcon(color, number):
    """
    workaround as suggested by 
    1. [Github User](https://github.com/python-visualization/folium/issues/1466#issuecomment-818582994)
    2. [Stackoverflow](https://stackoverflow.com/questions/46400769/numbers-in-map-marker-in-folium)

    """

    # Style and create the icon
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


def visualize_clusters_on_map(df, cluster_labels, cluster_centers):
    """
    Visualize the clusters on a folium map.

    Parameters:
        df (DataFrame): DataFrame with lat, lng, and Demand columns.
        cluster_labels (Series): Cluster labels for each point in df.
        cluster_centers (np.ndarray): Centers of the clusters.

    """

    # CSS to make the map responsive
    make_map_responsive = """
     <style>
     [title~="st.iframe"] { width: 100%}
     </style>
    """
    st.markdown(make_map_responsive, unsafe_allow_html=True)

    # Convert DataFrame columns to numpy arrays
    coordinates = df[['lat', 'lng']].to_numpy()
    demand = df['Demand'].to_numpy()
    cluster_labels = cluster_labels.to_numpy().ravel()

    # Create a map centered at the mean of the cluster center points
    center_lat, center_lng = np.mean(cluster_centers[:, :2], axis=0)
    m = folium.Map(location=[center_lat, center_lng], zoom_start=4)

    # Create a feature group for each cluster
    cluster_fg = [folium.FeatureGroup(
        name=f'Cluster {i+1}') for i in range(len(cluster_centers))]

    # Compute the average distance for each cluster
    for i in range(len(cluster_centers)):
        mask = cluster_labels == i
        cluster_points = coordinates[mask]

    # Compute demand statistics per cluster
    cluster_avg_demand = [np.mean(demand[cluster_labels == i])
                          for i in range(len(cluster_centers))]
    cluster_std_demand = [np.std(demand[cluster_labels == i])
                          for i in range(len(cluster_centers))]
    cluster_total_demand = [np.sum(demand[cluster_labels == i])
                            for i in range(len(cluster_centers))]
    cluster_num_customers = [np.sum(cluster_labels == i)
                             for i in range(len(cluster_centers))]

    # Add coordinates points to the respective cluster feature group
    for i, label in enumerate(cluster_labels):
        # Select color based on cluster label
        color = col_hex[label % len(col_hex)]
        folium.CircleMarker(location=list(
            coordinates[i]), radius=5, fill=True, color=color, fill_opacity=0.6).add_to(cluster_fg[label])

    # Add the cluster feature groups to the map
    for fg in cluster_fg:
        fg.add_to(m)

    # Compute average distances from points to cluster centers
    avg_distances = [np.mean(np.linalg.norm(coordinates[cluster_labels == i] -
                             cluster_centers[i, :2], axis=1)) for i in range(len(cluster_centers))]

    # Add cluster centers as markers with demand statistics label
    for i, center in enumerate(cluster_centers):
        color = col_hex[i % len(col_hex)]  # Use label to select color
        avg_distance = avg_distances[i]
        avg_dem = cluster_avg_demand[i]
        std_dem = cluster_std_demand[i]
        total_dem = cluster_total_demand[i]
        num_customers = cluster_num_customers[i]

        # Adding cluster center markers and demand statistics tooltip
        folium.Marker(location=list(center[:2]),
                      icon=folium.Icon(color='white', icon_color='white')).add_to(m)
        folium.Marker(location=list(center[:2]),
                      icon=number_DivIcon(color, i+1),
                      tooltip=f'Avg Distance: {avg_distance:.2f} km<br>'
                      f'Avg Demand: {avg_dem:.2f}<br>'
                      f'Std Dev Demand: {std_dem:.2f}<br>'
                      f'Total Demand: {total_dem:.2f}<br>'
                      f'Number of Customers: {num_customers}').add_to(m)

    # Add a layer control to the map
    folium.LayerControl().add_to(m)

    # Show map in Streamlit
    st_folium.folium_static(m)
