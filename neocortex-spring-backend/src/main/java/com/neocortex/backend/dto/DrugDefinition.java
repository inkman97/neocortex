package com.neocortex.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DrugDefinition {
    @NotBlank
    private String name;

    private String drug_class;

    @NotEmpty
    private List<MolecularTarget> molecularTargets;

    @NotNull
    private Pharmacokinetics pharmacokinetics;
    private List<ActiveMetaboliteDTO> active_metabolites;
}
