package ar.edu.itba.sims;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Random;

import ar.edu.itba.sims.models.Particle;
import ar.edu.itba.sims.neighbours.CIM;

public class Simulator implements Iterable<Simulator.Iteration> {
    private static final Random random = new Random();

    private final List<Particle> particles;
    private final Interact interaction;
    private final double L;
    private final double Rc;
    private final double noise;
    private final int start;
    private final int steps;

    public Simulator(final List<Particle> particles, final InitialConditions conditions) {
        this(particles, conditions, 0);
    }

    public Simulator(final List<Particle> particles, final InitialConditions conditions, int start) {
        this.interaction = switch (conditions.getInteraction()) {
            case "average" -> Simulator::averageInteraction;
            case "voter" -> Simulator::voterInteraction;
            default -> throw new IllegalArgumentException("Unknown interaction type: " + conditions.getInteraction());
        };

        this.particles = particles;
        this.L = conditions.getL();
        this.Rc = conditions.getR();
        this.noise = conditions.getNoise();
        this.steps = conditions.getSteps();
        this.start = start;
    }

    @Override
    public Iterator<Iteration> iterator() {
        return new Iterator<Iteration>() {
            private int current = start;
            private List<Particle> simulation = List.copyOf(particles);

            @Override
            public boolean hasNext() {
                return current < steps;
            }

            @Override
            public Iteration next() {
                final List<Particle> result = new ArrayList<>(particles.size());

                CIM.evaluate(simulation, L, Rc).forEach((p, neighbours) -> {
                    var velocity = p.getVelocity();
                    var newX = p.getX() + velocity.getX();
                    var newY = p.getY() + velocity.getY();

                    // Check boundaries
                    if (newX < 0 || newX > L) {
                        newX = Math.abs(newX + L) % L; // Wrap around horizontally
                    }

                    if (newY < 0 || newY > L) {
                        newY = Math.abs(newY + L) % L; // Wrap around vertically
                    }

                    final var n = random.nextDouble(noise) - noise / 2;
                    final var newTheta = interaction.interact(p, neighbours) + n;

                    result.add(new Particle(newX, newY, p.getR(), p.getV(), newTheta));
                });

                simulation = result;
                current++;

                return new Iteration(current, List.copyOf(simulation));
            }
        };
    }

    public List<Particle> getInitialState() {
        return particles;
    }

    public int getSteps() {
        return steps;
    }

    private static double averageInteraction(final Particle p, final List<Particle> neighbours) {
        return p.computeAvgTheta(neighbours);
    }

    private static double voterInteraction(final Particle p, final List<Particle> neighbours) {
        return neighbours.get(random.nextInt(neighbours.size())).getTheta();
    }

    public record Iteration(int step, List<Particle> particles) {
    }

    private interface Interact {
        double interact(final Particle p, final List<Particle> neighbours);
    }
}
