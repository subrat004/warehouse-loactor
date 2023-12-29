import plotly.express as px
import plotly.subplots as sp
import streamlit as st
import plotly.graph_objects as go


def barchart(cluster_table):
    fig = px.bar(cluster_table,
                 x='Cluster',
                 y='Average Distance',
                 title='Average Distance per Cluster',
                 hover_data=['Average Distance'],
                 labels={'Average Distance': 'Average Distance (in units)',
                         'Cluster': f'Cluster (Total: {len(cluster_table["Cluster"])} clusters)'}
                 )

    st.plotly_chart(fig, use_container_width=True)


def demand_capacity_difference_barchart(cluster_table):
    cluster_table['Demand_Capacity_Difference'] = cluster_table['Capacities in Units'] - \
        cluster_table['Total Demand per Cluster in Units']

    # Change colors based on positive or negative values
    colors = ['green' if x >
              0 else 'red' for x in cluster_table['Demand_Capacity_Difference']]

    fig = go.Figure()

    # Add a bar for demand with conditional coloring
    fig.add_trace(go.Bar(
        x=cluster_table['Cluster'],
        y=cluster_table['Total Demand per Cluster in Units'],
        marker=dict(color=colors),
        name='Demand',
        hovertext=cluster_table['Demand_Capacity_Difference'],
        hoverinfo='x+y+text'
    ))

    max_capacity = cluster_table['Capacities in Units'].max()

    # Add a line for capacity
    fig.add_trace(go.Scatter(
        x=[cluster_table['Cluster'].min()-0.6, cluster_table['Cluster'].max()+0.6],
        y=[max_capacity, max_capacity],
        mode='lines',
        name='Capacity',
        line=dict(color='red', dash='dash')
    ))

    fig.update_layout(
        title="Demand and Capacity Differences across Clusters",
        yaxis=dict(title='Demand (in units)'),
        xaxis=dict(
            title=f'Cluster (Total: {len(cluster_table["Cluster"])} clusters)'),
        autosize=True,
        annotations=[
            dict(
                x=0.85,
                y=1.15,
                xref='paper',
                yref='paper',
                text="Bar Color Explanation:",
                showarrow=False
            ),
            dict(
                x=0.85,
                y=1.10,
                xref='paper',
                yref='paper',
                text="Green: Demand <= Capacity",
                showarrow=False,
                font=dict(color="green")
            ),
            dict(
                x=0.85,
                y=1.05,
                xref='paper',
                yref='paper',
                text="Red: Demand > Capacity",
                showarrow=False,
                font=dict(color="red")
            ),
            dict(
                x=len(cluster_table['Cluster']),
                y=1.08*max_capacity,
                xref='x',
                yref='y',
                text=f"Maximum Capacity: {max_capacity:,.2f}",
                showarrow=False,
                font=dict(color="black")
            ),
        ]
    )

    st.plotly_chart(fig, use_container_width=True)
