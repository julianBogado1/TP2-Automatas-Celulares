package ar.edu.itba.sims;

import ar.edu.itba.sims.models.Particle;
import ar.edu.itba.sims.models.Vector;
import ar.edu.itba.sims.neighbours.CIM;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;

public class Main {
    public static void main(String[] args) {

        InitialConditions ic = InitialStateParser.parse("initial_conditions.json", InitialConditions.class);
        List<Particle> particles = InitialStateParser.buildInitialState(ic);

        double L = ic.getL();
        double Rc = ic.getR();
        double noise = ic.getNoise();
        int steps = ic.getSteps();

        simulate(L, Rc, noise, steps, particles);

    }

    public static List<Particle> nextFrame(Map<Particle, List<Particle>> particles_neighbors, double L, double noise) {

        List<Particle> result = new ArrayList<>();

        for (Map.Entry<Particle, List<Particle>> entry : particles_neighbors.entrySet()) {
            // POSITION
            Vector velocity = Vector.fromPolar(entry.getKey().getV(), entry.getKey().getTheta());
            double newX = entry.getKey().getX() + velocity.getX();
            double newY = entry.getKey().getY() + velocity.getY();

            // Check boundaries
            if (newX < 0 || newX > L) {
                newX = Math.abs(newX + L) % L; // Wrap around horizontally
            }
            if (newY < 0 || newY > L) {
                newY = Math.abs(newY + L) % L; // Wrap around vertically
            }

            double newTheta = entry.getKey().computeAvgTheta(entry.getValue());
//            + (Math.random() - 0.5) * noise

            result.add(new Particle(newX, newY, entry.getKey().getR(), entry.getKey().getV(), newTheta));
        }
        return result;
    }

    public static void simulate(double L, double Rc, double noise, int steps, List<Particle> particles){
        final var executor = Executors.newFixedThreadPool(12);

        String directoryPath = "src/main/resources/time_slices";
        final File directory = new File(directoryPath);
        if (!directory.exists()) {
            directory.mkdirs();
        } else {
            for (File file : directory.listFiles()) {
                if (file.isFile()) {
                    file.delete();
                }
            }
        }

        for (int i = 0; i < steps; i++) {
            // TODO: make this configurable (could be named step)
            final var animation_step = 5;
            if (i % animation_step == 0) {
                executor.submit(new Writer(i / animation_step, particles));
            }

            Map<Particle, List<Particle>> particles_neighbors = CIM.evaluate(particles, L, Rc); // TODO: L and Rc are hardcoded
            particles = nextFrame(particles_neighbors, L, noise); // TODO por ahora son todas vecinas
        }
    }

    private record Writer(int frame, List<Particle> particles) implements Runnable {
        @Override
        public void run() {
            final var sb = new StringBuilder();
            try (final var writer = new BufferedWriter(
                    new FileWriter("src/main/resources/time_slices/" + frame + ".txt"))) {

                for (final var p : particles) {
                    sb.append(p.getX()).append(" ")
                            .append(p.getY()).append(" ")
                            .append(p.getR()).append(" ")
                            .append(p.getV()).append(" ")
                            .append(p.getTheta()).append("\n");
                }

                writer.write(sb.toString());
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}