import { trace } from '../theme/tokens';

export const NEUROCHEM_SERIES = [
  { key: 'serotonin', name: 'Serotonin (5HT)', stroke: trace.serotonin },
  { key: 'dopamine', name: 'Dopamine (DA)', stroke: trace.dopamine },
  { key: 'noradrenaline', name: 'Noradrenaline (NE)', stroke: trace.noradrenaline },
  { key: 'acetylcholine', name: 'Acetylcholine (ACh)', stroke: trace.acetylcholine },
  { key: 'gaba', name: 'GABA', stroke: trace.gaba },
  { key: 'glutamate', name: 'Glutamate', stroke: trace.glutamate },
];

export const MENTAL_STATE_SERIES = [
  { key: 'arousal', name: 'Arousal', stroke: trace.arousal },
  { key: 'valence', name: 'Valence', stroke: trace.valence },
];

export const PHYSIO_SERIES = {
  heart_rate: { name: 'Heart rate', short: 'HR', stroke: trace.heartRate },
  respiratory_rate: { name: 'Respiratory rate', short: 'RR', stroke: trace.respiratoryRate },
  skin_conductance: { name: 'Skin conductance', short: 'SC', stroke: trace.skinConductance },
  muscle_tension: { name: 'Muscle tension', short: 'MT', stroke: trace.muscleTension },
  gut_feeling: { name: 'Gut feeling', short: 'Gut', stroke: trace.gutFeeling },
  pain: { name: 'Pain', short: 'Pain', stroke: trace.pain },
  fatigue: { name: 'Fatigue', short: 'Fatigue', stroke: trace.fatigue },
  temperature: { name: 'Temperature', short: 'Temp', stroke: trace.temperature },
};

export const PHYSIO_KEYS = Object.keys(PHYSIO_SERIES);

export const PHYSIO_GROUPS = [
  {
    id: 'cardio',
    label: 'Cardiorespiratory',
    blurb: 'Baseline sits between 40 and 60. Below that reads as bradycardia or slow breathing, above it as tachycardia or hyperventilation.',
    keys: ['heart_rate', 'respiratory_rate'],
    height: 340,
  },
  {
    id: 'stress',
    label: 'Stress & tension',
    blurb: 'Skin conductance tracks sympathetic activity. Higher values mean more arousal and more muscular guarding.',
    keys: ['skin_conductance', 'muscle_tension'],
    height: 340,
  },
  {
    id: 'wellbeing',
    label: 'Wellbeing',
    blurb: 'Gut feeling reads better when high. Pain and fatigue read better when low.',
    keys: ['gut_feeling', 'pain', 'fatigue'],
    height: 340,
  },
  {
    id: 'all',
    label: 'All parameters',
    blurb: 'Every physiological channel on one axis.',
    keys: PHYSIO_KEYS,
    height: 400,
    compact: true,
  },
];
