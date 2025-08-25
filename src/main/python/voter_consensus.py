
import matplotlib.pyplot as plt
import os
import json
import numpy as np
import sys
from resources import path

with open(f"order_parameters/consensus_time_step.txt", "w") as out_file:
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
        Reads all txt files in a folder
        and returns the time step at which consensus is reached.
        """
        files = [f for f in os.listdir(folder) if f.endswith(".txt")]
        files.sort(key=lambda x: int(os.path.splitext(x)[0]))
        time_steps = 0

        for file in files:
            filepath = os.path.join(folder, file)
            print(f"\n Processing {filepath}")
            avg_v = compute_avg_velocity(filepath)
            print(f" Average velocity: {avg_v}")
            time_steps += 1
            if(avg_v >= 0.95):
                print(f"Reached consensus at time step {time_steps}")
                return time_steps
        
        return -1


    results = []
    def vary_prams():
        # Load initial conditions
        config = {}
        with open(path('initial_conditions.json'), 'r') as f:
            config = json.load(f)

        # params = [
        #     {
        #         'length': 1000,
        #         'particles': 100,   #density = 0.0001
        #         'steps': 50000
        #     },
        #     {
        #         'length': 1000,
        #         'particles': 1000,  #density = 0.001
        #         'steps': 40000
        #     },
        #     {
        #         'length': 10000,
        #         'particles': 10000,  #density = 0.01
        #         'steps': 15000
        #     },
        #     {
        #         'length': 100,
        #         'particles': 1000,  #density = 0.1
        #         'steps': 15000
        #     },
        #     {
        #         'length': 100,
        #         'particles': 10000,  #density = 1
        #         'steps': 10000
        #     },
        #     {
        #         'length': 100,
        #         'particles': 60000,  #density = 6
        #         'steps': 5000
        #     },
        #     {
        #         'length': 10,
        #         'particles': 1000,  #density = 10
        #         'steps': 5000
        #     },
        #     {
        #         'length': 10,
        #         'particles': 10000,  #density = 100
        #         'steps': 5000
        #     },
        #     {
        #         'length': 10,
        #         'particles': 60000,  #density = 600
        #         'steps': 20000
        #     }
        # ]

        densities = np.linspace(0.0001, 100, 20).tolist()
        # for i in range(len(params)):
            # config['l'] = params[i]['length']
            # config['n'] = params[i]['particles']
            # config['steps'] = params[i]['steps']
        for i in range(len(densities)):
            N = config['n']
            config['l'] = int(np.sqrt(N / densities[i]))
            with open(path('initial_conditions.json'), 'w') as f:
                json.dump(config, f, indent=4)
            # input(f"Running for length={config['l']} particles={config['n']} steps={config['steps']}...")
            os.system("bash ../../../run.sh")
            res = get_consensus_time_step(path('time_slices/'))
            results.append(res)
            out_file.write(f"{res}\n")
    vary_prams()

for v in results:
    print(f"Consensus time step for run {results.index(v)}: {v}")
