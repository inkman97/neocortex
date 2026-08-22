package com.neocortex.backend.controller;

import com.neocortex.backend.dto.HealthResponse;
import com.neocortex.backend.dto.TrialRequest;
import com.neocortex.backend.dto.TrialResponse;
import com.neocortex.backend.service.TrialService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/trials")
@RequiredArgsConstructor
@Tag(name = "Drug Trials", description = "Virtual drug trial simulation endpoints")
public class TrialController {

    private final TrialService trialService;

    @GetMapping("/health")
    @Operation(summary = "Report backend and GPU server availability")
    public ResponseEntity<HealthResponse> health() {
        return ResponseEntity.ok(trialService.checkHealth());
    }

    @PostMapping("/simulate")
    @Operation(
            summary = "Run a virtual drug trial",
            description = "Simulates a drug against a disease model on the NeoCortex GPU server"
    )
    public ResponseEntity<TrialResponse> runTrial(@Valid @RequestBody TrialRequest request) {
        TrialResponse response = trialService.runTrial(request);

        log.info("Trial finished: {} timepoints, used_neocortex={}",
                response.getTimepoints().size(),
                response.isUsed_neocortex());

        return ResponseEntity.ok(response);
    }

    @GetMapping("/drugs/library")
    @Operation(summary = "List the known drugs")
    public ResponseEntity<Map<String, Object>> getDrugsLibrary() {
        return ResponseEntity.ok(trialService.getKnownDrugs());
    }

    @GetMapping("/diseases/library")
    @Operation(summary = "List the known diseases")
    public ResponseEntity<Map<String, Object>> getDiseasesLibrary() {
        return ResponseEntity.ok(trialService.getKnownDiseases());
    }
}
