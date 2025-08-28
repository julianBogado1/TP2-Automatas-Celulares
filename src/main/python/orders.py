import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import numpy as np

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

def sci_notation(val, _):
    if val == 0:
        return rf"$0\times 10^{{0}}$"
    exponent = int(np.floor(np.log10(abs(val))))
    coeff = val / 10**exponent
    # if int(coeff) == 1:
    #     return rf"$10^{{{exponent}}}$"
    return rf"${coeff:.0f}\times 10^{{{exponent}}}$"

ax.xaxis.set_major_formatter(FuncFormatter(sci_notation))
ax.yaxis.set_major_formatter(FuncFormatter(sci_notation))

# ax.ticklabel_format(useOffset=False, style='plain')

# ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
# ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

plt.xlabel('Pasos', fontsize=20)
plt.ylabel('Orden', fontsize=20)
plt.grid(True)
plt.show()
