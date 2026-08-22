package com.neocortex.backend.service;

import org.springframework.stereotype.Component;

import java.util.*;

/**
 * Complete Disease Library - All 6 Neurotransmitters Active
 *
 * ACTIVE NEUROTRANSMITTERS (6):
 * - Serotonin (5HT)
 * - Dopamine (DA)
 * - Noradrenaline (NE)
 * - Acetylcholine (ACh)
 * - GABA (inhibitory)
 * - Glutamate (excitatory)
 *
 * UNIFIED CONVENTION:
 * POSITIVE = DEFICIT (low neurotransmitter)
 * NEGATIVE = EXCESS (high neurotransmitter)
 *
 * All physiological parameters emerge from NT coupling.
 */
@Component
public class KnownDiseasesLibrary {

    private static final Map<String, Object> LIBRARY = buildLibrary();

    public Map<String, Object> getDiseases() {
        return LIBRARY;
    }

    private static Map<String, Object> buildLibrary() {
        Map<String, Object> library = new LinkedHashMap<>();

        library.put("depression", Map.of(
                "id", "depression",
                "name", "Major Depressive Disorder",
                "category", "mood",
                "profile", Map.of(
                        "serotonin", 0.40,
                        "dopamine", 0.30,
                        "noradrenaline", 0.25,
                        "acetylcholine", 0.0,
                        "gaba", 0.0,
                        "glutamate", 0.0
                ),
                "description", "Persistent sadness, anhedonia, psychomotor changes",
                "symptoms", List.of("Depressed mood", "Anhedonia", "Fatigue", "Psychomotor retardation")
        ));

        library.put("dysthymia", Map.of(
                "id", "dysthymia",
                "name", "Persistent Depressive Disorder",
                "category", "mood",
                "profile", Map.of(
                        "serotonin", 0.25,
                        "dopamine", 0.20,
                        "noradrenaline", 0.15,
                        "acetylcholine", 0.0,
                        "gaba", 0.0,
                        "glutamate", 0.0
                ),
                "description", "Chronic low-grade depression lasting 2+ years",
                "symptoms", List.of("Persistent low mood", "Low energy", "Poor concentration")
        ));

        library.put("bipolar_depression", Map.of(
                "id", "bipolar_depression",
                "name", "Bipolar Disorder - Depressive Phase",
                "category", "mood",
                "profile", Map.of(
                        "serotonin", 0.45,
                        "dopamine", 0.40,
                        "noradrenaline", 0.30,
                        "acetylcholine", 0.0,
                        "gaba", 0.0,
                        "glutamate", 0.0
                ),
                "description", "Severe depressive episodes in bipolar disorder",
                "symptoms", List.of("Severe depression", "Hypersomnia", "Psychomotor retardation")
        ));

        library.put("generalized_anxiety", Map.of(
                "id", "generalized_anxiety",
                "name", "Generalized Anxiety Disorder",
                "category", "anxiety",
                "profile", Map.of(
                        "serotonin", 0.30,
                        "dopamine", 0.10,
                        "noradrenaline", -0.35,  // EXCESS
                        "acetylcholine", 0.0,
                        "gaba", 0.25,             // DEFICIT
                        "glutamate", -0.15        // EXCESS
                ),
                "description", "Excessive worry, autonomic hyperarousal, GABAergic dysfunction",
                "symptoms", List.of("Excessive worry", "Restlessness", "Muscle tension", "Fatigue")
        ));

        library.put("panic_disorder", Map.of(
                "id", "panic_disorder",
                "name", "Panic Disorder",
                "category", "anxiety",
                "profile", Map.of(
                        "serotonin", 0.35,
                        "dopamine", 0.05,
                        "noradrenaline", -0.50,  // EXCESS
                        "acetylcholine", 0.0,
                        "gaba", 0.30,             // DEFICIT
                        "glutamate", -0.20        // EXCESS
                ),
                "description", "Recurrent panic attacks with acute autonomic symptoms",
                "symptoms", List.of("Panic attacks", "Palpitations", "Hyperventilation", "Fear of dying")
        ));

        library.put("social_anxiety", Map.of(
                "id", "social_anxiety",
                "name", "Social Anxiety Disorder",
                "category", "anxiety",
                "profile", Map.of(
                        "serotonin", 0.35,
                        "dopamine", 0.15,
                        "noradrenaline", -0.30,  // EXCESS
                        "acetylcholine", 0.0,
                        "gaba", 0.20,             // DEFICIT
                        "glutamate", -0.10        // EXCESS
                ),
                "description", "Intense fear of social situations and negative evaluation",
                "symptoms", List.of("Social fear", "Avoidance", "Blushing", "Trembling")
        ));

        library.put("ocd", Map.of(
                "id", "ocd",
                "name", "Obsessive-Compulsive Disorder",
                "category", "anxiety",
                "profile", Map.of(
                        "serotonin", 0.50,
                        "dopamine", -0.15,       // EXCESS
                        "noradrenaline", -0.20,  // EXCESS
                        "acetylcholine", 0.0,
                        "gaba", 0.15,             // DEFICIT
                        "glutamate", -0.10        // EXCESS
                ),
                "description", "Intrusive obsessions and compulsive rituals",
                "symptoms", List.of("Intrusive thoughts", "Compulsive rituals", "Anxiety", "Doubt")
        ));

        library.put("ptsd", Map.of(
                "id", "ptsd",
                "name", "Post-Traumatic Stress Disorder",
                "category", "anxiety",
                "profile", Map.of(
                        "serotonin", 0.40,
                        "dopamine", 0.20,
                        "noradrenaline", -0.45,  // EXCESS
                        "acetylcholine", 0.0,
                        "gaba", 0.25,             // DEFICIT
                        "glutamate", -0.15        // EXCESS
                ),
                "description", "Trauma-related disorder with hyperarousal and re-experiencing",
                "symptoms", List.of("Flashbacks", "Hypervigilance", "Avoidance", "Nightmares")
        ));

        library.put("schizophrenia", Map.of(
                "id", "schizophrenia",
                "name", "Schizophrenia",
                "category", "psychosis",
                "profile", Map.of(
                        "serotonin", 0.20,
                        "dopamine", -0.50,       // EXCESS
                        "noradrenaline", -0.10,  // EXCESS
                        "acetylcholine", 0.0,
                        "gaba", 0.15,             // DEFICIT
                        "glutamate", 0.20         // DEFICIT
                ),
                "description", "Psychotic disorder with positive and negative symptoms",
                "symptoms", List.of("Hallucinations", "Delusions", "Disorganized thinking")
        ));

        library.put("schizoaffective", Map.of(
                "id", "schizoaffective",
                "name", "Schizoaffective Disorder",
                "category", "psychosis",
                "profile", Map.of(
                        "serotonin", 0.35,
                        "dopamine", -0.40,       // EXCESS
                        "noradrenaline", 0.15,
                        "acetylcholine", 0.0,
                        "gaba", 0.10,             // DEFICIT
                        "glutamate", 0.15         // DEFICIT
                ),
                "description", "Mixed psychotic and mood symptoms",
                "symptoms", List.of("Psychosis", "Mood episodes", "Delusions", "Hallucinations")
        ));

        library.put("adhd", Map.of(
                "id", "adhd",
                "name", "ADHD",
                "category", "neurodevelopmental",
                "profile", Map.of(
                        "serotonin", 0.05,
                        "dopamine", 0.45,
                        "noradrenaline", 0.40,
                        "acetylcholine", 0.0,
                        "gaba", 0.0,
                        "glutamate", 0.0
                ),
                "description", "Inattention, hyperactivity, impulsivity",
                "symptoms", List.of("Inattention", "Hyperactivity", "Impulsivity", "Disorganization")
        ));

        library.put("alzheimer", Map.of(
                "id", "alzheimer",
                "name", "Alzheimer's Disease",
                "category", "neurodegenerative",
                "profile", Map.of(
                        "serotonin", 0.15,
                        "dopamine", 0.0,
                        "noradrenaline", 0.0,
                        "acetylcholine", 0.60,
                        "gaba", 0.0,
                        "glutamate", 0.10  // DEFICIT
                ),
                "description", "Progressive dementia with cholinergic degeneration",
                "symptoms", List.of("Memory loss", "Disorientation", "Language problems", "Apraxia")
        ));

        library.put("mild_cognitive_impairment", Map.of(
                "id", "mild_cognitive_impairment",
                "name", "Mild Cognitive Impairment",
                "category", "neurodegenerative",
                "profile", Map.of(
                        "serotonin", 0.10,
                        "dopamine", 0.0,
                        "noradrenaline", 0.0,
                        "acetylcholine", 0.30,
                        "gaba", 0.0,
                        "glutamate", 0.0
                ),
                "description", "Pre-dementia stage with mild cholinergic decline",
                "symptoms", List.of("Mild memory problems", "Forgetfulness", "Normal daily function")
        ));

        library.put("parkinson", Map.of(
                "id", "parkinson",
                "name", "Parkinson's Disease",
                "category", "neurodegenerative",
                "profile", Map.of(
                        "serotonin", 0.0,
                        "dopamine", 0.70,
                        "noradrenaline", 0.0,
                        "acetylcholine", -0.15,  // EXCESS
                        "gaba", 0.0,
                        "glutamate", 0.0
                ),
                "description", "Movement disorder with substantia nigra degeneration",
                "symptoms", List.of("Tremor", "Bradykinesia", "Rigidity", "Postural instability")
        ));

        library.put("restless_legs_syndrome", Map.of(
                "id", "restless_legs_syndrome",
                "name", "Restless Legs Syndrome",
                "category", "movement",
                "profile", Map.of(
                        "serotonin", 0.0,
                        "dopamine", 0.30,
                        "noradrenaline", 0.0,
                        "acetylcholine", 0.0,
                        "gaba", 0.0,
                        "glutamate", 0.0
                ),
                "description", "Uncomfortable leg sensations with urge to move",
                "symptoms", List.of("Leg discomfort", "Urge to move", "Worsens at night", "Sleep disruption")
        ));

        library.put("epilepsy", Map.of(
                "id", "epilepsy",
                "name", "Epilepsy",
                "category", "neurological",
                "profile", Map.of(
                        "serotonin", 0.0,
                        "dopamine", 0.0,
                        "noradrenaline", 0.0,
                        "acetylcholine", 0.0,
                        "gaba", 0.40,             // DEFICIT
                        "glutamate", -0.30        // EXCESS
                ),
                "description", "Seizure disorder - imbalance between excitation and inhibition",
                "symptoms", List.of("Seizures", "Loss of consciousness", "Convulsions", "Aura")
        ));

        library.put("chronic_insomnia", Map.of(
                "id", "chronic_insomnia",
                "name", "Chronic Insomnia",
                "category", "sleep",
                "profile", Map.of(
                        "serotonin", 0.15,
                        "dopamine", 0.0,
                        "noradrenaline", -0.20,  // EXCESS
                        "acetylcholine", 0.0,
                        "gaba", 0.35,             // DEFICIT
                        "glutamate", -0.10        // EXCESS
                ),
                "description", "Persistent sleep disorder with GABAergic dysfunction",
                "symptoms", List.of("Difficulty falling asleep", "Frequent awakening", "Early morning awakening", "Daytime fatigue")
        ));

        library.put("healthy", Map.of(
                "id", "healthy",
                "name", "Healthy Baseline",
                "category", "control",
                "profile", Map.of(
                        "serotonin", 0.0,
                        "dopamine", 0.0,
                        "noradrenaline", 0.0,
                        "acetylcholine", 0.0,
                        "gaba", 0.0,
                        "glutamate", 0.0
                ),
                "description", "Normal neurotransmitter balance",
                "symptoms", List.of()
        ));

        return library;
    }
}