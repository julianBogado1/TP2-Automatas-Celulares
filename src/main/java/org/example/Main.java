package org.example;

import org.example.models.Particle;
import org.example.models.Vector;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        InitialStateParser.buildInitialState();

        List<Particle> particles = InitialStateParser.parseParticles("particles_t0.json");

        for(int i=1; i < 11; i++) {

            StringBuilder sb = new StringBuilder();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter("src/main/resources/time_slices/"+i+"txt"))) {

                for(Particle p : particles) {
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

            particles = nextFrame(particles, particles);    // por ahora son todas vecinas
        }




    }

    public static List<Particle> nextFrame(List<Particle> particles, List<Particle> neighbors) {

        List<Particle> result = new ArrayList<>();

        for(Particle p : particles) {
            //POSITION
            Vector velocity = Vector.fromPolar(p.getV(), Math.toRadians(p.getTheta()));
            double newX = p.getX() + velocity.getX();
            double newY = p.getY() + velocity.getY();

            //Check boundaries
            //TODO this L is fixed currently
            double L = 100.0;
            if (newX < 0 || newX > L) {
                newX = (newX + L) % L; // Wrap around horizontally
            }
            if (newY < 0 || newY > L) {
                newY = (newY + L) % L; // Wrap around vertically
            }

            double noise = 2L; //noise amplitude
            double newTheta = p.computeAvgTheta(neighbors) + (Math.random() - 0.5) * noise;

            result.add(new Particle(newX, newY, p.getR(), p.getV(), newTheta));
        }
        return result;
    }

}