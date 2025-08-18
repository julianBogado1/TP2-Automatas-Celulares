import matplotlib.pyplot as plt

import os

import sys

from resources import path

folder = path('order_parameter')

sources = sys.argv[1:] if len(sys.argv) > 1 else os.listdir(folder)
for filename in sources:
    filepath = os.path.join(folder, filename)

    if not os.path.isfile(filepath):
        continue

    with open(filepath, 'r') as f:
        numbers = [float(line.strip()) for line in f if line.strip()]

    plt.plot(numbers, label=filename.replace('.txt', ''))

plt.title('Parametro de Orden en funcion del Tiempo')
plt.xlabel('Tiempo (steps)')
plt.ylabel('Orden')
plt.grid(True)
plt.legend()
plt.show()
