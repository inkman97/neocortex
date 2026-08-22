package com.neocortex.backend.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TrialRequest {
    @NotNull
    private DrugDefinition drug;

    @NotNull
    private DiseaseDefinition disease;

    @Min(0)
    private double dose_mg;

    @Min(0)
    private double typical_dose_mg;

    @Min(10000)
    @Max(1000000)
    private int neurons = 100000;

    @Min(1)
    @Max(8760)
    private int duration_hours = 168;

    @Min(1)
    @Max(168)
    private int sampling_interval_hours = 24;
}
