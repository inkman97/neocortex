import { NEUROTRANSMITTERS } from '../constants/neurotransmitters';

const DEFAULT_HILL = 1.5;
const DEFAULT_VD_L_KG = 20.0;

const adaptTarget = (target) => ({
  target: target.target,
  action: target.action,
  potency: target.potency,
  hill: target.hill || DEFAULT_HILL,
});

const adaptMetabolite = (metabolite) => ({
  name: metabolite.name,
  formation_fraction: metabolite.formation_fraction,
  halfLife_hours: metabolite.halfLife,
  tmax_hours: metabolite.tmax,
  targets: metabolite.targets.map(adaptTarget),
});

const fallbackDrug = (drug) => ({
  name: drug.name || drug.id || 'Unknown Drug',
  drug_class: drug.drug_class || drug.class || 'Unknown',
  molecularTargets: [],
  pharmacokinetics: {
    halfLife_hours: 24,
    tmax_hours: 2,
    bioavailability: 0.7,
    vd_L_kg: DEFAULT_VD_L_KG,
  },
  active_metabolites: [],
});

export const adaptDrugForBackend = (drug) => {
  if (drug.targets && drug.pk) {
    return {
      name: drug.name || drug.id,
      drug_class: drug.class,
      molecularTargets: drug.targets.map(adaptTarget),
      pharmacokinetics: {
        halfLife_hours: drug.pk.halfLife,
        tmax_hours: drug.pk.tmax,
        bioavailability: drug.pk.bioavailability,
        vd_L_kg: drug.pk.vd_L_kg || DEFAULT_VD_L_KG,
      },
      active_metabolites: drug.active_metabolites
        ? drug.active_metabolites.map(adaptMetabolite)
        : [],
    };
  }

  if (drug.molecularTargets && drug.pharmacokinetics) {
    return {
      name: drug.name,
      drug_class: drug.drug_class,
      molecularTargets: drug.molecularTargets,
      pharmacokinetics: drug.pharmacokinetics,
      active_metabolites: drug.active_metabolites || [],
    };
  }

  return fallbackDrug(drug);
};

export const adaptDiseaseForBackend = (disease) => {
  if (!disease.profile) return disease;

  const deficits = NEUROTRANSMITTERS.reduce(
    (acc, nt) => ({ ...acc, [nt.deficitKey]: disease.profile[nt.key] || 0 }),
    {}
  );

  return {
    name: disease.name || disease.id,
    category: disease.category,
    description: disease.description,
    ...deficits,
  };
};

export const adaptDiseaseForDiscovery = (disease) =>
  NEUROTRANSMITTERS.reduce((acc, nt) => ({ ...acc, [nt.deficitKey]: disease.profile?.[nt.key] || 0 }), {
    name: disease.name,
  });
