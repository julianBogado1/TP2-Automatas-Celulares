from particle import Particle as TParticle

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize

import numpy as np

from tqdm import tqdm

import time

import sys

import frames
from resources import config, path
from streaming import SequentialStreamingExecutor as Executor

abar = None
def main(length: float, count: int, show: bool, save: bool):
    global abar

    executor = Executor(frames.next, frames.count())

    fig, ax = plt.subplots()

    ax.set_aspect('equal')
    ax.set_xlim(0, length)
    ax.set_ylim(0, length)

    xdata, ydata, vxdata, vydata, angles = [0.0] * count, [0.0] * count, [0.0] * count, [0.0] * count, [0.0] * count
    q = ax.quiver(
        xdata, ydata, vxdata, vydata, angles,
        angles='xy', scale_units='xy', scale=4, cmap='hsv',
        norm=Normalize(vmin=0, vmax=2*np.pi),
        headwidth=40, headlength=60, headaxislength=50, minlength=0, pivot='middle'
    )

    cbar = fig.colorbar(q, ax=ax, orientation='vertical', label='Angle (radians)')
    cbar.set_ticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
    cbar.set_ticklabels([r'$0$', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])

    def update(particles: list[TParticle]):
        global abar

        xdata.clear()
        ydata.clear()
        vxdata.clear()
        vydata.clear()
        angles.clear()

        for particle in particles:
            xdata.append(particle.x)
            ydata.append(particle.y)
            vxdata.append(np.cos(particle.theta))
            vydata.append(np.sin(particle.theta))
            angles.append((particle.theta + (2 * np.pi)) % (2 * np.pi))

        q.set_offsets(np.c_[xdata, ydata])
        q.set_UVC(vxdata, vydata, angles)

        if abar is not None:
            abar.update()

        return q,

    ani = FuncAnimation(
        fig,
        update,
        frames=executor.stream(),
        save_count=frames.count(),
        interval=5,
        blit=True,
        repeat=True
    )

    if show:
        abar = tqdm(total=frames.count())
        plt.show()
        abar.close()

    if save:
        print("Saving animation...")

        filename = path("animations", f"particles_{int(time.time())}.mp4")
        with tqdm(total=frames.count()) as sbar:
            callback = lambda _i, _n: sbar.update(1)
            ani.save(filename, writer='ffmpeg', fps=60, progress_callback=callback)

        print(f"Animation saved at {filename}.")

    executor.close()

if __name__ == "__main__":
    settings = config(sys.argv[1] if len(sys.argv) > 1 else None)

    if not (settings['save_animation'] or settings['show_animation']):
        print("At least one of save_animation or show_animation must be true.")
        print("Otherwise, this program is useless.")
        sys.exit(0)

    main(settings['l'], settings['n'], settings['show_animation'], settings['save_animation'])
