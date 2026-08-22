package com.neocortex.backend.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class DiscoveryJob {
    private String jobId;
    private String status; // "running", "completed", "failed"
    private int currentGeneration;
    private int totalGenerations;
    private double bestFitness;
    private double avgFitness;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private DiscoveryResponse result;
    private String error;
    private DiscoveryRequest request; // Store original request
    private int lastValidGeneration = 0;
    private double lastValidFitness = 0.0;
    private double lastValidAvgFitness = 0.0;

    public DiscoveryJob(String jobId, DiscoveryRequest request) {
        this.jobId = jobId;
        this.request = request;
        this.status = "running";
        this.currentGeneration = 0;
        this.totalGenerations = request.getConfig().getIterations();
        this.bestFitness = 0.0;
        this.avgFitness = 0.0;
        this.startTime = LocalDateTime.now();
    }

    public void updateProgress(int generation, double bestFitness, double avgFitness) {
        this.currentGeneration = generation;
        this.bestFitness = bestFitness;
        this.avgFitness = avgFitness;
        if (generation > 0) {
            this.lastValidGeneration = generation;
            this.lastValidFitness = bestFitness;
            this.lastValidAvgFitness = avgFitness;
        }
    }

    public void complete(DiscoveryResponse result) {
        this.status = "completed";
        this.result = result;
        this.endTime = LocalDateTime.now();
    }

    public void fail(String error) {
        this.status = "failed";
        this.error = error;
        this.endTime = LocalDateTime.now();
    }

    public int getProgressPercent() {
        if (totalGenerations == 0) return 0;
        return (int) ((currentGeneration * 100.0) / totalGenerations);
    }

    public int getSafeGeneration() {
        return currentGeneration > 0 ? currentGeneration : lastValidGeneration;
    }

    public double getSafeFitness() {
        return currentGeneration > 0 ? bestFitness : lastValidFitness;
    }

    public double getSafeAvgFitness() {
        return currentGeneration > 0 ? avgFitness : lastValidAvgFitness;
    }
}