package ar.edu.itba.sims.models;

public class Vector {
    private double x;
    private double y;

    public Vector(double x, double y) {
        this.x = x;
        this.y = y;
    }
    public Vector() {}

    public static Vector fromPolar(double magnitude, double angle) {
        return new Vector(magnitude * Math.cos(angle), magnitude * Math.sin(angle));
    }

    public double getMagnitude() {
        return Math.sqrt(x * x + y * y);
    }
    public double getAngle() {
        return Math.atan2(y, x);
    }
    public void add(Vector other) {
        this.x += other.x;
        this.y += other.y;
    }
    public double getX() {
        return x;
    }
    public double getY() {
        return y;
    }
}
