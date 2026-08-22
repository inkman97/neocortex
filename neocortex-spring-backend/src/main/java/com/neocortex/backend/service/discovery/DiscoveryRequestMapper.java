package com.neocortex.backend.service.discovery;

import com.neocortex.backend.dto.DiscoveryJob;
import com.neocortex.backend.dto.DiscoveryRequest;
import com.neocortex.backend.dto.DiseaseDefinition;
import org.springframework.stereotype.Component;

import java.util.LinkedHashMap;
import java.util.Map;

@Component
public class DiscoveryRequestMapper {

    public Map<String, Object> toPythonRequest(DiscoveryRequest request, DiscoveryJob job) {
        DiseaseDefinition disease = request.getDisease();
        if (disease == null) {
            throw new IllegalArgumentException("Discovery requires a disease definition, none was sent");
        }

        Map<String, Object> pythonRequest = new LinkedHashMap<>();
        pythonRequest.put("disease_profile", diseaseProfile(disease));
        pythonRequest.put("config", optimizationConfig(request.getConfig()));
        pythonRequest.put("neurons", request.getNeurons());
        pythonRequest.put("jobId", job.getJobId());
        return pythonRequest;
    }

    private Map<String, Object> diseaseProfile(DiseaseDefinition disease) {
        Map<String, Object> profile = new LinkedHashMap<>();
        profile.put("serotonin_deficit", disease.getSerotonin_deficit());
        profile.put("dopamine_deficit", disease.getDopamine_deficit());
        profile.put("noradrenaline_deficit", disease.getNoradrenaline_deficit());
        profile.put("acetylcholine_deficit", disease.getAcetylcholine_deficit());
        profile.put("gaba_deficit", disease.getGaba_deficit());
        profile.put("glutamate_deficit", disease.getGlutamate_deficit());
        return profile;
    }

    private Map<String, Object> optimizationConfig(DiscoveryRequest.OptimizationConfig config) {
        Map<String, Object> pythonConfig = new LinkedHashMap<>();
        pythonConfig.put("iterations", config.getIterations());
        pythonConfig.put("populationSize", config.getPopulationSize());
        pythonConfig.put("mutationRate", config.getMutationRate());
        pythonConfig.put("crossoverRate", config.getCrossoverRate());
        pythonConfig.put("eliteCount", config.getEliteCount());
        pythonConfig.put("selectionMethod", config.getSelectionMethod());
        pythonConfig.put("weights", fitnessWeights(config.getWeights()));
        pythonConfig.put("useDocking", config.isUseDocking());
        pythonConfig.put("dockingExhaustiveness", config.getDockingExhaustiveness());
        pythonConfig.put("maxTargets", config.getMaxTargets());
        pythonConfig.put("minPotency", config.getMinPotency());
        pythonConfig.put("maxPotency", config.getMaxPotency());
        pythonConfig.put("trialDuration", config.getTrialDuration());
        pythonConfig.put("samplingInterval", config.getSamplingInterval());
        return pythonConfig;
    }

    private Map<String, Object> fitnessWeights(DiscoveryRequest.FitnessWeights weights) {
        Map<String, Object> mapped = new LinkedHashMap<>();
        mapped.put("nt_correction", weights.getNtCorrection());
        mapped.put("side_effects", weights.getSideEffects());
        mapped.put("complexity", weights.getComplexity());
        mapped.put("speed", weights.getSpeed());
        mapped.put("docking", weights.getDocking());
        return mapped;
    }
}
