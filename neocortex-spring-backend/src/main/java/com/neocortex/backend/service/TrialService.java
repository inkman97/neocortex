package com.neocortex.backend.service;

import com.neocortex.backend.dto.ActiveMetaboliteDTO;
import com.neocortex.backend.dto.HealthResponse;
import com.neocortex.backend.dto.TrialRequest;
import com.neocortex.backend.dto.TrialResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class TrialService {

    private static final int MIN_NEURONS = 10_000;
    private static final int MAX_NEURONS = 1_000_000;
    private static final int MIN_DURATION_HOURS = 1;
    private static final int MAX_DURATION_HOURS = 8_760;

    private final RestTemplate restTemplate = new RestTemplate();

    private final KnownDrugsLibrary drugsLibrary;
    private final KnownDiseasesLibrary diseasesLibrary;
    private final MathematicalFallbackSimulator fallbackSimulator;

    @Value("${neocortex.gpu-server.url}")
    private String gpuServerUrl;

    public HealthResponse checkHealth() {
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(gpuServerUrl + "/health", Map.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                return HealthResponse.builder()
                        .status("ok")
                        .backendOnline(true)
                        .gpuServerOnline(true)
                        .gpuServerUrl(gpuServerUrl)
                        .neocortexAvailable((Boolean) body.get("neocortex_available"))
                        .gpuAvailable((Boolean) body.get("gpu_available"))
                        .gpuInfo(body.get("gpu_info"))
                        .build();
            }
        } catch (Exception e) {
            log.error("GPU server health check failed: {}", e.getMessage());
        }

        return HealthResponse.builder()
                .status("degraded")
                .backendOnline(true)
                .gpuServerOnline(false)
                .gpuServerUrl(gpuServerUrl)
                .error("GPU server not reachable")
                .build();
    }

    public TrialResponse runTrial(TrialRequest request) {
        validateRequest(request);
        logRequest(request);

        try {
            return callGpuServer(request);
        } catch (Exception e) {
            log.error("GPU server call failed: {}", e.getMessage());
            return fallbackSimulator.simulate(request);
        }
    }

    public Map<String, Object> getKnownDrugs() {
        return drugsLibrary.getDrugs();
    }

    public Map<String, Object> getKnownDiseases() {
        return diseasesLibrary.getDiseases();
    }

    private TrialResponse callGpuServer(TrialRequest request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        log.info("Calling GPU server: {}/simulate", gpuServerUrl);

        ResponseEntity<TrialResponse> response = restTemplate.postForEntity(
                gpuServerUrl + "/simulate",
                new HttpEntity<>(request, headers),
                TrialResponse.class);

        if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
            log.info("GPU server returned {} timepoints", response.getBody().getTimepoints().size());
            return response.getBody();
        }

        throw new IllegalStateException("GPU server returned an empty response");
    }

    private void validateRequest(TrialRequest request) {
        if (request.getDose_mg() <= 0) {
            throw new IllegalArgumentException("Dose must be > 0");
        }
        if (request.getTypical_dose_mg() <= 0) {
            throw new IllegalArgumentException("Typical dose must be > 0");
        }
        if (request.getNeurons() < MIN_NEURONS || request.getNeurons() > MAX_NEURONS) {
            throw new IllegalArgumentException("Neurons must be between 10K and 1M");
        }
        if (request.getDuration_hours() < MIN_DURATION_HOURS || request.getDuration_hours() > MAX_DURATION_HOURS) {
            throw new IllegalArgumentException("Duration must be between 1h and 1 year");
        }
        if (request.getDrug().getMolecularTargets().isEmpty()) {
            throw new IllegalArgumentException("Drug must have at least one molecular target");
        }
    }

    private void logRequest(TrialRequest request) {
        log.info("Trial: drug={} ({}mg), disease={}, duration={}h",
                request.getDrug().getName(),
                request.getDose_mg(),
                request.getDisease().getName(),
                request.getDuration_hours());

        List<ActiveMetaboliteDTO> metabolites = request.getDrug().getActive_metabolites();
        if (metabolites == null || metabolites.isEmpty()) {
            return;
        }

        log.info("Active metabolites: {}", metabolites.size());
        metabolites.forEach(metabolite -> log.info("  {} (t1/2={}h, formation={}%)",
                metabolite.getName(),
                metabolite.getHalfLife_hours(),
                (int) (metabolite.getFormation_fraction() * 100)));
    }
}
