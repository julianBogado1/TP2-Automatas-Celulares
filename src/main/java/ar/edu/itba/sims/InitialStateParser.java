package ar.edu.itba.sims;

import com.fasterxml.jackson.databind.ObjectMapper;
import ar.edu.itba.sims.models.Particle;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

//En esta clase se proveen utilidades para:
//      construir un estado inicial a partir de parametros (output JSON)
//      parsear un estado inicial desde un archivo JSON

public class InitialStateParser {
    public static InitialConditions parse(String resourceName) {
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            return objectMapper.readValue(
                    new File("src/main/resources/" + resourceName),
                    InitialConditions.class
            );
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public static List<Particle> buildInitialState(InitialConditions ic){
        List<Particle> particles = new ArrayList<>();
        for(int i = 0; i < ic.getN(); i++){
            particles.add(new Particle(
                Math.random() * ic.getL(), //x
                Math.random() * ic.getL(), //y
                ic.getR(),                 //r
                ic.getV(),                 //v
                Math.random() * 2 * Math.PI //theta
            ));
        }

        return particles;
    }

    public static List<Particle> parseParticles(int step) throws IOException {
        final var particles = new ArrayList<Particle>();
    
        try (final var br = new BufferedReader(new FileReader("src/main/resources/time_slices/" + step + ".txt"))) {
            String line;
            while ((line = br.readLine()) != null) {
                final var tokens = line.trim().split("\\s+");
                final var values = new double[tokens.length];
    
                for (int i = 0; i < tokens.length; i++) {
                    values[i] = Double.parseDouble(tokens[i]);
                }
    
                particles.add(new Particle(values));
            }
        }
    
        return particles;
    }
}
