package ar.edu.itba.sims;

import ar.edu.itba.sims.models.Particle;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Locale;

public class Inciso1c {
    // Reduced parameter scope for faster execution
    private static final double[] ETA_VALUES = {0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0};
    private static final double[] RHO_VALUES = {0.5, 1.0, 2.0, 3.0, 4.0, 5.0};
    private static final int RUNS_PER_PARAMETER = 5;
    
    private static final double FIXED_L = 20.0;  // Reduced from 20.0
    private static final double FIXED_R = 1.0;
    private static final double FIXED_V = 0.03;
    private static final int FIXED_STEPS = 1000;   // Reduced from 1000
    
    public static void main(String[] args) throws IOException {
        System.out.println("Starting parameter sweep study...");
        
        preparePath("results");
        preparePath("results/eta_study/configs");
        preparePath("results/eta_study/raw_data");
        preparePath("results/rho_study/configs");
        preparePath("results/rho_study/raw_data");
        
        runEtaStudy();
        runRhoStudy();
        
        // Shutdown CIM executor after all simulations
        ar.edu.itba.sims.neighbours.CIM.shutdown();
        
        System.out.println("Parameter sweep study completed!");
    }
    
    private static void runEtaStudy() throws IOException {
        System.out.println("Running η (noise) study...");
        double fixedRho = 2.0;
        int fixedN = (int)(fixedRho * FIXED_L * FIXED_L);
        
        for (double eta : ETA_VALUES) {
            System.out.printf("Processing η = %.1f\n", eta);
            
            for (int run = 1; run <= RUNS_PER_PARAMETER; run++) {
                String configName = String.format(Locale.ROOT, "eta_%.1f_run_%d", eta, run);
                InitialConditions config = new InitialConditions(
                    FIXED_R, FIXED_V, FIXED_L, fixedN, eta, FIXED_STEPS
                );
                
                String configPath = "results/eta_study/configs/" + configName + ".json";
                saveConfig(config, configPath);
                
                List<Particle> particles = InitialStateParser.buildInitialState(config);
                
                String outputDir = "results/eta_study/raw_data/" + configName;
                preparePath(outputDir);
                preparePath(outputDir + "/order_parameter");
                
                runSingleSimulation(config, particles, outputDir);
            }
        }
    }
    
    private static void runRhoStudy() throws IOException {
        System.out.println("Running ρ (density) study...");
        double fixedEta = 1.0;
        
        for (double rho : RHO_VALUES) {
            System.out.printf("Processing ρ = %.1f\n", rho);
            int n = (int)(rho * FIXED_L * FIXED_L);
            
            for (int run = 1; run <= RUNS_PER_PARAMETER; run++) {
                String configName = String.format(Locale.ROOT, "rho_%.1f_run_%d", rho, run);
                InitialConditions config = new InitialConditions(
                    FIXED_R, FIXED_V, FIXED_L, n, fixedEta, FIXED_STEPS
                );
                
                String configPath = "results/rho_study/configs/" + configName + ".json";
                saveConfig(config, configPath);
                
                List<Particle> particles = InitialStateParser.buildInitialState(config);
                
                String outputDir = "results/rho_study/raw_data/" + configName;
                preparePath(outputDir);
                preparePath(outputDir + "/order_parameter");
                
                runSingleSimulation(config, particles, outputDir);
            }
        }
    }
    
    private static void runSingleSimulation(InitialConditions config, List<Particle> particles, String outputDir) throws IOException {        
        Main.simulate(config.getL(), config.getR(), config.getNoise(), config.getSteps(), config.getV(), particles, 0);
    }
    
    private static void saveConfig(InitialConditions config, String path) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        mapper.writeValue(new File(path), config);
    }
    
    private static void preparePath(String path) {
        File directory = new File(path);
        if (!directory.exists()) {
            directory.mkdirs();
        }
    }
}
