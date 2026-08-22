package com.neocortex.backend.dto;

import lombok.Data;
import java.util.List;

/**
 * Active metabolite definition
 */
@Data
public class ActiveMetaboliteDTO {
    private String name;
    private Double formation_fraction;  // 0-1, fraction of parent converted
    private Double halfLife_hours;
    private Double tmax_hours;
    private List<MolecularTarget> targets;  // Same as parent drug targets
}