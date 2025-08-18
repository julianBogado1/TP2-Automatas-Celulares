package ar.edu.itba.sims.models;

import java.util.List;

/**
 * A particle in the simulation.
 *
 * Particles are identified by an auto-incremental ID generated at construction.
 */
public class Particle {
    private static long SERIAL = 0;
    private final long id = SERIAL++;

    private double x;
    private double y;
    private double r;       //el radio de interaccion con otras particulas
    private double v;       //modulo de la velocidad
    private double theta;   //angulo de la velocidad en radianes
    private Vector velocity;
    public Particle(double x, double y, double r, double v, double theta) {
        this.x = x;
        this.y = y;
        this.r = r;
        this.v = v;
        this.theta = theta;
        this.velocity = Vector.fromPolar(v, theta);
    }
    public Particle() {}

    public Particle(double ...args) {
        this(args[0], args[1], args[2], args[3], args[4]);
    }

    public double computeAvgTheta(List<Particle> particles) {
        double sumSin = 0.0;
        double sumCos = 0.0;
        for (Particle p : particles) {
            sumSin += Math.sin(p.getTheta());
            sumCos += Math.cos(p.getTheta());
        }
        return Math.atan2(sumSin/ particles.size(), sumCos/particles.size());
    }

    /**
     * Calculates the squared distance to another particle.
     * 
     * @apiNote This method does not take into account the radius.
     * @apiNote This method does not take into account periodic boundary conditions.
     *
     * @param other the other particle
     * @return the distance to the other particle
     */
    public double sqrdDistance(Particle other) {
        final var dx = x - other.x;
        final var dy = y - other.y;
        return dx * dx + dy * dy;
    }

    /**
     * Calculates the squared distance to another particle.
     *
     * @apiNote This method does not take into account the radius.
     *
     * @param other the other particle
     * @param L     Length of the simulation box
     * @return the distance to the other particle
     */
    public double sqrdDistance(Particle other, double L) {
        var dx = Math.abs(x - other.x);
        var dy = Math.abs(y - other.y);

        if (dx > L / 2) {
            dx -= L;
        }

        if (dy > L / 2) {
            dy -= L;
        }

        return dx * dx + dy * dy;
    }

    /**
     * Calculates the distance to another particle.
     * 
     * @apiNote This method does not take into account the radius.
     * @apiNote This method does not take into account periodic boundary conditions.
     *
     * @param other the other particle
     * @return the distance to the other particle
     */
    public double distance(Particle other) {
        return Math.sqrt(sqrdDistance(other));
    }

    /**
     * Calculates the distance to another particle.
     * 
     * @apiNote This method does not take into account the radius.
     *
     * @param other the other particle
     * @param L     Length of the simulation box
     * @return the distance to the other particle
     */
    public double distance(Particle other, double L) {
        return Math.sqrt(sqrdDistance(other, L));
    }

    /**
     * @return the ID of the particle
     */
    public long getId() {
        return id;
    }

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
    public Vector getVelocity() {
        return velocity;
    }
    public void setVelocity(Vector velocity) {
        this.velocity = velocity;
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

    @Override
    public int hashCode() {
        return Long.hashCode(id);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;

        if (obj == null)
            return false;

        if (!(obj instanceof Particle other))
            return false;

        return id == other.id;
    }
}
