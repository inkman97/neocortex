package com.neocortex.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TrialResponse {
    private String trial_id;
    private boolean success;
    private List<TrialTimepoint> timepoints;
    private boolean used_neocortex;
    private int neurons;
    private int duration_hours;
    private Map<String, Object> gpu_info;
    private String fallback_reason;
}
