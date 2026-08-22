package com.neocortex.backend.dto;

import lombok.Data;

import java.util.List;

/**
 * Response from drug discovery optimization
 */
@Data
public class DiscoveryResponse {
    
    private DrugDefinition optimalDrug;
    private List<FitnessHistoryPoint> fitnessHistory;
    private double finalFitness;
    private int generations;
    private OptimizationMetadata metadata;
    
    @Data
    public static class FitnessHistoryPoint {
        private int generation;
        private double bestFitness;
        private double avgFitness;
        private double diversity;
    }
    
    @Data
    public static class OptimizationMetadata {
        private String disease;
        private int totalEvaluations;
        private long durationMs;
        private String status;
        private boolean converged;
    }
}
