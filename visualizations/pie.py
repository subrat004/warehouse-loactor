import plotly.express as px
import streamlit as st


def piechart(cluster_table):
    cluster_demand_distribution = cluster_table['Total Demand per Cluster in Units']

    fig = px.pie(cluster_demand_distribution,
                 values=cluster_demand_distribution.values,
                 names=cluster_demand_distribution.index,
                 title='Demand Distribution per Cluster',
                 hover_data=['Total Demand per Cluster in Units'],
                 labels={'label': 'Cluster',
                         'value': 'Total Demand per Cluster in Units'},
                 )

    fig.update_traces(textinfo='percent+label+value',  # Show percent, label and value
                      hovertemplate="%{label}: %{value} <br>Demand: %{customdata[0]}")

    st.plotly_chart(fig, use_container_width=True)


def piechart_cluster_count(cluster_table):
    # Group the data by 'Cluster' and count the number of data points in each cluster
    cluster_count_distribution = cluster_table['Customers per cluster']

    fig = px.pie(cluster_count_distribution,
                 values=cluster_count_distribution.values,
                 names=cluster_count_distribution.index,
                 title='Number of Points in Each Cluster',
                 hover_data=['Customers per cluster'],
                 labels={'label': 'Cluster', 'value': 'Count'},
                 )

    fig.update_traces(textinfo='percent+label+value',  # Show percent, label and value
                      hovertemplate="%{label}: %{value} <br>Count: %{customdata[0]}")

    st.plotly_chart(fig, use_container_width=True)
