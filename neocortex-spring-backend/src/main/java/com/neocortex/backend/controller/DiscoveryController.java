package com.neocortex.backend.controller;

import com.github.benmanes.caffeine.cache.Cache;
import com.neocortex.backend.dto.DiscoveryJob;
import com.neocortex.backend.dto.DiscoveryRequest;
import com.neocortex.backend.dto.DiscoveryResponse;
import com.neocortex.backend.service.DiscoveryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

@Slf4j
@RestController
@RequestMapping("/api/discovery")
@RequiredArgsConstructor
@Tag(name = "Drug Discovery", description = "Genetic algorithm optimization endpoints")
public class DiscoveryController {

    private static final String STATUS_COMPLETED = "completed";
    private static final String CANCELLED_REASON = "Cancelled by user";

    private final DiscoveryService discoveryService;
    private final Cache<String, DiscoveryJob> discoveryJobCache;

    @PostMapping("/start")
    @Operation(summary = "Start an asynchronous drug discovery run")
    public ResponseEntity<Map<String, String>> startDiscovery(@RequestBody DiscoveryRequest request) {
        String jobId = UUID.randomUUID().toString();
        DiscoveryJob job = new DiscoveryJob(jobId, request);
        discoveryJobCache.put(jobId, job);

        log.info("Discovery job {} accepted: disease={}, iterations={}, population={}",
                jobId,
                request.getDisease().getName(),
                request.getConfig().getIterations(),
                request.getConfig().getPopulationSize());

        CompletableFuture.runAsync(() -> execute(jobId, request, job));

        return ResponseEntity.ok(Map.of(
                "jobId", jobId,
                "status", "started",
                "message", "Discovery started. Poll /status/" + jobId + " for progress."
        ));
    }

    @GetMapping("/status/{jobId}")
    @Operation(summary = "Read job progress, optionally reporting it")
    public ResponseEntity<?> getJobStatus(
            @PathVariable String jobId,
            @RequestParam(required = false) Integer generation,
            @RequestParam(required = false) Double fitness,
            @RequestParam(required = false) Double avgFitness) {

        DiscoveryJob job = discoveryJobCache.getIfPresent(jobId);
        if (job == null) {
            return jobNotFound(jobId);
        }

        if (generation != null && fitness != null) {
            job.updateProgress(generation, fitness, avgFitness != null ? avgFitness : fitness);
            discoveryJobCache.put(jobId, job);
            log.debug("Job {} progress: generation={}, fitness={}", jobId, generation, fitness);
        }

        Map<String, Object> status = new LinkedHashMap<>();
        status.put("jobId", job.getJobId());
        status.put("status", job.getStatus());
        status.put("currentGeneration", job.getSafeGeneration());
        status.put("totalGenerations", job.getTotalGenerations());
        status.put("bestFitness", job.getSafeFitness());
        status.put("avgFitness", job.getSafeAvgFitness());
        status.put("progressPercent", job.getProgressPercent());
        status.put("result", job.getResult() != null ? job.getResult() : Map.of());

        return ResponseEntity.ok(status);
    }

    @GetMapping("/result/{jobId}")
    @Operation(summary = "Read the final result of a completed job")
    public ResponseEntity<?> getJobResult(@PathVariable String jobId) {
        DiscoveryJob job = discoveryJobCache.getIfPresent(jobId);
        if (job == null) {
            return jobNotFound(jobId);
        }

        if (!STATUS_COMPLETED.equals(job.getStatus())) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of(
                    "error", "Job has not finished yet",
                    "status", job.getStatus(),
                    "progress", job.getProgressPercent() + "%"
            ));
        }

        return ResponseEntity.ok(job.getResult());
    }

    @DeleteMapping("/cancel/{jobId}")
    @Operation(summary = "Mark a running job as cancelled")
    public ResponseEntity<?> cancelJob(@PathVariable String jobId) {
        DiscoveryJob job = discoveryJobCache.getIfPresent(jobId);
        if (job == null) {
            return jobNotFound(jobId);
        }

        if (STATUS_COMPLETED.equals(job.getStatus())) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of(
                    "error", "Job has already completed"
            ));
        }

        job.fail(CANCELLED_REASON);
        discoveryJobCache.put(jobId, job);

        return ResponseEntity.ok(Map.of(
                "message", "Job marked as cancelled",
                "jobId", jobId
        ));
    }

    private void execute(String jobId, DiscoveryRequest request, DiscoveryJob job) {
        try {
            DiscoveryResponse result = discoveryService.runDiscovery(request, job);
            job.complete(result);
            discoveryJobCache.put(jobId, job);
            log.info("Job {} completed with fitness {}", jobId, result.getFinalFitness());
        } catch (Exception e) {
            log.error("Job {} failed", jobId, e);
            job.fail(e.getMessage());
            discoveryJobCache.put(jobId, job);
        }
    }

    private ResponseEntity<Map<String, String>> jobNotFound(String jobId) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of(
                "error", "Job not found",
                "jobId", jobId,
                "message", "The job may have expired after 24h, or it never existed"
        ));
    }
}
