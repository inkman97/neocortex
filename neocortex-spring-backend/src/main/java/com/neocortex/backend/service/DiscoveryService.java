package com.neocortex.backend.service;

import com.neocortex.backend.dto.DiscoveryJob;
import com.neocortex.backend.dto.DiscoveryRequest;
import com.neocortex.backend.dto.DiscoveryResponse;
import com.neocortex.backend.service.discovery.DiscoveryRequestMapper;
import com.neocortex.backend.service.discovery.DiscoveryResponseMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class DiscoveryService {

    private static final String TRIAL_PORT = ":8000";
    private static final String DISCOVERY_PORT = ":8001";
    private static final String DISCOVERY_PATH = "/discover";

    private final RestTemplate restTemplate = new RestTemplate();

    private final DiscoveryRequestMapper requestMapper;
    private final DiscoveryResponseMapper responseMapper;

    @Value("${neocortex.gpu-server.url}")
    private String gpuServerUrl;

    public DiscoveryResponse runDiscovery(DiscoveryRequest request, DiscoveryJob job) {
        String discoveryUrl = gpuServerUrl.replace(TRIAL_PORT, DISCOVERY_PORT) + DISCOVERY_PATH;

        try {
            Map<String, Object> pythonRequest = requestMapper.toPythonRequest(request, job);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            log.info("Starting discovery job {} against {}", job.getJobId(), discoveryUrl);
            log.debug("Discovery payload: {}", pythonRequest);

            @SuppressWarnings("unchecked")
            Map<String, Object> pythonResponse = restTemplate.postForObject(
                    discoveryUrl,
                    new HttpEntity<>(pythonRequest, headers),
                    Map.class);

            return responseMapper.fromPythonResponse(pythonResponse, request);

        } catch (Exception e) {
            log.error("Discovery job {} failed", job.getJobId(), e);
            throw new IllegalStateException("Drug discovery optimization failed: " + e.getMessage(), e);
        }
    }
}
