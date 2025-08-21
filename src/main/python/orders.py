from typing import cast

import matplotlib.pyplot as plt

import os

import sys

from resources import path

box = plt.gca().get_position()
plt.gca().set_position(cast(tuple[float, float, float, float], [box.x0, box.y0, box.width * 0.8, box.height]))

folder = path('order_parameter')

sources = sys.argv[1:] if len(sys.argv) > 1 else os.listdir(folder)
for filename in sources:
    filepath = os.path.join(folder, filename)

    if not os.path.isfile(filepath):
        continue

    with open(filepath, 'r') as f:
        numbers = [float(line.strip()) for line in f if line.strip()]

    plt.plot(numbers, label=filename.replace('.txt', ''))

plt.title('Parametro de Orden en funcion de los pasos')
plt.xlabel('Pasos')
plt.ylabel('Orden')
plt.grid(True)
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()
