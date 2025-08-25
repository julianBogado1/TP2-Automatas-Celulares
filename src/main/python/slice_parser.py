import os
import sys
import numpy as np

def compute_avg_velocity(filename):
    """
    Reads a single time slice file and computes avg velocity.
    """
    vx_list = []
    vy_list = []
    v_val = None
    
    with open(filename, "r") as f:
        for line in f:
            if not line.strip():
                continue
            x, y, r, v, theta = map(float, line.split())
            v_val = v  # all v should be the same
            vx = v * np.cos(theta)
            vy = v * np.sin(theta)
            vx_list.append(vx)
            vy_list.append(vy)
    
    N = len(vx_list)
    if N == 0:
        return 0.0
    
    # Vector sum
    total_vx = sum(vx_list)
    total_vy = sum(vy_list)
    magnitude = np.sqrt(total_vx**2 + total_vy**2)
    
    # Formula: 1 / (N * v) * |sum v_i|
    avg_v = magnitude / (N * v_val)
    return avg_v


def get_consensus_time_step(folder):
    """
    Reads all txt files in a folder, sorted by name, 
    and returns the time step at which consensus is reached.
    """
    files = [f for f in os.listdir(folder) if f.endswith(".txt")]
    files.sort(key=lambda x: int(os.path.splitext(x)[0]))
    time_steps = 0

    for file in files:
        filepath = os.path.join(folder, file)
        print(f"\n Processing {filepath}")
        avg_v = compute_avg_velocity(filepath)
        time_steps += 1
        if(avg_v >= 0.95):
            print(f"Reached consensus at time step {time_steps}")
            break
    
    return time_steps


if __name__ == "__main__":
    folder = "../resources/time_slices/"  # change this!
    consensus_time_step = get_consensus_time_step(folder)
    with open(f"order_parameters/consensus_time_step.txt", "w") as out_file:
        out_file.write(f"{consensus_time_step}\n")
