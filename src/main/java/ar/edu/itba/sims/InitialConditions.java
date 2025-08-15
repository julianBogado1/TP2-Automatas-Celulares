package ar.edu.itba.sims;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

//Esta clase representa las condiciones iniciales que estan en initial_conditions.JSON

@JsonIgnoreProperties(ignoreUnknown = true)
public class InitialConditions {
    private double r;
    private double v;
    private double l;
    private int n;      //amount of particles
    private double noise;
    private int steps;

    public InitialConditions(double r, double v, double L, int N, double noise, int steps) {
        this.r = r;
        this.v = v;
        this.l = L;
        this.n = N;
        this.noise = noise;
        this.steps = steps;
    }
    public InitialConditions() {}

    public double getR() {
        return r;
    }
    public void setR(double r) {
        this.r = r;

    }
    public double getV() {
        return v;
    }
    public void setV(double v) {
        this.v = v;
    }
    public double getL() {
        return l;
    }
    public void setL(double L) {
        this.l = L;
    }
    public int getN() {
        return n;
    }
    public void setN(int N) {
        this.n = N;
    }
    public double getNoise() {
        return noise;
    }
    public void setNoise(double noise) {
        this.noise = noise;
    }
    public int getSteps(){return steps;}
    public void setSteps(int steps){this.steps=steps;}

}
