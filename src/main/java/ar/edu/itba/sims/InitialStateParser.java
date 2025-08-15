package ar.edu.itba.sims;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import ar.edu.itba.sims.models.Particle;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

//En esta clase se proveen utilidades para:
//      construir un estado inicial a partir de parametros (output JSON)
//      parsear un estado inicial desde un archivo JSON

public class InitialStateParser {
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


    public static List<Particle> parseParticles(String resourceName) {
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            return objectMapper.readValue(
                    new File("src/main/resources/" + resourceName),
                    new TypeReference<List<Particle>>() {}
            );
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }


}
