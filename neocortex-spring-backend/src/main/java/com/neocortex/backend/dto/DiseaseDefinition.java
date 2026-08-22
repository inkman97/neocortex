package com.neocortex.backend.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DiseaseDefinition {
    @NotBlank
    private String name;

    @Min(-1)
    @Max(1)
    private double serotonin_deficit = 0.0;

    @Min(-1)
    @Max(1)
    private double dopamine_deficit = 0.0;

    @Min(-1)
    @Max(1)
    private double noradrenaline_deficit = 0.0;

    @Min(-1)
    @Max(1)
    private double acetylcholine_deficit = 0.0;

    // ============== AGGIUNTI (6 NT SYSTEM) ==============
    @Min(-1)
    @Max(1)
    private double gaba_deficit = 0.0;

    @Min(-1)
    @Max(1)
    private double glutamate_deficit = 0.0;
    // ===================================================
}