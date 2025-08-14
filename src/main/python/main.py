import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import frames
from resources import config

def main(length: float):
    fig, ax = plt.subplots()

    ax.set_aspect('equal')
    ax.set_xlim(0, length)
    ax.set_ylim(0, length)

    xdata, ydata = [], []
    ln, = ax.plot([], [], 'ro')

    def update(frame: int):
        particles = frames.next(frame)
        xdata.clear()
        ydata.clear()

        for particle in particles:
            xdata.append(particle.x)
            ydata.append(particle.y)

        ln.set_data(xdata, ydata)
        return ln,

    ani = FuncAnimation( # pyright: ignore[reportUnusedVariable]
        fig,
        update,
        frames=frames.count(),
        interval=200,
        blit=True
    )

    plt.show()

if __name__ == "__main__":
    main(config()['l'])
