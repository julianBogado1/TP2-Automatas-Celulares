//Esta clase representa las condiciones iniciales que estan en initial_conditions.JSON

public class InitialConditions {
    private double r;
    private double v;
    private double l;
    private int n;      //amount of particles

    public InitialConditions(double r, double v, double L, int N){
        this.r = r;
        this.v = v;
        this.l = L;
        this.n = N;
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

}
