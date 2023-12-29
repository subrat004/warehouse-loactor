from sklearn.cluster import KMeans
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler


def get_kmeans(df, num_clusters):
    """
    Executes the K-Means algorithm with weighted or fixed inputs.
    Parameters:
        df (DataFrame): Preprocessed DataFrame.
        num_clusters (int): Number of clusters.
        dataset_type (str): Selected dataset type.
    Returns:
        tuple: Tuple containing the updated DataFrame, cluster labels and centroid centers.
    """

    return K_Means_algo_fixed(df, num_clusters)


def K_Means_algo_fixed(df, num_clusters):
    # Extract latitude and longitude columns
    coordinates = df[['lat', 'lng']]

    # Fit K-means clustering model
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(coordinates)

    # Get the cluster labels
    cluster_labels = kmeans.labels_

    # Get cluster centroids
    centroids = kmeans.cluster_centers_

    # Add the cluster labels to the dataset
    df['Cluster'] = cluster_labels
    return df, cluster_labels, centroids