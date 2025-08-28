import os

from functools import cache

from particle import Particle
import resources

def next(f: int):
    """
    Reads the input file for a given frame.
    """
    file_path = resources.path('time_slices', f"{f}.txt")
    with open(file_path, 'r') as file:
        # Iterate through the lines and convert them to Particles
        return f, [Particle(*map(float, line.strip().split())) for line in file]

@cache
def count():
    """
    Counts the number of files in the input directory.

    Assumes all the files are input files.
    """
    return len(os.listdir(resources.path('time_slices')))
