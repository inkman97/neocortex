package com.neocortex.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Single timepoint in a trial with neurochemical AND physiological data.
 *
 * Updated to include 8 physiological parameters:
 * - Heart rate, respiratory rate, skin conductance, muscle tension
 * - Gut feeling, temperature, pain, fatigue
 *
 * All physiological values are normalized 0-1 for consistency.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TrialTimepoint {

    // ============================================================
    // TIME
    // ============================================================
    private double hours;
    private double days;
    private String phase;  // "baseline" or "treatment"

    // ============================================================
    // PHARMACOLOGY
    // ============================================================
    private double drug_concentration;  // Percentage (0-100)
    private Map<String, Double> metabolite_concentrations;

    // ============================================================
    // NEUROCHEMISTRY (0-1 normalized)
    // ============================================================
    private double serotonin;
    private double dopamine;
    private double noradrenaline;
    private double acetylcholine;
    private double gaba;
    private double glutamate;

    // ============================================================
    // PSYCHOLOGICAL STATE
    // ============================================================
    private double arousal;           // 0-1 (activation level)
    private double valence;           // -1 to +1 (negative to positive emotion)
    private double firing_rate;       // Average Hz
    private String dominant_emotion;  // "happy", "sad", "anxious", etc.

    // ============================================================
    // PHYSIOLOGICAL PARAMETERS (NEW!)
    // All normalized 0-1 scale
    // ============================================================

    /**
     * Heart rate (0-1 normalized)
     * - 0.0-0.4: Bradycardia (slow heart rate)
     * - 0.4-0.6: Normal (60-100 bpm)
     * - 0.6-1.0: Tachycardia (elevated heart rate)
     *
     * Clinical relevance: Many drugs affect heart rate
     * (stimulants increase, beta-blockers decrease)
     */
    private double heart_rate;

    /**
     * Respiratory rate (0-1 normalized)
     * - 0.0-0.4: Slow breathing
     * - 0.4-0.6: Normal (12-20 breaths/min)
     * - 0.6-1.0: Hyperventilation
     *
     * Clinical relevance: Anxiety increases, sedatives decrease
     */
    private double respiratory_rate;

    /**
     * Skin conductance (0-1 normalized)
     * Measures arousal/stress through sweat gland activity
     * - 0.0-0.3: Low arousal (calm)
     * - 0.3-0.6: Moderate arousal
     * - 0.6-1.0: High arousal/stress
     *
     * Clinical relevance: Anxiety marker, SSRI initial activation
     */
    private double skin_conductance;

    /**
     * Muscle tension (0-1 normalized)
     * - 0.0-0.4: Relaxed
     * - 0.4-0.6: Normal tone
     * - 0.6-1.0: Tense/rigid
     *
     * Clinical relevance: Anxiety, Parkinson's rigidity,
     * anxiolytic efficacy marker
     */
    private double muscle_tension;

    /**
     * Gut feeling (0-1 normalized)
     * Visceral sensation quality
     * - 0.0-0.4: Discomfort/nausea
     * - 0.4-0.6: Neutral
     * - 0.6-1.0: Comfort/wellbeing
     *
     * Clinical relevance: Antidepressant efficacy,
     * GI side effects, somatic anxiety
     */
    private double gut_feeling;

    /**
     * Temperature sensation (0-1 normalized)
     * - 0.0-0.4: Cold sensation
     * - 0.4-0.6: Normal
     * - 0.6-1.0: Hot sensation/fever
     *
     * Clinical relevance: Withdrawal symptoms, infection,
     * thyroid medication effects
     */
    private double temperature;

    /**
     * Pain level (0-1 normalized)
     * - 0.0-0.2: No pain
     * - 0.2-0.5: Mild pain
     * - 0.5-0.8: Moderate pain
     * - 0.8-1.0: Severe pain
     *
     * Clinical relevance: Depression often presents with pain,
     * analgesic efficacy, psychosomatic symptoms
     */
    private double pain;

    /**
     * Fatigue level (0-1 normalized)
     * - 0.0-0.3: Energetic
     * - 0.3-0.6: Normal energy
     * - 0.6-1.0: Exhausted
     *
     * Clinical relevance: Major depression symptom,
     * early antidepressant response marker,
     * stimulant vs sedative effects
     */
    private double fatigue;
}