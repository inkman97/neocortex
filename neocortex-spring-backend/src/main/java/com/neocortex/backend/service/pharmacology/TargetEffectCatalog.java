package com.neocortex.backend.service.pharmacology;

import java.util.List;
import java.util.Map;

public final class TargetEffectCatalog {

    public enum Accumulation {
        REPLACE,
        ADD
    }

    public record Contribution(String neurotransmitter, double factor, Accumulation accumulation) {

        static Contribution replace(String neurotransmitter, double factor) {
            return new Contribution(neurotransmitter, factor, Accumulation.REPLACE);
        }

        static Contribution add(String neurotransmitter, double factor) {
            return new Contribution(neurotransmitter, factor, Accumulation.ADD);
        }
    }

    public static final String SEROTONIN = "serotonin";
    public static final String DOPAMINE = "dopamine";
    public static final String NORADRENALINE = "noradrenaline";
    public static final String ACETYLCHOLINE = "acetylcholine";
    public static final String GABA = "gaba";
    public static final String GLUTAMATE = "glutamate";

    private static final Map<String, List<Contribution>> CONTRIBUTIONS = Map.ofEntries(
            Map.entry("SERT_INHIBITION", List.of(Contribution.replace(SEROTONIN, 0.40))),
            Map.entry("DAT_INHIBITION", List.of(Contribution.replace(DOPAMINE, 0.40))),
            Map.entry("NET_INHIBITION", List.of(Contribution.replace(NORADRENALINE, 0.35))),

            Map.entry("D2_ANTAGONISM", List.of(Contribution.add(DOPAMINE, -0.40))),
            Map.entry("D2_AGONISM", List.of(Contribution.replace(DOPAMINE, 0.30))),
            Map.entry("D3_AGONISM", List.of(Contribution.add(DOPAMINE, 0.25))),
            Map.entry("D2_PARTIAL_AGONISM", List.of(Contribution.replace(DOPAMINE, 0.20))),

            Map.entry("HT2A_ANTAGONISM", List.of(Contribution.add(SEROTONIN, -0.20))),
            Map.entry("5HT2A_ANTAGONISM", List.of(Contribution.add(SEROTONIN, -0.20))),
            Map.entry("HT1A_AGONISM", List.of(Contribution.replace(SEROTONIN, 0.30))),
            Map.entry("5HT1A_AGONISM", List.of(Contribution.replace(SEROTONIN, 0.30))),

            Map.entry("ACHE_INHIBITION", List.of(Contribution.replace(ACETYLCHOLINE, 0.40))),
            Map.entry("ACETYLCHOLINESTERASE_INHIBITION", List.of(Contribution.replace(ACETYLCHOLINE, 0.40))),

            Map.entry("DA_PRECURSOR", List.of(Contribution.replace(DOPAMINE, 0.50))),

            Map.entry("MAO_A_INHIBITION", List.of(
                    Contribution.add(SEROTONIN, 0.30),
                    Contribution.add(DOPAMINE, 0.20))),
            Map.entry("MAOA_INHIBITION", List.of(
                    Contribution.add(SEROTONIN, 0.30),
                    Contribution.add(DOPAMINE, 0.20))),
            Map.entry("MAO_B_INHIBITION", List.of(Contribution.replace(DOPAMINE, 0.30))),
            Map.entry("MAOB_INHIBITION", List.of(Contribution.replace(DOPAMINE, 0.30))),

            Map.entry("ALPHA2_ANTAGONISM", List.of(Contribution.replace(NORADRENALINE, 0.30))),

            Map.entry("GABA_A_PAM", List.of(Contribution.replace(GABA, 0.40))),
            Map.entry("GAT_INHIBITION", List.of(Contribution.replace(GABA, 0.35))),
            Map.entry("GABA_TRANSAMINASE_INHIBITION", List.of(Contribution.replace(GABA, 0.30))),

            Map.entry("NMDA_ANTAGONISM", List.of(Contribution.replace(GLUTAMATE, -0.40))),
            Map.entry("GLUTAMATE_RELEASE_INHIBITION", List.of(Contribution.replace(GLUTAMATE, -0.35))),
            Map.entry("VOLTAGE_GATED_SODIUM_BLOCKER", List.of(Contribution.replace(GLUTAMATE, -0.30))),

            Map.entry("ALPHA2DELTA_CALCIUM_CHANNEL_BLOCKER", List.of(
                    Contribution.replace(GLUTAMATE, -0.25),
                    Contribution.add(GABA, 0.15))),
            Map.entry("ALPHA2DELTA_BLOCKER", List.of(
                    Contribution.replace(GLUTAMATE, -0.25),
                    Contribution.add(GABA, 0.15)))
    );

    private TargetEffectCatalog() {
    }

    public static List<Contribution> contributionsFor(String targetName) {
        return CONTRIBUTIONS.getOrDefault(targetName, List.of());
    }
}
