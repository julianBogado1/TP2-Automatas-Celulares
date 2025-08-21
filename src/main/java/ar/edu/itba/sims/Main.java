package ar.edu.itba.sims;

import ar.edu.itba.sims.models.Particle;
import ar.edu.itba.sims.neighbours.CIM;
import me.tongfei.progressbar.ProgressBar;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.Executors;

public class Main {
    public static void main(String[] args) throws IOException {
        final var ic = InitialStateParser.parse(System.getProperty("input", "initial_conditions.json"));
        final int resume = Integer.valueOf(args.length > 0 ? args[0] : "0");

        final List<Particle> particles;
        final Simulator simulator;

        if (resume > 0) {
            System.out.println("Resuming simulation from step " + resume);
            // Retrieve the particles from the previous animation step
            final var prev = resume / 5 /* Animation step */ - (resume % 5 == 0 ? 1 : 0);
            particles = InitialStateParser.parseParticles(prev);

            simulator = new Simulator(particles, ic, resume);
        } else {
            particles = InitialStateParser.buildInitialState(ic);
            simulator = new Simulator(particles, ic);
        }

        simulate(simulator, resume > 0);
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

    public static void simulate(final Simulator simulator, final boolean resume) throws IOException {
        final var animation_step = 5;
        final var directoryPath = "src/main/resources/time_slices";

        try (final var executor = Executors.newFixedThreadPool(3);
                final var pb = new ProgressBar("Simulating", simulator.getSteps())) {
            final var iterator = simulator.iterator();

            preparePath(directoryPath, resume);

            if (!resume) {
                executor.submit(new Animator(0, simulator.getInitialState()));
            } else if (iterator.hasNext()) {
                // Skip the first iteration if resuming
                iterator.next();
            }

            while (iterator.hasNext()) {
                final var iteration = iterator.next();
                final var i = iteration.step();

                if (i % animation_step == 0) {
                    executor.submit(new Animator(i / animation_step, iteration.particles()));
                }

                pb.stepTo(i);
            }
        } finally {
            CIM.shutdown();
        }
    }

    private record Animator(int frame, List<Particle> particles) implements Runnable {
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
