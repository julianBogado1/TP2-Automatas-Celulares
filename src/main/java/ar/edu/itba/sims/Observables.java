package ar.edu.itba.sims;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.Locale;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import ar.edu.itba.sims.models.Vector;

public class Observables {
    public static void main(String[] args) {
        final var folder = new File("src/main/resources/time_slices");

        if (!folder.exists() || !folder.isDirectory()) {
            System.err.println("time_slices does not exist or is not a directory.");
            return;
        }

        final var files = folder.listFiles((dir, name) -> name.endsWith(".txt"));
        if (files == null || files.length == 0) {
            System.err.println("No files found in time_slices directory.");
            return;
        }

        new Observables(args[0]).observe(files);
    }

    private final Observer observer;

    private Observables(final String observe) {
        observer = switch (observe) {
            case "v_a" -> this::v_a;
            default -> throw new IllegalArgumentException("Unknown observable: " + observe);
        };
    }

    private void observe(final File[] files) {
        final var executor = Executors.newFixedThreadPool(12);
        try {
            observer.observe(executor, files);
        } finally {
            executor.shutdown();
        }
    }

    private void v_a(final ExecutorService executor, final File[] files) {
        final var ic = InitialStateParser.parse("initial_conditions.json");
        final var v = ic.getV();

        final var output = new ConcurrentHashMap<Integer, Double>(files.length + 1, 1.0f);

        final var latch = new CountDownLatch(files.length);
        for (final var file : files) {
            if (file.isFile()) {
                executor.submit(() -> {
                    try {
                        final var step = Integer.parseInt(file.getName().replace(".txt", ""));
                        final var particles = InitialStateParser.parseParticles(step);

                        final var avg = new Vector(0, 0);
                        for (final var p : particles) {
                            avg.add(p.getVelocity());
                        }

                        final var orden = avg.getMagnitude() / (particles.size() * v);
                        output.put(step, orden);
                    } catch (Exception e) {
                        e.printStackTrace();
                    } finally {
                        latch.countDown();
                    }
                });
            }
        }

        final var folder = "src/main/resources/order_parameter/";
        final var directory = new File(folder);
        if (!directory.exists()) {
            directory.mkdirs();
        }

        final var filename = "%s N-%d L-%.2f Ruido-%.2f.txt".formatted(ic.getInteraction(), ic.getN(), ic.getL(), ic.getNoise());
        try (final var writer = new BufferedWriter(new FileWriter(Paths.get(folder, filename).toString()))) {
            latch.await();

            for (int i = 0; i < files.length; i++) {
                writer.write(String.format(Locale.ROOT, "%.16f\n", output.get(i)));
            }
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            throw new RuntimeException(e);
        }

        System.out.println("Order parameter written to \"" + filename + '"');
    }

    private interface Observer {
        void observe(final ExecutorService executor, final File[] file);
    }
}
