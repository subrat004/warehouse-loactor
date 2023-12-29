import numpy as np
import pandas as pd
import streamlit as st
import math


def capcacity_display(df, centroid_centers):
    sumd = df['Demand'].sum()
    K = len(centroid_centers)
    cap = sumd/K
    cap += 0.1*cap
    cluster_centers = df.groupby('Cluster').agg({'lat': 'mean', 'lng': 'mean'})
    # centroid_centers
    # Calculate the Total Demand per Cluster in Units for each cluster
    demand_sum = df.groupby('Cluster')['Demand'].sum()

    # Calculate the number of points in each cluster
    point_count = df.groupby('Cluster').size()

    # Calculate the Euclidean distance between each point and its cluster centroid
    distances = np.sqrt(
        ((df[['lat', 'lng']] - np.array(centroid_centers)[df['Cluster'], :2])**2).sum(axis=1))

    # Calculate the total distance of points from their respective cluster centroids
    total_distance = distances.groupby(df['Cluster']).sum()

    # Calculate the average distance for each cluster
    avg_distance = distances.groupby(df['Cluster']).mean()

    # Create a DataFrame with the cluster information
    cluster_table = pd.DataFrame({
        'Cluster': demand_sum.index+1,
        'Customers per cluster': point_count.values,
        'Total Demand per Cluster in Units': demand_sum.values,
        'Total Distance': total_distance.values,
        'Average Distance': avg_distance.values,
        'Capacities in Units': cap
    })
    # reset the index to start from 1
    cluster_table.index = np.arange(1, len(cluster_table) + 1)

    return cluster_table, cap
