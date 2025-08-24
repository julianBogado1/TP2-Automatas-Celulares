import matplotlib.pyplot as plt

import os

import sys

from resources import path

fig, ax = plt.subplots()

folder = path('order_parameter')

sources = sys.argv[1:] if len(sys.argv) > 1 else os.listdir(folder)
for filename in sources:
    filepath = os.path.join(folder, filename)

    if not os.path.isfile(filepath):
        continue

    with open(filepath, 'r') as f:
        numbers = [float(line.strip()) for line in f if line.strip()]

    y_axis = list(range(0, len(numbers) * 5, 5))
    ax.plot(y_axis, numbers)

ax.ticklabel_format(useOffset=False, style='plain')

plt.xlabel('Pasos', fontsize=20)
plt.ylabel('Orden', fontsize=20)
plt.grid(True)
plt.show()
