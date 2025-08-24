import os

import sys

import numpy as np

from resources import path

if len(sys.argv) != 3:
    print("Usage: python average.py <filename> <start_index>")
    sys.exit(1)

filepath = path("order_parameter", sys.argv[1])
start = int(sys.argv[2])

if not os.path.isfile(filepath):
    print(f"File {filepath} does not exist.")
    sys.exit(1)

with open(filepath, 'r') as f:
    numbers = [float(line.strip()) for line in f if line.strip()]

if start < 0 or start >= len(numbers):
    print(f"Start index {start} is out of bounds for the data length {len(numbers)}.")
    sys.exit(1)

average = np.mean(numbers[start:])
print(average)
