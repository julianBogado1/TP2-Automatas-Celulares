package ar.edu.itba.sims;

import ar.edu.itba.sims.models.Particle;
import ar.edu.itba.sims.models.Vector;
import ar.edu.itba.sims.neighbours.CIM;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.Executors;

public class Main {
    public static void main(String[] args) throws IOException {
        InitialConditions ic = InitialStateParser.parse("initial_conditions.json", InitialConditions.class);

        final int resume = Integer.valueOf(args.length > 0 ? args[0] : "0");

        List<Particle> particles;
        if (resume > 0) {
            System.out.println("Resuming simulation from step " + resume);
            // Retrieve the particles from the previous animation step
            final var prev = resume / 5 /* Animation step */ - (resume % 5 == 0 ? 1 : 0);
            particles = InitialStateParser.parseParticles(prev);
        } else {
            particles = InitialStateParser.buildInitialState(ic);
        }

        double L = ic.getL();
        double Rc = ic.getR();
        double noise = ic.getNoise();
        int steps = ic.getSteps();
        double v = ic.getV();
        simulate(L, Rc, noise, steps, v, particles, resume);
    }

    public static List<Particle> nextFrame(Map<Particle, List<Particle>> particles_neighbors, double L, double noise,
            double v) {

        List<Particle> result = new ArrayList<>();

        for (Map.Entry<Particle, List<Particle>> entry : particles_neighbors.entrySet()) {
            // ================== POSITION ====================
            Vector velocity = entry.getKey().getVelocity();
            double newX = entry.getKey().getX() + velocity.getX();
            double newY = entry.getKey().getY() + velocity.getY();

            // Check boundaries
            if (newX < 0 || newX > L) {
                newX = Math.abs(newX + L) % L; // Wrap around horizontally
            }
            if (newY < 0 || newY > L) {
                newY = Math.abs(newY + L) % L; // Wrap around vertically
            }

            double newTheta = entry.getKey().computeAvgTheta(entry.getValue()) + (Math.random() - 0.5) * noise;

            result.add(new Particle(newX, newY, entry.getKey().getR(), entry.getKey().getV(), newTheta));
        }
        return result;
    }

    private static void preparePath(String path, boolean preserve) {
        final File directory = new File(path);
        if (!directory.exists()) {
            directory.mkdirs();
        } else if (!preserve) {
            for (File file : directory.listFiles()) {
                if (file.isFile()) {
                    file.delete();
                }
            }
        }
    }

    public static void simulate(double L, double Rc, double noise, int steps, double v, List<Particle> particles, int resume)
            throws IOException {
        final var executor = Executors.newFixedThreadPool(3);

        final var directoryPath = "src/main/resources/time_slices";
        preparePath(directoryPath, resume != 0);

        final var orderPath = "src/main/resources/order_parameter";
        preparePath(orderPath, true);

        final var filename = "%s/N-%d L-%.2f Ruido-%.2f.txt".formatted(orderPath, particles.size(), L, noise);

        // Truncate the file to resume
        try (final var stream = new FileOutputStream(filename, true)) {
            stream.getChannel().truncate(resume * 19L); // Each number is 19 chars long
        } catch (IOException e) {
            System.err.println("Error resuming simulation: " + e.getMessage());
            return;
        }

        final var orderWriter = new BufferedWriter(new FileWriter(filename, true));

        // Resuming with the info from the previous step
        if (resume > 0) {
            final var particles_neighbors = CIM.evaluate(particles, L, Rc);
            particles = nextFrame(particles_neighbors, L, noise, v);
        }

        final var animation_step = 5;
        final var progress_step = steps / 10;
        for (int i = resume; i < steps; i++) {
            if (i % animation_step == 0) {
                executor.submit(new Animator(i / animation_step, v, particles));
            }

            if (i % progress_step == 0) {
                System.out.println("Progress: " + (i * 100 / steps) + "%");
            }

            final var avgVelocity = new Vector(0, 0);
            for (final var p : particles) {
                avgVelocity.add(p.getVelocity());
            }

            final var orden = avgVelocity.getMagnitude() / (particles.size() * v);
            orderWriter.write(String.format(Locale.ROOT, "%.16f\n", orden));

            // If not the last step, calculate the next frame
            if (i + 1 != steps) {
                final var particles_neighbors = CIM.evaluate(particles, L, Rc);
                particles = nextFrame(particles_neighbors, L, noise, v);
            }
        }

        orderWriter.close();
        executor.shutdown();
        CIM.shutdown();
    }

    private record Animator(int frame, double v, List<Particle> particles) implements Runnable {
        @Override
        public void run() {
            final var sb = new StringBuilder();
            final var path = "src/main/resources/time_slices/" + frame + ".txt";

            try (final var writer = new BufferedWriter(new FileWriter(path))) {
                for (final var p : particles) {
                    sb.append(p.getX()).append(" ")
                            .append(p.getY()).append(" ")
                            .append(p.getR()).append(" ")
                            .append(p.getV()).append(" ")
                            .append(p.getTheta()).append("\n");

                    writer.write(sb.toString());
                    sb.setLength(0); // Clear the StringBuilder for the next particle
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
