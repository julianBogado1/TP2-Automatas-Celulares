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
    ax.plot(y_axis, numbers, label=filename.replace('.txt', ''))

ax.ticklabel_format(useOffset=False, style='plain')

fig.tight_layout()
fig.subplots_adjust(right=0.8)
fig.legend(loc=7)

plt.title('Orden en funcion de los pasos')
plt.xlabel('Pasos')
plt.ylabel('Orden')
plt.grid(True)
plt.show()
