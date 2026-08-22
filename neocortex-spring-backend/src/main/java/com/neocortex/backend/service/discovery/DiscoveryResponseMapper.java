package com.neocortex.backend.service.discovery;

import com.neocortex.backend.dto.DiscoveryRequest;
import com.neocortex.backend.dto.DiscoveryResponse;
import com.neocortex.backend.dto.DrugDefinition;
import com.neocortex.backend.dto.MolecularTarget;
import com.neocortex.backend.dto.Pharmacokinetics;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Component
@SuppressWarnings("unchecked")
public class DiscoveryResponseMapper {

    private static final double CONVERGENCE_THRESHOLD = 0.95;

    public DiscoveryResponse fromPythonResponse(Map<String, Object> pythonResponse, DiscoveryRequest request) {
        DiscoveryResponse response = new DiscoveryResponse();
        response.setOptimalDrug(parseDrug((Map<String, Object>) pythonResponse.get("optimal_drug")));
        response.setFitnessHistory(parseHistory((List<Map<String, Object>>) pythonResponse.get("fitness_history")));
        response.setFinalFitness(asDouble(pythonResponse.get("final_fitness")));
        response.setGenerations(asInt(pythonResponse.get("generations")));
        response.setMetadata(buildMetadata(request, response.getFinalFitness()));
        return response;
    }

    private DrugDefinition parseDrug(Map<String, Object> drugMap) {
        return DrugDefinition.builder()
                .name((String) drugMap.get("name"))
                .drug_class((String) drugMap.get("class"))
                .molecularTargets(parseTargets((List<Map<String, Object>>) drugMap.get("molecularTargets")))
                .pharmacokinetics(parsePharmacokinetics((Map<String, Object>) drugMap.get("pharmacokinetics")))
                .build();
    }

    private List<MolecularTarget> parseTargets(List<Map<String, Object>> targetMaps) {
        List<MolecularTarget> targets = new ArrayList<>();
        for (Map<String, Object> targetMap : targetMaps) {
            targets.add(MolecularTarget.builder()
                    .target((String) targetMap.get("target"))
                    .action((String) targetMap.get("action"))
                    .potency(asDouble(targetMap.get("potency")))
                    .build());
        }
        return targets;
    }

    private Pharmacokinetics parsePharmacokinetics(Map<String, Object> pkMap) {
        return Pharmacokinetics.builder()
                .halfLife_hours(asDouble(pkMap.get("halfLife_hours")))
                .tmax_hours(asDouble(pkMap.get("tmax_hours")))
                .bioavailability(asDouble(pkMap.get("bioavailability")))
                .build();
    }

    private List<DiscoveryResponse.FitnessHistoryPoint> parseHistory(List<Map<String, Object>> historyMaps) {
        List<DiscoveryResponse.FitnessHistoryPoint> history = new ArrayList<>();
        for (Map<String, Object> pointMap : historyMaps) {
            DiscoveryResponse.FitnessHistoryPoint point = new DiscoveryResponse.FitnessHistoryPoint();
            point.setGeneration(asInt(pointMap.get("generation")));
            point.setBestFitness(asDouble(pointMap.get("best_fitness")));
            point.setAvgFitness(asDouble(pointMap.get("avg_fitness")));
            point.setDiversity(asDouble(pointMap.get("diversity")));
            history.add(point);
        }
        return history;
    }

    private DiscoveryResponse.OptimizationMetadata buildMetadata(DiscoveryRequest request, double finalFitness) {
        DiscoveryResponse.OptimizationMetadata metadata = new DiscoveryResponse.OptimizationMetadata();
        metadata.setDisease(request.getDisease().getName());
        metadata.setTotalEvaluations(
                request.getConfig().getIterations() * request.getConfig().getPopulationSize());
        metadata.setStatus("complete");
        metadata.setConverged(finalFitness > CONVERGENCE_THRESHOLD);
        return metadata;
    }

    private double asDouble(Object value) {
        return ((Number) value).doubleValue();
    }

    private int asInt(Object value) {
        return ((Number) value).intValue();
    }
}
