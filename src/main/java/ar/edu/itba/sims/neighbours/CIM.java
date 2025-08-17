package ar.edu.itba.sims.neighbours;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import ar.edu.itba.sims.models.Matrix;
import ar.edu.itba.sims.models.Particle;

public abstract class CIM {
    private static final ExecutorService executor = Executors.newFixedThreadPool(8);

    /**
     * Evaluates the interaction between particles in a simulation box.
     *
     * @apiNote Particles are assumed to be points (radius of 0).
     * @apiNote Particles are neighbours to themselves.
     * @apiNote Particles are assumed to be in a periodic boundary condition box.
     *
     * @param particles List of particles to evaluate
     * @param L         Length of the simulation box
     * @param Rc        Interaction radius
     * @return A map where each key is a particle and the value is a list of
     *         particles that interact with it.
     */
    public static Map<Particle, List<Particle>> evaluate(final List<Particle> particles, double L, double Rc) {
        if (executor.isShutdown()) {
            throw new IllegalStateException("Executor service is shut down");
        }

        final var M = (int) (L / Rc);
        final var R2 = Rc * Rc;

        final var tasks = new ArrayList<Callable<Object>>(particles.size());
        final var matrix = new Matrix<>(M, LinkedList<Particle>::new);
        final var result = new ConcurrentHashMap<Particle, List<Particle>>();

        for (final var p : particles) {
            var i = (int) (p.getX() / Rc);
            var j = (int) (p.getY() / Rc);
            matrix.get(i, j).add(p);

            final var neighbours = new LinkedList<Particle>();
            neighbours.add(p);
            result.putIfAbsent(p, neighbours);

            // "Clean code"
            final var coordinates = List.of(
                    new WrappedCoordinate(i - 1, j - 1, M),
                    new WrappedCoordinate(i - 1, j, M),
                    new WrappedCoordinate(i - 1, j + 1, M),
                    new WrappedCoordinate(i, j - 1, M),
                    new WrappedCoordinate(i, j, M)
            );

            tasks.add(Executors.callable(new Task(p, result, L, R2, matrix, coordinates)));
        }

        try {
            executor.invokeAll(tasks);
        } catch (InterruptedException e) {
            throw new RuntimeException("Evaluation interrupted", e);
        }

        return result;
    }

    public static void shutdown() {
        executor.shutdown();
    }

    private static record Task(Particle p, Map<Particle, List<Particle>> result, double L, double R2,
            Matrix<LinkedList<Particle>> matrix, List<WrappedCoordinate> coordinates) implements Runnable {
        @Override
        public void run() {
            for (final var coords : coordinates) {
                final var quadrant = matrix.get(coords.getX(), coords.getY());

                for (final var other : quadrant) {
                    if (p.getId() < other.getId() && p.sqrdDistance(other, L) < R2) {
                        result.compute(p, (p, list) -> {
                            list.add(other);
                            return list;
                        });

                        result.compute(other, (p, list) -> {
                            list.add(p);
                            return list;
                        });
                    }
                }
            }
        }
    }

    private static class WrappedCoordinate {
        private final int x;
        private final int y;

        public WrappedCoordinate(int x, int y, int M) {
            this.x = (x + M) % M;
            this.y = (y + M) % M;
        }

        public int getX() {
            return x;
        }

        public int getY() {
            return y;
        }
    }
}
