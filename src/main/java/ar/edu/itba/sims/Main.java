package ar.edu.itba.sims;

import ar.edu.itba.sims.models.Particle;
import ar.edu.itba.sims.models.Vector;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        InitialStateParser.buildInitialState();

        List<Particle> particles = InitialStateParser.parseParticles("particles_t0.json");

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

        for (int i = 0; i < 150; i++) {
            // Only generate output every 1000 iterations
            // TODO: make this configurable (could be named step)
            final var animation_step = 5;
            if (i % animation_step == 0) {
                StringBuilder sb = new StringBuilder();
                try (BufferedWriter writer = new BufferedWriter(
                        new FileWriter(directoryPath + "/" + i / animation_step + ".txt"))) {

                    for (Particle p : particles) {
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

            particles = nextFrame(particles, particles); // TODO por ahora son todas vecinas
        }

    }

    public static List<Particle> nextFrame(List<Particle> particles, List<Particle> neighbors) {

        List<Particle> result = new ArrayList<>();

        for (Particle p : particles) {
            // POSITION
            Vector velocity = Vector.fromPolar(p.getV(), Math.toRadians(p.getTheta()));
            double newX = p.getX() + velocity.getX();
            double newY = p.getY() + velocity.getY();

            // Check boundaries
            // TODO this L is fixed currently
            double L = 100.0;
            if (newX < 0 || newX > L) {
                newX = (newX + L) % L; // Wrap around horizontally
            }
            if (newY < 0 || newY > L) {
                newY = (newY + L) % L; // Wrap around vertically
            }

            double noise = 2L; // noise amplitude
            double newTheta = p.computeAvgTheta(neighbors) + (Math.random() - 0.5) * noise;
            System.out.println("Old theta: " + p.getTheta() + ", New theta: " + newTheta);

            result.add(new Particle(newX, newY, p.getR(), p.getV(), newTheta));
        }
        return result;
    }

}