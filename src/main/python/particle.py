import numpy as np

class Particle:
    def __init__(self, x: float, y: float, radius: float, velocity: float, theta: float):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity = velocity
        self.theta = theta
