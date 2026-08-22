package com.neocortex.backend.service;

import org.springframework.stereotype.Component;

import java.util.*;

/**
 * Complete Drug Library with Hill Coefficients + Active Metabolites
 *
 * UPDATED: Added Hill coefficients and active metabolites
 * All drug effects emerge from molecular targets - NO hardcoded clinical responses
 */
@Component
public class KnownDrugsLibrary {

    private static final Map<String, Object> LIBRARY = buildLibrary();

    public Map<String, Object> getDrugs() {
        return LIBRARY;
    }

    private static Map<String, Object> buildLibrary() {
        Map<String, Object> library = new LinkedHashMap<>();

        // ============================================================
        // SSRIs (Selective Serotonin Reuptake Inhibitors)
        // ============================================================

        library.put("fluoxetine", Map.of(
                "id", "fluoxetine",
                "name", "Fluoxetine (Prozac)",
                "class", "SSRI",
                "typical_dose_mg", 20,
                "dose_range", List.of(10, 80),
                "indications", List.of("depression", "ocd", "panic_disorder", "social_anxiety"),
                "targets", List.of(
                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.85, "hill", 1.5)
                ),
                "pk", Map.of("halfLife", 96, "tmax", 6, "bioavailability", 0.72),
                "active_metabolites", List.of(
                        Map.of(
                                "name", "norfluoxetine",
                                "formation_fraction", 0.80,
                                "halfLife", 336,
                                "tmax", 24,
                                "targets", List.of(
                                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.75, "hill", 1.5)
                                )
                        )
                )
        ));

        library.put("sertraline", Map.of(
                "id", "sertraline",
                "name", "Sertraline (Zoloft)",
                "class", "SSRI",
                "typical_dose_mg", 50,
                "dose_range", List.of(25, 200),
                "indications", List.of("depression", "ocd", "panic_disorder", "ptsd", "social_anxiety"),
                "targets", List.of(
                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.75, "hill", 1.5),
                        Map.of("target", "dat_inhibition", "action", "mechanism", "potency", 0.15, "hill", 1.3)
                ),
                "pk", Map.of("halfLife", 26, "tmax", 5, "bioavailability", 0.44),
                "active_metabolites", List.of(
                        Map.of(
                                "name", "desmethylsertraline",
                                "formation_fraction", 0.60,
                                "halfLife", 62,
                                "tmax", 12,
                                "targets", List.of(
                                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.15, "hill", 1.4)
                                )
                        )
                )
        ));

        library.put("paroxetine", Map.of(
                "id", "paroxetine",
                "name", "Paroxetine (Paxil)",
                "class", "SSRI",
                "typical_dose_mg", 20,
                "dose_range", List.of(10, 60),
                "indications", List.of("depression", "generalized_anxiety", "social_anxiety", "panic_disorder", "ptsd"),
                "targets", List.of(
                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.80, "hill", 1.6)
                ),
                "pk", Map.of("halfLife", 21, "tmax", 5, "bioavailability", 0.50)
        ));

        library.put("escitalopram", Map.of(
                "id", "escitalopram",
                "name", "Escitalopram (Lexapro)",
                "class", "SSRI",
                "typical_dose_mg", 10,
                "dose_range", List.of(5, 20),
                "indications", List.of("depression", "generalized_anxiety"),
                "targets", List.of(
                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.95, "hill", 1.7)
                ),
                "pk", Map.of("halfLife", 30, "tmax", 5, "bioavailability", 0.80)
        ));

        library.put("fluvoxamine", Map.of(
                "id", "fluvoxamine",
                "name", "Fluvoxamine (Luvox)",
                "class", "SSRI",
                "typical_dose_mg", 100,
                "dose_range", List.of(50, 300),
                "indications", List.of("ocd", "social_anxiety"),
                "targets", List.of(
                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.77, "hill", 1.4)
                ),
                "pk", Map.of("halfLife", 15, "tmax", 4, "bioavailability", 0.53)
        ));

        // ============================================================
        // SNRIs (Serotonin-Norepinephrine Reuptake Inhibitors)
        // ============================================================

        library.put("venlafaxine", Map.of(
                "id", "venlafaxine",
                "name", "Venlafaxine (Effexor)",
                "class", "SNRI",
                "typical_dose_mg", 150,
                "dose_range", List.of(37, 375),
                "indications", List.of("depression", "generalized_anxiety", "social_anxiety", "panic_disorder"),
                "targets", List.of(
                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.70, "hill", 1.5),
                        Map.of("target", "net_inhibition", "action", "mechanism", "potency", 0.50, "hill", 1.4)
                ),
                "pk", Map.of("halfLife", 5, "tmax", 6, "bioavailability", 0.45),
                "active_metabolites", List.of(
                        Map.of(
                                "name", "o-desmethylvenlafaxine",
                                "formation_fraction", 0.90,
                                "halfLife", 11,
                                "tmax", 8,
                                "targets", List.of(
                                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.85, "hill", 1.5),
                                        Map.of("target", "net_inhibition", "action", "mechanism", "potency", 0.85, "hill", 1.5)
                                )
                        )
                )
        ));

        library.put("duloxetine", Map.of(
                "id", "duloxetine",
                "name", "Duloxetine (Cymbalta)",
                "class", "SNRI",
                "typical_dose_mg", 60,
                "dose_range", List.of(30, 120),
                "indications", List.of("depression", "generalized_anxiety"),
                "targets", List.of(
                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.75, "hill", 1.5),
                        Map.of("target", "net_inhibition", "action", "mechanism", "potency", 0.70, "hill", 1.5)
                ),
                "pk", Map.of("halfLife", 12, "tmax", 6, "bioavailability", 0.50)
        ));

        // ============================================================
        // NDRIs (Norepinephrine-Dopamine Reuptake Inhibitors)
        // ============================================================

        library.put("bupropion", Map.of(
                "id", "bupropion",
                "name", "Bupropion (Wellbutrin)",
                "class", "NDRI",
                "typical_dose_mg", 300,
                "dose_range", List.of(150, 450),
                "indications", List.of("depression", "adhd"),
                "targets", List.of(
                        Map.of("target", "dat_inhibition", "action", "mechanism", "potency", 0.55, "hill", 1.4),
                        Map.of("target", "net_inhibition", "action", "mechanism", "potency", 0.45, "hill", 1.3)
                ),
                "pk", Map.of("halfLife", 21, "tmax", 3, "bioavailability", 0.85),
                "active_metabolites", List.of(
                        Map.of(
                                "name", "hydroxybupropion",
                                "formation_fraction", 0.70,
                                "halfLife", 20,
                                "tmax", 6,
                                "targets", List.of(
                                        Map.of("target", "dat_inhibition", "action", "mechanism", "potency", 0.35, "hill", 1.3),
                                        Map.of("target", "net_inhibition", "action", "mechanism", "potency", 0.30, "hill", 1.2)
                                )
                        )
                )
        ));

        // ============================================================
        // NaSSAs (Noradrenergic and Specific Serotonergic Antidepressants)
        // ============================================================

        library.put("mirtazapine", Map.of(
                "id", "mirtazapine",
                "name", "Mirtazapine (Remeron)",
                "class", "NaSSA",
                "typical_dose_mg", 30,
                "dose_range", List.of(15, 45),
                "indications", List.of("depression", "generalized_anxiety"),
                "targets", List.of(
                        Map.of("target", "alpha2_antagonism", "action", "mechanism", "potency", 0.80, "hill", 1.6),
                        Map.of("target", "ht2a_antagonism", "action", "mechanism", "potency", 0.60, "hill", 1.5)
                ),
                "pk", Map.of("halfLife", 30, "tmax", 2, "bioavailability", 0.50),
                "active_metabolites", List.of(
                        Map.of(
                                "name", "desmethylmirtazapine",
                                "formation_fraction", 0.50,
                                "halfLife", 40,
                                "tmax", 6,
                                "targets", List.of(
                                        Map.of("target", "alpha2_antagonism", "action", "mechanism", "potency", 0.30, "hill", 1.5)
                                )
                        )
                )
        ));

        // ============================================================
        // ATYPICAL ANTIPSYCHOTICS
        // ============================================================

        library.put("risperidone", Map.of(
                "id", "risperidone",
                "name", "Risperidone (Risperdal)",
                "class", "Atypical Antipsychotic",
                "typical_dose_mg", 4,
                "dose_range", List.of(1, 8),
                "indications", List.of("schizophrenia", "schizoaffective", "bipolar_depression"),
                "targets", List.of(
                        Map.of("target", "d2_antagonism", "action", "mechanism", "potency", 0.70, "hill", 1.7),
                        Map.of("target", "ht2a_antagonism", "action", "mechanism", "potency", 0.90, "hill", 1.6)
                ),
                "pk", Map.of("halfLife", 20, "tmax", 1, "bioavailability", 0.70),
                "active_metabolites", List.of(
                        Map.of(
                                "name", "9-hydroxyrisperidone",
                                "formation_fraction", 0.85,
                                "halfLife", 24,
                                "tmax", 3,
                                "targets", List.of(
                                        Map.of("target", "d2_antagonism", "action", "mechanism", "potency", 0.85, "hill", 1.7),
                                        Map.of("target", "ht2a_antagonism", "action", "mechanism", "potency", 0.95, "hill", 1.6)
                                )
                        )
                )
        ));

        library.put("aripiprazole", Map.of(
                "id", "aripiprazole",
                "name", "Aripiprazole (Abilify)",
                "class", "Atypical Antipsychotic",
                "typical_dose_mg", 10,
                "dose_range", List.of(2, 30),
                "indications", List.of("schizophrenia", "schizoaffective", "bipolar_depression"),
                "targets", List.of(
                        Map.of("target", "d2_partial_agonism", "action", "mechanism", "potency", 0.60, "hill", 1.5),
                        Map.of("target", "ht2a_antagonism", "action", "mechanism", "potency", 0.85, "hill", 1.5),
                        Map.of("target", "ht1a_agonism", "action", "mechanism", "potency", 0.70, "hill", 1.4)
                ),
                "pk", Map.of("halfLife", 75, "tmax", 3, "bioavailability", 0.87),
                "active_metabolites", List.of(
                        Map.of(
                                "name", "dehydroaripiprazole",
                                "formation_fraction", 0.75,
                                "halfLife", 94,
                                "tmax", 12,
                                "targets", List.of(
                                        Map.of("target", "d2_partial_agonism", "action", "mechanism", "potency", 0.30, "hill", 1.4),
                                        Map.of("target", "ht2a_antagonism", "action", "mechanism", "potency", 0.36, "hill", 1.4)
                                )
                        )
                )
        ));

        library.put("olanzapine", Map.of(
                "id", "olanzapine",
                "name", "Olanzapine (Zyprexa)",
                "class", "Atypical Antipsychotic",
                "typical_dose_mg", 10,
                "dose_range", List.of(5, 20),
                "indications", List.of("schizophrenia", "schizoaffective", "bipolar_depression"),
                "targets", List.of(
                        Map.of("target", "d2_antagonism", "action", "mechanism", "potency", 0.65, "hill", 1.5),
                        Map.of("target", "ht2a_antagonism", "action", "mechanism", "potency", 0.85, "hill", 1.6)
                ),
                "pk", Map.of("halfLife", 33, "tmax", 6, "bioavailability", 0.80)
        ));

        library.put("quetiapine", Map.of(
                "id", "quetiapine",
                "name", "Quetiapine (Seroquel)",
                "class", "Atypical Antipsychotic",
                "typical_dose_mg", 300,
                "dose_range", List.of(50, 800),
                "indications", List.of("schizophrenia", "bipolar_depression", "generalized_anxiety"),
                "targets", List.of(
                        Map.of("target", "d2_antagonism", "action", "mechanism", "potency", 0.45, "hill", 1.3),
                        Map.of("target", "ht2a_antagonism", "action", "mechanism", "potency", 0.70, "hill", 1.4)
                ),
                "pk", Map.of("halfLife", 6, "tmax", 1.5, "bioavailability", 0.10),
                "active_metabolites", List.of(
                        Map.of(
                                "name", "norquetiapine",
                                "formation_fraction", 0.50,
                                "halfLife", 12,
                                "tmax", 4,
                                "targets", List.of(
                                        Map.of("target", "net_inhibition", "action", "mechanism", "potency", 0.15, "hill", 1.2)
                                )
                        )
                )
        ));

        // ============================================================
        // STIMULANTS (ADHD)
        // ============================================================

        library.put("methylphenidate", Map.of(
                "id", "methylphenidate",
                "name", "Methylphenidate (Ritalin)",
                "class", "Stimulant",
                "typical_dose_mg", 20,
                "dose_range", List.of(10, 60),
                "indications", List.of("adhd"),
                "targets", List.of(
                        Map.of("target", "dat_inhibition", "action", "mechanism", "potency", 0.65, "hill", 1.5),
                        Map.of("target", "net_inhibition", "action", "mechanism", "potency", 0.55, "hill", 1.4)
                ),
                "pk", Map.of("halfLife", 3, "tmax", 2, "bioavailability", 0.30)
        ));

        library.put("amphetamine", Map.of(
                "id", "amphetamine",
                "name", "Amphetamine (Adderall)",
                "class", "Stimulant",
                "typical_dose_mg", 20,
                "dose_range", List.of(5, 60),
                "indications", List.of("adhd"),
                "targets", List.of(
                        Map.of("target", "dat_inhibition", "action", "mechanism", "potency", 0.80, "hill", 1.6),
                        Map.of("target", "net_inhibition", "action", "mechanism", "potency", 0.70, "hill", 1.5),
                        Map.of("target", "sert_inhibition", "action", "mechanism", "potency", 0.30, "hill", 1.3)
                ),
                "pk", Map.of("halfLife", 10, "tmax", 3, "bioavailability", 0.75)
        ));

        library.put("atomoxetine", Map.of(
                "id", "atomoxetine",
                "name", "Atomoxetine (Strattera)",
                "class", "NRI",
                "typical_dose_mg", 80,
                "dose_range", List.of(40, 100),
                "indications", List.of("adhd"),
                "targets", List.of(
                        Map.of("target", "net_inhibition", "action", "mechanism", "potency", 0.90, "hill", 1.7)
                ),
                "pk", Map.of("halfLife", 5, "tmax", 1.5, "bioavailability", 0.63)
        ));

        // ============================================================
        // CHOLINESTERASE INHIBITORS (Alzheimer's)
        // ============================================================

        library.put("donepezil", Map.of(
                "id", "donepezil",
                "name", "Donepezil (Aricept)",
                "class", "AChE Inhibitor",
                "typical_dose_mg", 10,
                "dose_range", List.of(5, 23),
                "indications", List.of("alzheimer", "mild_cognitive_impairment"),
                "targets", List.of(
                        Map.of("target", "ache_inhibition", "action", "mechanism", "potency", 0.75, "hill", 1.6)
                ),
                "pk", Map.of("halfLife", 70, "tmax", 4, "bioavailability", 1.0)
        ));

        library.put("rivastigmine", Map.of(
                "id", "rivastigmine",
                "name", "Rivastigmine (Exelon)",
                "class", "AChE/BuChE Inhibitor",
                "typical_dose_mg", 6,
                "dose_range", List.of(3, 12),
                "indications", List.of("alzheimer", "parkinson"),
                "targets", List.of(
                        Map.of("target", "ache_inhibition", "action", "mechanism", "potency", 0.70, "hill", 1.5)
                ),
                "pk", Map.of("halfLife", 1.5, "tmax", 1, "bioavailability", 0.36)
        ));

        library.put("galantamine", Map.of(
                "id", "galantamine",
                "name", "Galantamine (Razadyne)",
                "class", "AChE Inhibitor",
                "typical_dose_mg", 16,
                "dose_range", List.of(8, 24),
                "indications", List.of("alzheimer", "mild_cognitive_impairment"),
                "targets", List.of(
                        Map.of("target", "ache_inhibition", "action", "mechanism", "potency", 0.68, "hill", 1.5)
                ),
                "pk", Map.of("halfLife", 7, "tmax", 1.5, "bioavailability", 0.90)
        ));

        // ============================================================
        // PARKINSON'S DISEASE
        // ============================================================

        library.put("levodopa", Map.of(
                "id", "levodopa",
                "name", "Levodopa (L-DOPA)",
                "class", "DA Precursor",
                "typical_dose_mg", 400,
                "dose_range", List.of(100, 1000),
                "indications", List.of("parkinson"),
                "targets", List.of(
                        Map.of("target", "da_precursor", "action", "mechanism", "potency", 0.90, "hill", 1.3)
                ),
                "pk", Map.of("halfLife", 1.5, "tmax", 0.75, "bioavailability", 0.30)
        ));

        library.put("pramipexole", Map.of(
                "id", "pramipexole",
                "name", "Pramipexole (Mirapex)",
                "class", "DA Agonist",
                "typical_dose_mg", 1.5,
                "dose_range", List.of(0.5, 4.5),
                "indications", List.of("parkinson", "restless_legs_syndrome"),
                "targets", List.of(
                        Map.of("target", "d2_agonism", "action", "mechanism", "potency", 0.75, "hill", 1.6),
                        Map.of("target", "d3_agonism", "action", "mechanism", "potency", 0.85, "hill", 1.7)
                ),
                "pk", Map.of("halfLife", 8, "tmax", 2, "bioavailability", 0.90)
        ));

        library.put("ropinirole", Map.of(
                "id", "ropinirole",
                "name", "Ropinirole (Requip)",
                "class", "DA Agonist",
                "typical_dose_mg", 6,
                "dose_range", List.of(1, 24),
                "indications", List.of("parkinson", "restless_legs_syndrome"),
                "targets", List.of(
                        Map.of("target", "d2_agonism", "action", "mechanism", "potency", 0.70, "hill", 1.5),
                        Map.of("target", "d3_agonism", "action", "mechanism", "potency", 0.80, "hill", 1.6)
                ),
                "pk", Map.of("halfLife", 6, "tmax", 1.5, "bioavailability", 0.55)
        ));

        library.put("selegiline", Map.of(
                "id", "selegiline",
                "name", "Selegiline (Eldepryl)",
                "class", "MAO-B Inhibitor",
                "typical_dose_mg", 5,
                "dose_range", List.of(5, 10),
                "indications", List.of("parkinson"),
                "targets", List.of(
                        Map.of("target", "mao_b_inhibition", "action", "mechanism", "potency", 0.85, "hill", 1.8)
                ),
                "pk", Map.of("halfLife", 2, "tmax", 0.5, "bioavailability", 0.10)
        ));

        // ============================================================
        // BENZODIAZEPINES (Anxiety, Insomnia)
        // ============================================================

        library.put("diazepam", Map.of(
                "id", "diazepam",
                "name", "Diazepam (Valium)",
                "class", "Benzodiazepine",
                "typical_dose_mg", 10,
                "dose_range", List.of(2, 40),
                "indications", List.of("generalized_anxiety", "panic_disorder", "chronic_insomnia"),
                "targets", List.of(
                        Map.of("target", "gaba_a_pam", "action", "mechanism", "potency", 0.85, "hill", 1.6)
                ),
                "pk", Map.of("halfLife", 48, "tmax", 1, "bioavailability", 1.0),
                "active_metabolites", List.of(
                        Map.of(
                                "name", "nordiazepam",
                                "formation_fraction", 0.70,
                                "halfLife", 100,
                                "tmax", 12,
                                "targets", List.of(
                                        Map.of("target", "gaba_a_pam", "action", "mechanism", "potency", 0.75, "hill", 1.6)
                                )
                        )
                )
        ));

        library.put("lorazepam", Map.of(
                "id", "lorazepam",
                "name", "Lorazepam (Ativan)",
                "class", "Benzodiazepine",
                "typical_dose_mg", 2,
                "dose_range", List.of(1, 6),
                "indications", List.of("generalized_anxiety", "panic_disorder", "chronic_insomnia"),
                "targets", List.of(
                        Map.of("target", "gaba_a_pam", "action", "mechanism", "potency", 0.80, "hill", 1.5)
                ),
                "pk", Map.of("halfLife", 14, "tmax", 2, "bioavailability", 0.90)
        ));

        library.put("alprazolam", Map.of(
                "id", "alprazolam",
                "name", "Alprazolam (Xanax)",
                "class", "Benzodiazepine",
                "typical_dose_mg", 1,
                "dose_range", List.of(0.5, 4),
                "indications", List.of("generalized_anxiety", "panic_disorder"),
                "targets", List.of(
                        Map.of("target", "gaba_a_pam", "action", "mechanism", "potency", 0.82, "hill", 1.6)
                ),
                "pk", Map.of("halfLife", 12, "tmax", 1.5, "bioavailability", 0.80),
                "active_metabolites", List.of(
                        Map.of(
                                "name", "alpha-hydroxyalprazolam",
                                "formation_fraction", 0.40,
                                "halfLife", 12,
                                "tmax", 3,
                                "targets", List.of(
                                        Map.of("target", "gaba_a_pam", "action", "mechanism", "potency", 0.45, "hill", 1.5)
                                )
                        )
                )
        ));

        library.put("clonazepam", Map.of(
                "id", "clonazepam",
                "name", "Clonazepam (Klonopin)",
                "class", "Benzodiazepine",
                "typical_dose_mg", 1,
                "dose_range", List.of(0.5, 4),
                "indications", List.of("panic_disorder", "epilepsy"),
                "targets", List.of(
                        Map.of("target", "gaba_a_pam", "action", "mechanism", "potency", 0.87, "hill", 1.7)
                ),
                "pk", Map.of("halfLife", 40, "tmax", 2, "bioavailability", 0.90)
        ));

        // ============================================================
        // ANTICONVULSANTS (Epilepsy)
        // ============================================================

        library.put("lamotrigine", Map.of(
                "id", "lamotrigine",
                "name", "Lamotrigine (Lamictal)",
                "class", "Anticonvulsant",
                "typical_dose_mg", 200,
                "dose_range", List.of(25, 400),
                "indications", List.of("epilepsy", "bipolar_depression"),
                "targets", List.of(
                        Map.of("target", "voltage_gated_sodium_blocker", "action", "mechanism", "potency", 0.70, "hill", 1.4),
                        Map.of("target", "glutamate_release_inhibition", "action", "mechanism", "potency", 0.50, "hill", 1.3)
                ),
                "pk", Map.of("halfLife", 29, "tmax", 2.5, "bioavailability", 0.98)
        ));

        library.put("valproate", Map.of(
                "id", "valproate",
                "name", "Valproate (Depakote)",
                "class", "Anticonvulsant",
                "typical_dose_mg", 1000,
                "dose_range", List.of(500, 2000),
                "indications", List.of("epilepsy", "bipolar_depression"),
                "targets", List.of(
                        Map.of("target", "gaba_transaminase_inhibition", "action", "mechanism", "potency", 0.75, "hill", 1.5),
                        Map.of("target", "voltage_gated_sodium_blocker", "action", "mechanism", "potency", 0.50, "hill", 1.3)
                ),
                "pk", Map.of("halfLife", 16, "tmax", 4, "bioavailability", 1.0)
        ));

        library.put("gabapentin", Map.of(
                "id", "gabapentin",
                "name", "Gabapentin (Neurontin)",
                "class", "Gabapentinoid",
                "typical_dose_mg", 900,
                "dose_range", List.of(300, 3600),
                "indications", List.of("epilepsy", "generalized_anxiety"),
                "targets", List.of(
                        Map.of("target", "alpha2delta_calcium_channel_blocker", "action", "mechanism", "potency", 0.70, "hill", 1.4)
                ),
                "pk", Map.of("halfLife", 6, "tmax", 3, "bioavailability", 0.60)
        ));

        // ============================================================
        // Z-DRUGS (Insomnia)
        // ============================================================

        library.put("zolpidem", Map.of(
                "id", "zolpidem",
                "name", "Zolpidem (Ambien)",
                "class", "Z-Drug",
                "typical_dose_mg", 10,
                "dose_range", List.of(5, 10),
                "indications", List.of("chronic_insomnia"),
                "targets", List.of(
                        Map.of("target", "gaba_a_pam", "action", "mechanism", "potency", 0.75, "hill", 1.8)
                ),
                "pk", Map.of("halfLife", 2.5, "tmax", 1.5, "bioavailability", 0.70)
        ));

        // ============================================================
        // NARIs (Noradrenaline Reuptake Inhibitors)
        // ============================================================

        library.put("reboxetine", Map.of(
                "id", "reboxetine",
                "name", "Reboxetine (Edronax)",
                "class", "NARI",
                "typical_dose_mg", 8,
                "dose_range", List.of(4, 12),
                "indications", List.of("depression"),
                "targets", List.of(
                        Map.of("target", "net_inhibition", "action", "mechanism", "potency", 0.90, "hill", 1.6)
                ),
                "pk", Map.of("halfLife", 13, "tmax", 2, "bioavailability", 0.60),
                "notes", "FAILED DRUG: Approved in Europe (1997) but REJECTED by FDA (2001). Meta-analysis (BMJ 2010) showed NOT superior to placebo for major depression. Mechanism: Only increases NE, but depression requires 5HT (primary) + DA. Used for validation testing in NeoCortex."
        ));

        return library;
    }
}