package com.neocortex.backend.service.pharmacology;

import com.neocortex.backend.dto.DiseaseDefinition;

public record NeurochemicalState(
        double serotonin,
        double dopamine,
        double noradrenaline,
        double acetylcholine,
        double gaba,
        double glutamate
) {

    private static final double BASELINE = 0.5;
    private static final double DEFICIT_SCALE = 0.3;

    public static NeurochemicalState baselineFor(DiseaseDefinition disease) {
        return new NeurochemicalState(
                BASELINE + disease.getSerotonin_deficit() * DEFICIT_SCALE,
                BASELINE + disease.getDopamine_deficit() * DEFICIT_SCALE,
                BASELINE + disease.getNoradrenaline_deficit() * DEFICIT_SCALE,
                BASELINE + disease.getAcetylcholine_deficit() * DEFICIT_SCALE,
                BASELINE + disease.getGaba_deficit() * DEFICIT_SCALE,
                BASELINE + disease.getGlutamate_deficit() * DEFICIT_SCALE);
    }

    public NeurochemicalState plusScaledEffects(java.util.Map<String, DrugEffect> effects,
                                                DrugEffectCalculator calculator,
                                                double concentration) {
        return new NeurochemicalState(
                serotonin + calculator.effectOn(effects, TargetEffectCatalog.SEROTONIN) * concentration,
                dopamine + calculator.effectOn(effects, TargetEffectCatalog.DOPAMINE) * concentration,
                noradrenaline + calculator.effectOn(effects, TargetEffectCatalog.NORADRENALINE) * concentration,
                acetylcholine + calculator.effectOn(effects, TargetEffectCatalog.ACETYLCHOLINE) * concentration,
                gaba + calculator.effectOn(effects, TargetEffectCatalog.GABA) * concentration,
                glutamate + calculator.effectOn(effects, TargetEffectCatalog.GLUTAMATE) * concentration);
    }

    public NeurochemicalState clipped() {
        return new NeurochemicalState(
                clip(serotonin), clip(dopamine), clip(noradrenaline),
                clip(acetylcholine), clip(gaba), clip(glutamate));
    }

    public double arousal() {
        return (serotonin + dopamine + noradrenaline) / 3.0;
    }

    public double valence() {
        return serotonin * 0.4 + dopamine * 0.6 - noradrenaline * 0.2;
    }

    private static double clip(double value) {
        return Math.max(0, Math.min(1, value));
    }
}
