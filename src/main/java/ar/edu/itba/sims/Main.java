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

public class Main {

    static Vector avgVelocity = new Vector(0, 0);
    static double orden = 0;


    public static void main(String[] args) throws IOException {

        InitialConditions ic = InitialStateParser.parse("initial_conditions.json", InitialConditions.class);
        List<Particle> particles = InitialStateParser.buildInitialState(ic);

        double L = ic.getL();
        double Rc = ic.getR();
        double noise = ic.getNoise();
        int steps = ic.getSteps();
        double v = ic.getV();
        simulate(L, Rc, noise, steps, v, particles);

    }

    public static List<Particle> nextFrame(Map<Particle, List<Particle>> particles_neighbors, double L, double noise, double v) {

        List<Particle> result = new ArrayList<>();
        


        for (Map.Entry<Particle, List<Particle>> entry : particles_neighbors.entrySet()) {
            
            //================== POSITION ====================
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

            double newTheta = entry.getKey().computeAvgTheta(entry.getValue())+ (Math.random() - 0.5) * noise;

            result.add(new Particle(newX, newY, entry.getKey().getR(), entry.getKey().getV(), newTheta));
            
        }

        double avgMagnitude = avgVelocity.getMagnitude() / (particles_neighbors.size() * v);
        return result;
    }


    private static void preparePath(String path){
        final File directory = new File(path);
        if (!directory.exists()) {
            directory.mkdirs();
        } else {
            for (File file : directory.listFiles()) {
                if (file.isFile()) {
                    file.delete();
                }
            }
        }
    }

    public static void simulate(double L, double Rc, double noise, int steps, double v, List<Particle> particles) throws IOException {
        String directoryPath = "src/main/resources/time_slices";
        preparePath(directoryPath);

        String orderPath = "src/main/resources/order_parameter";
        preparePath(orderPath);

        StringBuilder orderBuilder = new StringBuilder();
        BufferedWriter orderWriter = new BufferedWriter(new FileWriter( orderPath+"/order_parameter.txt"));

        for (int i = 0; i < steps; i++) {

            final var animation_step = 5;
            if (i % animation_step == 0) {
                StringBuilder sb = new StringBuilder();
                BufferedWriter writer = new BufferedWriter(
                        new FileWriter(directoryPath + "/" + i / animation_step + ".txt"));

                    for (Particle p : particles) {

                        //================= OUTPUT ===================
                        sb.append(p.getX()).append(" ")
                                .append(p.getY()).append(" ")
                                .append(p.getR()).append(" ")
                                .append(p.getV()).append(" ")
                                .append(p.getTheta()).append("\n");


                        //================= ORDER PARAMETER ===================
                        avgVelocity.add(p.getVelocity());
                    }

                    //================= ORDER PARAMETER ===================
                    orden = avgVelocity.getMagnitude() / (particles.size() * v);
                    orderBuilder.append(orden+"\n");
                    avgVelocity = new Vector(0, 0); // reset for next iteration

                    writer.write(sb.toString());
            }
            Map<Particle, List<Particle>> particles_neighbors = CIM.evaluate(particles, L, Rc); // TODO: L and Rc are hardcoded
            particles = nextFrame(particles_neighbors, L, noise,v); // TODO por ahora son todas vecinas
        }

        orderWriter.write(orderBuilder.toString());
        orderWriter.close();
        

    }

}