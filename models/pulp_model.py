import numpy as np
import pandas as pd
from math import sin, cos, asin, acos, radians
from pulp import LpProblem, LpMinimize, LpVariable, LpBinary, lpSum, LpStatus, value
import matplotlib.pyplot as plt
plt.style.use('ggplot')


def get_pulp(df, num_clusters):
    """
    Executes the Pulp algorithm.
    Parameters:
        df (DataFrame): Preprocessed DataFrame.
        num_clusters (int): Number of clusters.
    Returns:
        tuple: Tuple containing the updated DataFrame, cluster labels and centroid centers.
    """
    return process_data(df, num_clusters)


def process_data(df, num_clusters):
    """
    Use the Pulp model checker to find the solution.
    Parameters:
        df (DataFrame): Preprocessed DataFrame.
        n_warehouses (int): Number of warehouses (clusters).
    Returns:
        tuple: Tuple containing the updated DataFrame, cluster labels and warehouse locations.
    """ 

    #Dictionary of customer and demand
    demand_dict = {customer: df['Demand'][i]
                   for i, customer in enumerate(df.index)}
    
    #Mention random state so that the warehouses are not chosen differently every time for the same no. of clusters
    RANDOM_STATE = 2
    
    #Table representing location of warehouses
    new_df = df.sample(n=num_clusters, random_state=RANDOM_STATE) #faculty_df
    new_df = new_df.reset_index()
    
    #Table representing the customer locations same as the original dataframe
    customer_df = df
    
    #Specify the setup cost and the supply per warehouse
    SETUP_COST = 10**5
    SUPPLY_PER_WAREHOUSE = df['Demand'].sum() / num_clusters    #capacity of warehouses
    SUPPLY_PER_WAREHOUSE += 0.1 * SUPPLY_PER_WAREHOUSE
    
    #Add the column warehouse_id to the warehouses database
    new_df['warehouse_id'] = ['Warehouse' +
                              str(i) for i in range(0, new_df.shape[0])]
    
    #Dictionary of supply and setup cost for each warehouse
    annual_supply_dict = {
        warehouse: SUPPLY_PER_WAREHOUSE for warehouse in new_df['warehouse_id']}
    annual_cost_dict = {
        warehouse: SETUP_COST for warehouse in new_df['warehouse_id']}
    
    #Dictionary representing transport cost from every warehouse to every customer
    transport_costs_dict = {}
    for i in range(new_df.shape[0]):
        warehouse_transport_costs_dict = {}
        for j in customer_df.index:
            if new_df['lat'].iloc[i] == customer_df.loc[j, 'lat'] and new_df['lng'].iloc[i] == customer_df.loc[j, 'lng']:
                d = 0
            else:
                d = haversine_distance(
                    new_df['lat'].iloc[i], new_df['lng'].iloc[i], customer_df.loc[j, 'lat'], customer_df.loc[j, 'lng'])
            warehouse_transport_costs_dict.update({j: travelling_cost(d)})
        transport_costs_dict.update(
            {new_df['warehouse_id'].iloc[i]: warehouse_transport_costs_dict})
    # Note that wherever you used customer_df.index[j] or customer_df['customer_id'][j], you just need to use customer_df.index[j]
    
    #Inititalize the problem
    lp_problem = LpProblem('CFLP', LpMinimize) #capacitated facility location problem
    
    #Variable representing whether facility has to be created or not
    created_facility = LpVariable.dicts(
        'Create_facility', new_df['warehouse_id'], 0, 1, LpBinary)
    
    #Variable representing no. of units being served
    served_customer = LpVariable.dicts('Link', [(
        i, j) for i in customer_df.index for j in new_df['warehouse_id']], 0)
    
    #Binary Variable describing whether i customer has been allocated to j warehouse
    bin = LpVariable.dicts('One', [(i, j) for i in customer_df.index
                           for j in new_df['warehouse_id']], 0, 1, LpBinary)
    
    #Specify the objective
    objective = lpSum(annual_cost_dict[j]*created_facility[j] for j in new_df['warehouse_id']) +\
        lpSum(transport_costs_dict[j][i]*served_customer[(i, j)]
              for j in new_df['warehouse_id'] for i in customer_df.index)
    
    #Add the objective to the problem
    lp_problem += objective

    # One User One Inventory
    for i in customer_df.index:
        lp_problem += lpSum(bin[(i, j)] for j in new_df['warehouse_id']) == 1

    # Demand Constraint
    for i in customer_df.index:
        lp_problem += lpSum(served_customer[(i, j)]
                            for j in new_df['warehouse_id']) == demand_dict[i]

    # Capacity Constraint
    for j in new_df['warehouse_id']:
        lp_problem += lpSum(served_customer[(i, j)] for i in customer_df.index
                            ) <= annual_supply_dict[j]*created_facility[j]

    #Solve the problem   
    lp_problem.solve()

    #Dictionary reprenting whcih customers have been assigned to which warehouse
    assigned_customers = {warehouse: []
                          for warehouse in new_df['warehouse_id']}
    for (customer, warehouse), variable in served_customer.items():
        if variable.varValue > 0:
            assigned_customers[warehouse].append(customer)
    
    
    # Calculate total demand for each warehouse
    total_demand_dict = {warehouse: sum(
        demand_dict[customer] for customer in assigned_customers[warehouse]) for warehouse in assigned_customers}
    
    for warehouse, customers in assigned_customers.items():
        assigned_customers[warehouse] = list(set(customers))

    # Check if any customer is assigned to multiple warehouses
    duplicate_customers = []
    for customer in customer_df.index:
        assigned_to_warehouses = []
        for warehouse, customers in assigned_customers.items():
            if customer in customers:
                assigned_to_warehouses.append(warehouse)
        if len(assigned_to_warehouses) > 1:
            duplicate_customers.append(customer)

    # Remove duplicate assignments by keeping the customer assigned to only one warehouse
    for customer in duplicate_customers:
        warehouses = []
        for warehouse, customers in assigned_customers.items():
            if customer in customers:
                warehouses.append(warehouse)
        # Keep the customer assigned to the first warehouse and remove from the others
        for warehouse in warehouses[1:]:
            assigned_customers[warehouse].remove(customer)
            total_demand_dict[warehouse] -= demand_dict[customer]
    
    var_continue = 0
    # Iterate over warehouses to check and reassign if needed
    while any(total_demand > annual_supply_dict[warehouse] for warehouse, total_demand in total_demand_dict.items()):
        # Iterate over warehouses
        for warehouse in assigned_customers:
            if total_demand_dict[warehouse] > annual_supply_dict[warehouse]:
                # Sort assigned customers by demand in descending order
                try:
                    assigned_customers[warehouse].sort(
                        key=lambda customer: transportation_cost(customer, warehouse, customer_df, new_df), reverse=True)
                except:
                    var_continue += 1
                # Reassign customers until capacity is not exceeded or no more reassignments are possible
                while total_demand_dict[warehouse] > annual_supply_dict[warehouse]:
                    reassigned = False

                    # Remove customer with highest demand from the current warehouse
                    customer_to_reassign = assigned_customers[warehouse].pop(0)
                    total_demand_dict[warehouse] -= demand_dict[customer_to_reassign]

                    # Find the closest warehouse with available capacity
                    closest_warehouse = None
                    min_distance = float('inf')
                    for other_warehouse in assigned_customers:
                        if total_demand_dict[other_warehouse] + demand_dict[customer_to_reassign] <= annual_supply_dict[other_warehouse]:
                            distance = haversine_distance(customer_df.loc[customer_to_reassign, 'lat'],
                                                          customer_df.loc[customer_to_reassign, 'lng'],
                                                          new_df.loc[new_df['warehouse_id']
                                                                     == other_warehouse, 'lat'],
                                                          new_df.loc[new_df['warehouse_id'] == other_warehouse, 'lng'])

                            if distance < min_distance:
                                min_distance = distance
                                closest_warehouse = other_warehouse

                    # Reassign the customer to the closest warehouse
                    if closest_warehouse is not None:
                        assigned_customers[closest_warehouse].append(
                            customer_to_reassign)
                        total_demand_dict[closest_warehouse] += demand_dict[customer_to_reassign]
                        reassigned = True

                    # Break the loop if no more reassignments are possible
                    if not reassigned:
                        break    
    
    #Array in which index is representing customer and the value at a particular index is warehouse id
    labels = []
    for i in range(len(customer_df)):
        labels.append(0)

    count = 0
    for warehouse in list(assigned_customers.keys()):
        for j in assigned_customers[warehouse]:
            labels[j] = count
        count += 1

       
    #Convert labels to numpy array and add it as a cluster column in df
    labels = np.asarray(labels)
    demand = df['Demand'].to_numpy()
    coordinates = df[['lat', 'lng']].to_numpy()
    centroids = new_df[['lat', 'lng']].to_numpy()
    df['Cluster'] = labels
    
    #Return parameters
    return df, labels, centroids

