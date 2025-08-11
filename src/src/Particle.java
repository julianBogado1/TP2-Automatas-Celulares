public class Particle {
    private double x;
    private double y;
    private double r;       //el radio de interaccion con otras particulas
    private double v;       //modulo de la velocidad
    private double theta;   //angulo de la velocidad
    public Particle(double x, double y, double r, double v, double theta) {
        this.x = x;
        this.y = y;
        this.r = r;
        this.v = v;
        this.theta = theta;
    }
    public Particle() {}

    public double getX() {
        return x;
    }
    public void setX(double x) {
        this.x = x;
    }
    public double getY() {
        return y;
    }
    public void setY(double y) {
        this.y = y;
    }
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
    public double getTheta() {
        return theta;
    }
    public void setTheta(double theta) {
        this.theta = theta;
    }
    @Override
    public String toString() {
        return "Particle{" +
                "x=" + x +
                ", y=" + y +
                ", r=" + r +
                ", v=" + v +
                ", theta=" + theta +
                '}';
    }
}
