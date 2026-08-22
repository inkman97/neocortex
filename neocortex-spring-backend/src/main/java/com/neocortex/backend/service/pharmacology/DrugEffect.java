package com.neocortex.backend.service.pharmacology;

public class DrugEffect {

    private final double maxEffect;
    private final double hill;
    private final double doseEffect;

    public DrugEffect(double maxEffect, double hill, double doseEffect) {
        this.maxEffect = maxEffect;
        this.hill = hill;
        this.doseEffect = doseEffect;
    }

    public double getMaxEffect() {
        return maxEffect;
    }

    public double getHill() {
        return hill;
    }

    public double getDoseEffect() {
        return doseEffect;
    }

    public DrugEffect combinedWith(DrugEffect other, double hill) {
        return new DrugEffect(maxEffect + other.maxEffect, hill, doseEffect + other.doseEffect);
    }
}
