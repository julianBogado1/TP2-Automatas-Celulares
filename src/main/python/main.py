from particle import Particle as TParticle

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import numpy as np

import time

import frames
from resources import config, path
from streaming import SequentialStreamingExecutor as Executor

def main(length: float, count: int, save: bool):
    executor = Executor(frames.next, frames.count())

    fig, ax = plt.subplots(figsize=(length,length))
    colormap = plt.get_cmap('brg')

    ax.set_aspect('equal')
    ax.set_xlim(0, length)
    ax.set_ylim(0, length)

    xdata, ydata, vxdata, vydata, color = [0.0] * count, [0.0] * count, [0.0] * count, [0.0] * count, [colormap(0)] * count
    q = ax.quiver(
        xdata, ydata, vxdata, vydata, color=color,
        angles='xy', scale_units='xy', scale=10,
        headwidth=40, headlength=60, headaxislength=50, minlength=0
    )

    def update(particles: list[TParticle]):
        xdata.clear()
        ydata.clear()
        vxdata.clear()
        vydata.clear()
        color.clear()

        for particle in particles:
            xdata.append(particle.x)
            ydata.append(particle.y)
            vxdata.append(np.cos(particle.theta))
            vydata.append(np.sin(particle.theta))
            color.append(colormap((particle.theta % (2 * np.pi)) / (2 * np.pi)))

        q.set_offsets(np.c_[xdata, ydata])
        q.set_UVC(vxdata, vydata)
        q.set_color(color)

        return q,

    ani = FuncAnimation( # pyright: ignore[reportUnusedVariable]
        fig,
        update,
        frames=executor.stream(),
        save_count=frames.count(),
        interval=5,
        blit=True
    )

    plt.show()
    executor.close()

    if save:
        print("Saving animation...")
        filename = path("animations", f"particles_{int(time.time())}.gif")
        ani.save(filename, writer='ffmpeg', fps=30, dpi=600)
        print(f"Animation saved at {filename}.")

if __name__ == "__main__":
    main(config()['l'], config()['n'], config()['save_gif'])
