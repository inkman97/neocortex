package com.neocortex.backend.service.pharmacology;

public record PhysiologicalState(
        double heartRate,
        double respiratoryRate,
        double skinConductance,
        double muscleTension,
        double gutFeeling,
        double temperature,
        double pain,
        double fatigue
) {

    public static PhysiologicalState from(NeurochemicalState nt, double arousal, double valence) {
        double heartRate = clamp(0.5 + nt.noradrenaline() * 0.3 + arousal * 0.2 - nt.serotonin() * 0.1, 0.2, 0.9);
        double respiratoryRate = clamp(heartRate * 0.9 + arousal * 0.15, 0.3, 0.8);
        double skinConductance = clamp(arousal * 0.7 + Math.abs(valence) * 0.2, 0.1, 0.9);
        double muscleTension = clamp(0.35 + arousal * 0.25 - nt.dopamine() * 0.15, 0.2, 0.9);
        double gutFeeling = clamp(0.5 + valence * 0.35 + nt.serotonin() * 0.15, 0.2, 0.9);
        double temperature = clamp(0.5 + arousal * 0.08, 0.4, 0.6);
        double pain = clamp(0.0 - valence * 0.15 - nt.serotonin() * 0.1, 0.0, 0.8);
        double fatigue = clamp(0.35 - nt.dopamine() * 0.3 - nt.serotonin() * 0.2 + arousal * 0.05, 0.1, 0.95);

        return new PhysiologicalState(
                heartRate, respiratoryRate, skinConductance, muscleTension,
                gutFeeling, temperature, pain, fatigue);
    }

    private static double clamp(double value, double min, double max) {
        return Math.max(min, Math.min(max, value));
    }
}
