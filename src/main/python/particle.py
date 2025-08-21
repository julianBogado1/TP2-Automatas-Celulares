from dataclasses import dataclass

@dataclass(frozen=True)
class Particle:
    x: float
    y: float
    radius: float
    velocity: float
    theta: float
