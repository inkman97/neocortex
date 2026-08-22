package com.neocortex.backend.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

/**
 * Request for drug discovery optimization
 * Uses existing DiseaseDefinition DTO
 *
 * UPDATED: Added docking support
 */
@Data
public class DiscoveryRequest {

    @NotNull
    @Valid
    private DiseaseDefinition disease;  // Uses existing DTO from com.neocortex.backend.dto

    @NotNull
    @Valid
    private OptimizationConfig config;

    @Min(10000)
    @Max(1000000)
    private int neurons = 100000;

    @Data
    public static class OptimizationConfig {
        @Min(10)
        @Max(1000)
        private int iterations = 100;

        @Min(10)
        @Max(500)
        private int populationSize = 50;

        @Min(0)
        @Max(1)
        private double mutationRate = 0.15;

        @Min(0)
        @Max(1)
        private double crossoverRate = 0.7;

        @Min(1)
        @Max(20)
        private int eliteCount = 5;

        private String selectionMethod = "tournament";

        @Valid
        private FitnessWeights weights = new FitnessWeights();

        @Min(1)
        @Max(10)
        private int maxTargets = 5;

        @Min(0)
        @Max(1)
        private double minPotency = 0.1;

        @Min(0)
        @Max(1)
        private double maxPotency = 1.0;

        private List<String> allowedCategories;

        @Min(24)
        @Max(672)
        private int trialDuration = 168;

        @Min(6)
        @Max(48)
        private int samplingInterval = 24;

        // ═══════════════════════════════════════════════════════
        // NEW: DOCKING SUPPORT
        // ═══════════════════════════════════════════════════════

        /**
         * Enable molecular docking validation.
         * If true, uses AutoDock Vina to verify molecules bind to target.
         */
        private boolean useDocking = false;

        /**
         * Docking search exhaustiveness.
         * Higher = more thorough but slower.
         * 4 = fast, 8 = balanced, 32 = thorough
         */
        @Min(4)
        @Max(32)
        private int dockingExhaustiveness = 8;
    }

    @Data
    public static class FitnessWeights {
        private double ntCorrection = 0.6;
        private double sideEffects = 0.2;
        private double complexity = 0.1;
        private double speed = 0.1;

        // ═══════════════════════════════════════════════════════
        // NEW: DOCKING WEIGHT
        // ═══════════════════════════════════════════════════════

        /**
         * Weight for molecular docking score.
         * Measures real binding affinity to target protein.
         * Receptor is auto-selected based on disease profile.
         */
        @Min(0)
        @Max(1)
        private double docking = 0.0;
    }
}