package com.neocortex.backend.service.pharmacology;

import com.neocortex.backend.dto.MolecularTarget;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class DrugEffectCalculator {

    private static final double DEFAULT_HILL = 1.5;

    public Map<String, DrugEffect> calculate(List<MolecularTarget> targets, double doseMg, double typicalDoseMg) {
        Map<String, DrugEffect> effects = new HashMap<>();
        if (targets == null) {
            return effects;
        }

        double doseRatio = doseMg / typicalDoseMg;

        for (MolecularTarget target : targets) {
            double potency = target.getPotency();
            double hill = target.getHill() != null ? target.getHill() : DEFAULT_HILL;
            double finalEffect = potency * applyHillTransform(doseRatio, hill);

            for (TargetEffectCatalog.Contribution contribution :
                    TargetEffectCatalog.contributionsFor(target.getTarget().toUpperCase())) {

                DrugEffect effect = new DrugEffect(potency, hill, finalEffect * contribution.factor());

                if (contribution.accumulation() == TargetEffectCatalog.Accumulation.ADD) {
                    effects.merge(contribution.neurotransmitter(), effect,
                            (existing, incoming) -> existing.combinedWith(incoming, hill));
                } else {
                    effects.put(contribution.neurotransmitter(), effect);
                }
            }
        }

        return effects;
    }

    public double effectOn(Map<String, DrugEffect> effects, String neurotransmitter) {
        DrugEffect effect = effects.get(neurotransmitter);
        return effect != null ? effect.getDoseEffect() : 0.0;
    }

    private double applyHillTransform(double doseRatio, double hill) {
        double numerator = Math.pow(doseRatio, hill);
        return numerator / (1.0 + numerator);
    }
}
