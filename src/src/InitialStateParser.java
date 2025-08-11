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

    public static <T> T parse(String resourceName) {
        ObjectMapper objectMapper = new ObjectMapper();
        try{
            T myObj = objectMapper.readValue(
                new File("src/src/main/resources/" + resourceName),
                new TypeReference<T>() {}
            );
            return myObj;
        }catch(Exception e){
            e.printStackTrace();
            return null;
        }

    }

    public static void buildInitialState(){
        InitialConditions ic = parse("initial_conditions.json");
        //generate a list of particles with random x, y, theta
    }
}