#Calculate Haversine distance between two locations
def haversine_distance(lat1, lon1, lat2, lon2):
    return 6371.01 *\
        acos(sin(radians(lat1))*sin(radians(lat2)) +
             cos(radians(lat1))*cos(radians(lat2))*cos(radians(lon1)-radians(lon2)))

#Calculate Travelling cost when distance is passed as parameter
def travelling_cost(distance):
    petrol_price = 1.87
    mileage = 0.38
    return petrol_price*mileage*distance

#Returns the customer and the warehouse through which it is being served
def get_linked_customers(input_warehouse, served_customer):
    # Initialize empty list
    linked_customers = []

    # Iterate through the xij decision variable
    for (k, v) in served_customer.items():

        # Filter the input warehouse and positive variable values
        if k[1] == input_warehouse and v.varValue > 0:

            # Customer is served by the input warehouse
            linked_customers.append(k[0])

    return linked_customers

#Returns the transportation cost . Either this or travelling_cost can be used
def transportation_cost(customer, warehouse, customer_df, new_df):
    # Retrieve the latitude and longitude of the customer and warehouse
    customer_lat = customer_df.loc[customer_df['customer_id']
                                   == customer, 'lat'].values[0]
    customer_lng = customer_df.loc[customer_df['customer_id']
                                   == customer, 'lng'].values[0]
    warehouse_lat = new_df.loc[new_df['warehouse_id']
                               == warehouse, 'lat'].values[0]
    warehouse_lng = new_df.loc[new_df['warehouse_id']
                               == warehouse, 'lng'].values[0]

    # Calculate the haversine distance between the customer and warehouse
    distance = haversine_distance(
        customer_lat, customer_lng, warehouse_lat, warehouse_lng)

    # You can replace this with your actual cost calculation formula
    cost = distance * 10  # Assuming a cost of $10 per kilometer

    return cost