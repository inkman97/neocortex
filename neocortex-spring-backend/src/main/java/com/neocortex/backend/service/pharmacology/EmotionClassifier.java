package com.neocortex.backend.service.pharmacology;

public final class EmotionClassifier {

    private static final double HIGH_AROUSAL = 0.6;
    private static final double LOW_AROUSAL = 0.4;

    private EmotionClassifier() {
    }

    public static String classify(double valence, double arousal) {
        if (arousal > HIGH_AROUSAL) {
            return valence > 0 ? "excited" : "anxious";
        }
        if (arousal < LOW_AROUSAL) {
            return valence > 0 ? "content" : "sad";
        }
        return valence > 0 ? "happy" : "neutral";
    }
}
