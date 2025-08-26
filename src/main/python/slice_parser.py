import os
import glob
import numpy as np
import matplotlib.pyplot as plt

def parse_file(filepath):
    """Parse a consensus_time_steps file into (densities, steps, errors)."""
    densities, steps, errors = [], [], []
    with open(filepath, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
        print(lines)
        # Only process complete triplets
        n = len(lines) // 3
        for i in range(n):
            densities.append(float(lines[3*i]))
            steps.append(float(lines[3*i + 1]))
            errors.append(float(lines[3*i + 2]))

    return np.array(densities), np.array(steps), np.array(errors)

def main():
    folder = "./order_parameters"
    files = sorted(glob.glob(os.path.join(folder, "consensus_time_step*.txt")))

    plt.figure(figsize=(10, 6))

    for file in files:
        densities, steps, errors = parse_file(file)
        label = os.path.basename(file).replace(".txt", "")

        plt.errorbar(
            densities,
            steps,
            yerr=errors,
            marker="o",
            capsize=4,
            label=label
        )
    plt.xscale("log")
    plt.xlabel("Density")
    plt.ylabel("Consensus Time Steps (mean)")
    plt.title("Consensus Time Steps vs Density with Mean Error")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
