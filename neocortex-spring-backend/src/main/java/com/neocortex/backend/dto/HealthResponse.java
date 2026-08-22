package com.neocortex.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class HealthResponse {
    private String status;
    private boolean backendOnline;
    private boolean gpuServerOnline;
    private String gpuServerUrl;
    private Boolean neocortexAvailable;
    private Boolean gpuAvailable;
    private Object gpuInfo;
    private String error;
}
