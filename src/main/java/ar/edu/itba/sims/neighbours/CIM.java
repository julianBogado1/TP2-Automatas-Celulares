package ar.edu.itba.sims.neighbours;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import ar.edu.itba.sims.models.Matrix;
import ar.edu.itba.sims.models.Particle;

public abstract class CIM {
    /**
     * Evaluates the interaction between particles in a simulation box.
     *
     * @apiNote Particles are assumed to be points (radius of 0).
     * @apiNote Particles are neighbours to themselves.
     *
     * @param particles List of particles to evaluate
     * @param L         Length of the simulation box
     * @param Rc        Interaction radius
     * @return A map where each key is a particle and the value is a list of particles that interact with it.
     */
    public static Map<Particle, List<Particle>> evaluate(final List<Particle> particles, double L, double Rc) {
        final var M = (int) (L / Rc);
        final var R2 = Rc * Rc;

        final var matrix = new Matrix<>(M, LinkedList<Particle>::new);
        final var result = new HashMap<Particle, List<Particle>>();

        for (final var p : particles) {
            int i = (int) (p.getX() / Rc);
            int j = (int) (p.getY() / Rc);
            matrix.get(i, j).add(p);

            List<Particle> neighbours = new LinkedList<>();
            neighbours.add(p);
            result.putIfAbsent(p, neighbours);
        }

        for (final var quadrant : matrix) {
            for (Particle p1 : quadrant) {
                for (Particle p2 : quadrant) {
                    if (p1.getId() < p2.getId() && p1.sqrdDistance(p2, L) < R2) {
                        result.get(p1).add(p2);
                        result.get(p2).add(p1);
                    }
                }
            }
        }

        return result;
    }
}
