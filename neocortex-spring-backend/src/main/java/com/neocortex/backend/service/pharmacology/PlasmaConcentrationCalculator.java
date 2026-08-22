package com.neocortex.backend.service.pharmacology;

import com.neocortex.backend.dto.ActiveMetaboliteDTO;
import com.neocortex.backend.dto.Pharmacokinetics;
import org.springframework.stereotype.Component;

@Component
public class PlasmaConcentrationCalculator {

    private static final double LN_2 = 0.693;
    private static final double ABSORPTION_RATE_FACTOR = 3.0;
    private static final double METABOLITE_PEAK_FACTOR = 0.8;

    public double parentConcentration(double hours, Pharmacokinetics pk) {
        if (hours <= 0) {
            return 0.0;
        }

        double tmax = pk.getTmax_hours();
        double bioavailability = pk.getBioavailability();
        double ke = eliminationRate(pk.getHalfLife_hours());
        double ka = ABSORPTION_RATE_FACTOR / tmax;

        double drugLevel;
        if (hours <= tmax * 2) {
            double absorption = 1.0 - Math.exp(-ka * hours);
            double elimination = Math.exp(-ke * hours);
            drugLevel = bioavailability * absorption * elimination;
        } else {
            double peakConcentration =
                    bioavailability * (1.0 - Math.exp(-ka * tmax)) * Math.exp(-ke * tmax);
            drugLevel = peakConcentration * Math.exp(-ke * (hours - tmax));
        }

        return Math.min(1.0, drugLevel);
    }

    public double metaboliteConcentration(double hours, Pharmacokinetics parentPk, ActiveMetaboliteDTO metabolite) {
        if (hours <= 0) {
            return 0.0;
        }

        double keMetabolite = eliminationRate(metabolite.getHalfLife_hours());
        double formationFraction = metabolite.getFormation_fraction();
        double tmaxMetabolite = metabolite.getTmax_hours();

        double concentration;
        if (hours < tmaxMetabolite) {
            double formationFactor = hours / tmaxMetabolite;
            concentration = formationFraction * formationFactor * parentConcentration(hours, parentPk);
        } else {
            double timeFromPeak = hours - tmaxMetabolite;
            double peakMetabolite =
                    formationFraction * parentPk.getBioavailability() * METABOLITE_PEAK_FACTOR;
            concentration = peakMetabolite * Math.exp(-keMetabolite * timeFromPeak);
        }

        return Math.min(1.0, concentration);
    }

    private double eliminationRate(double halfLifeHours) {
        return LN_2 / halfLifeHours;
    }
}
