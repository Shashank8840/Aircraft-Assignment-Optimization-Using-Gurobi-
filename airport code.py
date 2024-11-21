import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import random

## Fleet meaning: Aircrafts like boeing 707, Airbus 300, etc.

# Read data from the fleet details Excel file
flight_details_df = pd.read_excel('fleet_arrangement.xlsx')

# Read data from the flight details Excel file
aircraft_details_df = pd.read_excel('flight_details.xlsx')

# Extract data from the DataFrames
flight_legs = flight_details_df['Flight name'].tolist()
from_airports = flight_details_df['from'].tolist()
to_airports = flight_details_df['to'].tolist()
departure_times = flight_details_df['departure'].tolist()
arrival_times = flight_details_df['arrival'].tolist()
fare = flight_details_df['fare'].tolist()

aircraft_types = aircraft_details_df['Aircraft'].tolist()
number_of_seats = aircraft_details_df['Seats'].tolist()
number_of_aircraft_available = aircraft_details_df['No. of fleets'].tolist()
operating_cost = aircraft_details_df['Cost/passenger/km'].tolist()

# Generate demand for each flight leg
demand = [250 + random.choice([-100, -50, -25, 0, 25, 50, 75, 100, 200]) for _ in range(len(flight_legs))]

# Create a Gurobi model
model = gp.Model("FlightAssignment")

# Decision variables
x = {}  # Binary variables for flight assignment
y = {}  # Binary variables for aircraft type usage

for i in range(len(flight_legs)):
    for j in range(len(aircraft_types)):
        x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

for j in range(len(aircraft_types)):
    y[j] = model.addVar(vtype=GRB.BINARY, name=f"y_{j}")

model.update()

# Objective function
profit = gp.LinExpr()
for i in range(len(flight_legs)):
    for j in range(len(aircraft_types)):
        profit += fare[i] * demand[i] * x[i, j] - operating_cost[j] * number_of_seats[j] * x[i, j]

model.setObjective(profit, GRB.MAXIMIZE)

# Flow Balance Constraint
for i in range(len(flight_legs)):
    model.addConstr(gp.quicksum(x[i, j] for j in range(len(aircraft_types))) == 1, name=f"FlowBalance_{i}")

# Limited Fleet Availability Constraint
for j in range(len(aircraft_types)):
    model.addConstr(gp.quicksum(x[i, j] for i in range(len(flight_legs))) <= number_of_aircraft_available[j] * y[j], name=f"FleetAvailability_{j}")

# Only One Fleet Type per Flight Leg Constraint
for i in range(len(flight_legs)):
    model.addConstr(gp.quicksum(x[i, j] for j in range(len(aircraft_types))) == 1, name=f"OneFleetPerLeg_{i}")

# Optimize the model
model.optimize()

# Output the results
print("Optimization Status:", model.status)

if model.status == GRB.OPTIMAL:
    print("Optimal Assignment:")
    for i in range(len(flight_legs)):
        for j in range(len(aircraft_types)):
            if x[i, j].x > 0.5:
                print(f"Assign {aircraft_types[j]} to {flight_legs[i]}")

    print("Objective Value (Profit):", model.objVal)
