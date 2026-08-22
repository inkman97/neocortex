package com.neocortex.backend.service;

import com.neocortex.backend.dto.ActiveMetaboliteDTO;
import com.neocortex.backend.dto.DrugDefinition;
import com.neocortex.backend.dto.Pharmacokinetics;
import com.neocortex.backend.dto.TrialRequest;
import com.neocortex.backend.dto.TrialResponse;
import com.neocortex.backend.dto.TrialTimepoint;
import com.neocortex.backend.service.pharmacology.DrugEffect;
import com.neocortex.backend.service.pharmacology.DrugEffectCalculator;
import com.neocortex.backend.service.pharmacology.EmotionClassifier;
import com.neocortex.backend.service.pharmacology.NeurochemicalState;
import com.neocortex.backend.service.pharmacology.PhysiologicalState;
import com.neocortex.backend.service.pharmacology.PlasmaConcentrationCalculator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class MathematicalFallbackSimulator {

    private static final String FALLBACK_REASON =
            "GPU server unavailable - using mathematical model with Hill + metabolites";

    private final DrugEffectCalculator effectCalculator;
    private final PlasmaConcentrationCalculator concentrationCalculator;

    public TrialResponse simulate(TrialRequest request) {
        log.warn("GPU server unavailable, falling back to the mathematical model");

        DrugDefinition drug = request.getDrug();
        Pharmacokinetics pk = drug.getPharmacokinetics();
        List<ActiveMetaboliteDTO> metabolites = metabolitesOf(drug);

        NeurochemicalState baseline = NeurochemicalState.baselineFor(request.getDisease());

        Map<String, DrugEffect> parentEffects = effectCalculator.calculate(
                drug.getMolecularTargets(), request.getDose_mg(), request.getTypical_dose_mg());

        List<Map<String, DrugEffect>> metaboliteEffects = metabolites.stream()
                .map(metabolite -> effectCalculator.calculate(
                        metabolite.getTargets(), request.getDose_mg(), request.getTypical_dose_mg()))
                .toList();

        List<TrialTimepoint> timepoints = new ArrayList<>();

        for (int hour = 0; hour <= request.getDuration_hours(); hour += request.getSampling_interval_hours()) {
            timepoints.add(buildTimepoint(hour, pk, baseline, parentEffects, metabolites, metaboliteEffects));
        }

        return TrialResponse.builder()
                .trial_id("fallback_" + System.currentTimeMillis())
                .success(true)
                .timepoints(timepoints)
                .used_neocortex(false)
                .neurons(request.getNeurons())
                .duration_hours(request.getDuration_hours())
                .fallback_reason(FALLBACK_REASON)
                .build();
    }

    private TrialTimepoint buildTimepoint(
            double hours,
            Pharmacokinetics pk,
            NeurochemicalState baseline,
            Map<String, DrugEffect> parentEffects,
            List<ActiveMetaboliteDTO> metabolites,
            List<Map<String, DrugEffect>> metaboliteEffects) {

        double parentLevel = concentrationCalculator.parentConcentration(hours, pk);
        Map<String, Double> metaboliteLevels = new LinkedHashMap<>();

        NeurochemicalState state = baseline.plusScaledEffects(parentEffects, effectCalculator, parentLevel);

        for (int i = 0; i < metabolites.size(); i++) {
            ActiveMetaboliteDTO metabolite = metabolites.get(i);
            double level = concentrationCalculator.metaboliteConcentration(hours, pk, metabolite);
            metaboliteLevels.put(metabolite.getName(), level);
            state = state.plusScaledEffects(metaboliteEffects.get(i), effectCalculator, level);
        }

        state = state.clipped();

        double arousal = state.arousal();
        double valence = state.valence();
        PhysiologicalState physiology = PhysiologicalState.from(state, arousal, valence);

        return TrialTimepoint.builder()
                .hours(hours)
                .days(hours / 24.0)
                .phase(hours == 0 ? "baseline" : "treatment")
                .drug_concentration(parentLevel * 100)
                .metabolite_concentrations(asPercentages(metaboliteLevels))
                .serotonin(state.serotonin())
                .dopamine(state.dopamine())
                .noradrenaline(state.noradrenaline())
                .acetylcholine(state.acetylcholine())
                .gaba(state.gaba())
                .glutamate(state.glutamate())
                .arousal(arousal)
                .valence(valence)
                .firing_rate(0.0)
                .dominant_emotion(EmotionClassifier.classify(valence, arousal))
                .heart_rate(physiology.heartRate())
                .respiratory_rate(physiology.respiratoryRate())
                .skin_conductance(physiology.skinConductance())
                .muscle_tension(physiology.muscleTension())
                .gut_feeling(physiology.gutFeeling())
                .temperature(physiology.temperature())
                .pain(physiology.pain())
                .fatigue(physiology.fatigue())
                .build();
    }

    private List<ActiveMetaboliteDTO> metabolitesOf(DrugDefinition drug) {
        return drug.getActive_metabolites() != null
                ? drug.getActive_metabolites()
                : Collections.emptyList();
    }

    private Map<String, Double> asPercentages(Map<String, Double> levels) {
        Map<String, Double> percentages = new LinkedHashMap<>();
        levels.forEach((name, level) -> percentages.put(name, level * 100));
        return percentages;
    }
}
