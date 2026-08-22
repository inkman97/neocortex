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
public class MolecularTarget {
    @NotBlank
    private String target;  // SERT, DAT, D2, etc.

    @NotBlank
    private String action;  // inhibitor, antagonist, etc.

    @Min(0)
    @Max(1)
    private double potency;  // 0-1

    private Double hill;

    private Double ki_nM;  // Optional
}
