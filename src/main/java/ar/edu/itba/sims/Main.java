package ar.edu.itba.sims;

import ar.edu.itba.sims.models.Particle;
import ar.edu.itba.sims.neighbours.CIM;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.Executors;

public class Main {
    public static void main(String[] args) throws IOException {
        InitialConditions ic = InitialStateParser.parse(System.getProperty("input", "initial_conditions.json"),
                InitialConditions.class);

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
        final var interaction = ic.getInteraction();
        simulate(new Simulator(particles, L, Rc, noise, v, resume, steps, interaction), resume > 0);
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
        final var executor = Executors.newFixedThreadPool(3);

        final var directoryPath = "src/main/resources/time_slices";
        preparePath(directoryPath, resume);

        final var iterator = simulator.iterator();

        // Save the initial state
        if (!resume) {
            executor.submit(new Animator(0, simulator.getInitialParticles()));
        }

        final var animation_step = 5;
        // final var progress_step = Math.max(1, steps / 10);
        while (iterator.hasNext()) {
            final var iteration = iterator.next();
            final var i = iteration.step();

            if (i % animation_step == 0) {
                executor.submit(new Animator(i / animation_step, iteration.particles()));
            }

            // if (i % progress_step == 0) {
            //     System.out.println("Progress: " + (i * 100 / steps) + "%");
            // }
        }

        executor.shutdown();
        CIM.shutdown();
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
