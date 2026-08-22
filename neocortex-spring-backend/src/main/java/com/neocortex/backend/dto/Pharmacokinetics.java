package com.neocortex.backend.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Pharmacokinetics {
    @Min(0)
    private double halfLife_hours = 24.0;

    @Min(0)
    private double tmax_hours = 2.0;

    @Min(0)
    @Max(1)
    private double bioavailability = 0.7;

    private Double vd_L_kg = 20.0;
}
