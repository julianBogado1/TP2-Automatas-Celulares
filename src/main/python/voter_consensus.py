
import matplotlib.pyplot as plt
import os
import json
import numpy as np
import sys
from resources import path

with open(f"order_parameters/consensus_time_step{sys.argv[1]}.txt", "w") as out_file:
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

    def tau_approx(N, rho):
        if rho <= 1/np.pi:
            tau = (2*N/(np.pi * rho))
            if tau > 40000:
                return 40000
            return tau+100
        else:
            return 7000

    def get_consensus_time_step(folder):
        """
        Reads all txt files in a folder
        and returns the time step at which consensus is reached.
        """
        files = [f for f in os.listdir(folder) if f.endswith(".txt")]
        files.sort(key=lambda x: int(os.path.splitext(x)[0]))
        time_steps = 0

        for file in files:
            filepath = os.path.join(folder, file)
            avg_v = compute_avg_velocity(filepath)
            time_steps += 1
            if(avg_v >= 0.95):
                return time_steps * 5
        
        return -1


    results = []
    def vary_prams():
        # Load initial conditions
        config = {}
        with open(path('initial_conditions.json'), 'r') as f:
            config = json.load(f)

        # densities = np.logspace(2,3, 3).tolist()
        densities = [170, 200]
        N = config['n']
        timesteps = [tau_approx(N, rho) for rho in densities]
        print(densities)
        print(timesteps)
        for i in range(len(densities)):
            
            config['l'] = int(np.sqrt(N / densities[i]))
            config['steps'] = int(timesteps[i])
            with open(path('initial_conditions.json'), 'w') as f:
                json.dump(config, f, indent=4)

            consensuses = []
            for j in range(10):

                os.system("bash ../../../run.sh")
                res = get_consensus_time_step(path('time_slices/'))
                # results.append(res)
                consensuses.append(res)
            
            mean_consensus = np.mean(consensuses)
            std_error = np.std(consensuses) / np.sqrt(len(consensuses))
            out_file.write(f"{densities[i]}\n")
            out_file.write(f"{mean_consensus}\n")
            out_file.write(f"{std_error}\n")
            out_file.write("\n")
    vary_prams()
