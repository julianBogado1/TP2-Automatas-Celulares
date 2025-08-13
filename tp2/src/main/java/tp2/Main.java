package tp2;

import com.fasterxml.jackson.core.type.TypeReference;

import java.util.List;

public class Main {
    public static void main(String[] args) {
        System.out.println("I Declare this backend a JAVA backend");

        List<Particle> particles =
                InitialStateParser.parse("particles_t0.json", List.class);

        System.out.println(particles);

        InitialStateParser.buildInitialState();

    }
}
