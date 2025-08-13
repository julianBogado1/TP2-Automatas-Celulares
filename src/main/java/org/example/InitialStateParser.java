package org.example;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.Gson;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

//En esta clase se proveen utilidades para:
//      construir un estado inicial a partir de parametros (output JSON)
//      parsear un estado inicial desde un archivo JSON


public class InitialStateParser {
    private static final Gson gson = new Gson();

    public static <T> T parse(String resourceName, Class<T> clazz) {
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            return objectMapper.readValue(
                    new File("src/main/resources/" + resourceName),
                    clazz
            );
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public static void buildInitialState(){
        InitialConditions ic = InitialStateParser.parse("initial_conditions.json", InitialConditions.class);

        //generate a list of particles with random x, y, theta
        List<Particle> particles = new ArrayList<>();
        for(int i = 0; i < ic.getN(); i++){
            particles.add(new Particle(
                Math.random() * ic.getL(), //x
                Math.random() * ic.getL(), //y
                ic.getR(),                 //r
                ic.getV(),                 //v
                Math.random() * 360 //theta
            ));
        }

        //convert the list of particles to JSON
        String json = gson.toJson(particles);
        //write the JSON to a file
        try {
            File file = new File("src/main/resources/particles_t0.json");
            file.createNewFile();
            java.nio.file.Files.writeString(file.toPath(), json);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
