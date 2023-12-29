import streamlit as st
from data_exploration import normal
from models import kmeans, pulp_model
from plots import folium_density, folium_plot
from metrics import capacity
from plots import plot_clusters_consumers
from visualizations import pie, bar, folium_extra
""" ## Warehouse Location Optimization App
### Current Functionality

Our app currently utilizes a pre-stored dataset of world cities, providing you with a comprehensive base for your warehouse location analysis. We plan to expand the app's capabilities by incorporating an option for users to upload their own custom datasets, allowing for even greater flexibility and personalization.

### User Interface

* The app's user-friendly interface guides you through the optimization process seamlessly. 
* Simply go to the Main App tab and enter the ISO3 code of the country you wish to establish warehouses in.
* Select your preferred clustering algorithm (Kmeans or PuLP).
* Specify the desired number of warehouses (between 1 and 30).
* Choose the number of clusters you want to create.

### Future Scope

- We envision a future where our app incorporates real-time data integration to provide even more sophisticated warehouse location optimization capabilities. 
- We also envision on displaying a comparative results of the clustering algorithms that are used in the app.
"""

MODELS_TYPES = {
    'K-Means': kmeans.get_kmeans,
    'Pulp': pulp_model.get_pulp
}



def show_tabs(model_select, map_df, cluster_table, centroids, cluster_labels_df, cap, tab4, tab5, tab6, tab7, tab8):
    """
    Displays chart visualizations on selected tabs after model execution.
    Parameters:
        model_select (str): Selected model.
        map_df (DataFrame): DataFrame with map data.
        cluster_table (DataFrame): DataFrame with clustering results.
        centroids (array): Array of cluster centers.
        cluster_labels_df (DataFrame): DataFrame with cluster labels.
        cap (float): Total capacity of each warehouse.
        tab4, tab5, tab6, tab7, tab8: Streamlit tab objects.
    """
    if map_df is not None and cluster_table is not None:
        # For each tab, display appropriate visualization and summary data
        with tab4:
            pie.piechart(cluster_table)
        with tab5:
            bar.barchart(cluster_table)
        with tab6:
            bar.demand_capacity_difference_barchart(cluster_table)
        with tab7:
            pie.piechart_cluster_count(cluster_table)
        with tab8:
            folium_extra.folium_extra(map_df, cluster_labels_df, centroids)
        for tab in [tab4, tab5, tab6, tab7, tab8]:
            # Display the summary information at the end of each tab
            with tab:
                st.markdown(
                    f"**Total Capacity of each warehouse:** `{cap:,.2f}` Units.", unsafe_allow_html=True)
                st.dataframe(cluster_table.loc[:, cluster_table.columns != 'Demand_Capacity_Difference'],
                             use_container_width=True)


def get_model(model_select, df, num_clusters):
    """
    Selects and returns the appropriate model function based on user selection.
    Parameters:
        model_select (str): Selected model.
        df (DataFrame): Preprocessed DataFrame.
        num_clusters (int): Selected number of clusters.
        dataset_type (str): Selected dataset type.
    Returns:
        function: Model function that returns returns dataframe, cluster labels, and centroids.
    """
    return MODELS_TYPES[model_select](df, num_clusters)


def home_page(df):
    """
    The main function of the application. It displays sidebar, tabs, and visualizations.
    Parameters:
        df (DataFrame): Original DataFrame.
    """
    # Sidebar for the app
    with st.sidebar:
        # Dataset type selection
        st.sidebar.header("⚙️ Data Settings")
        dataset_type = st.text_input(
            "Enter iso3 code of country", 'ITA')

        df = df[df['iso3'] == dataset_type.upper()]
        df['customer_id'] = df.index
        df = normal.normal_data(df)

        # Model selection
        st.sidebar.header("📊 Plot Settings")
        model_select = st.sidebar.selectbox(
            "Model", MODELS_TYPES.keys())

        # Number of clusters selection
        st.sidebar.header("📦 Number of Warehouses")
        values = st.slider('Select a range of values', 1, 30, (2, 8))

        # Determine the number of clusters
        num_clusters = 5
        if values[0] != values[1]:
            num_clusters = st.sidebar.slider(
                "Number of warehouses", min_value=values[0], max_value=values[1], value=int((values[0]+values[1])/2))
        else:
            st.write('Please select a range of values')

        # Run model button
        run_button = st.button("Run")

    # Create all tabs at once
    tabs = st.tabs(["Model results", "Customer Demand plot", "Customer density plot", "Demand per cluster",
                   "Avg distance from cluster", "Demand-capacity constraint", "Customers per cluster", "Cluster density plot"])
    
    # these tabs are always visible.
    with tabs[1]:
        mp = folium_plot.pydeck_plot_data(df)
        st.pydeck_chart(mp)
    with tabs[2]:
        mp = folium_density.pydeck_density_data(df)
        st.pydeck_chart(mp)

    # Run the model and display the results
    if run_button:
        #  # Run the model and display the results
        df, cluster_labels, centroids = get_model(
            model_select, df, num_clusters)
        
        if dataset_type == "Repetition":
            df = df.drop_duplicates() 
        cluster_labels_df = df['Cluster']

        with tabs[0]:
            # Visualize the cluster on the map and display the capacity summary df
            plot_clusters_consumers.visualize_clusters_on_map(
                df, cluster_labels_df, centroids)
            cluster_table, cap = capacity.capcacity_display(df, centroids)
            st.markdown(
                f"**Total Capacity of each warehouse:** `{cap:,.2f}` Units.", unsafe_allow_html=True)
            st.dataframe(cluster_table, use_container_width=True)

        # Display the additional tabs with model results
        show_tabs(model_select, df, cluster_table,
                  centroids, cluster_labels_df, cap, *tabs[3:])
    else:
        # ask the user to run the model.
        with tabs[0]:
            st.info("Please run the model to see the results")
        for tab in tabs[3:]:
            with tab:
                st.info("Please run the model to see this tab content")
