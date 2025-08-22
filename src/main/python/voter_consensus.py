
import matplotlib.pyplot as plt
import os
import json
import sys
from resources import path


def vary_prams():
    # Load initial conditions
    with open(path('initial_conditions.json'), 'r') as f:
        config = json.load(f)

    # Parameters to vary
    densities = [0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000]
    particles = []
    L_dimensions = []

    for density in densities:
        # Calculate particles and L for each density
        # Assuming a base relationship, adjust as needed
        L = 10  # Base L dimension
        N = int(density * L * L)  # particles = density * area
    
        particles.append(N)
        L_dimensions.append(L)

    # Save the modified configuration
    with open(path('initial_conditions.json'), 'w') as f:
        json.dump(config, f, indent=4)

def graph_position():
    # Read the first time slice file
    timeslices_dir = path('time_slices')
    files = sorted([f for f in os.listdir(timeslices_dir) if f.endswith('.txt')])
    
    if not files:
        print("No time slice files found")
        return
    
    first_file = os.path.join(timeslices_dir, files[0])
    
    def avg_velocity_direction(file):
        # Read positions from the file
        thetas = []
        
        with open(file, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        theta = float(parts[4])
                        thetas.append(theta)
        avg_theta = sum(thetas) / len(thetas) if thetas else 0
        return avg_theta
    
    avg_theta = avg_velocity_direction(first_file)
    print(f"Average velocity direction (theta) in first time slice: {avg_theta} radians")

# Call the function
graph_position()