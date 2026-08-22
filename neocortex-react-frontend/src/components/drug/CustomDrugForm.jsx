import React from 'react';
import { Alert, Box, Button, Chip, Grid, TextField, Typography } from '@mui/material';
import Panel from '../../ui/Panel';
import TargetChips from '../../ui/TargetChips';
import TargetSelect from './TargetSelect';
import PotencySlider from './PotencySlider';
import MetaboliteEditor from './MetaboliteEditor';
import { DEFAULT_TARGET_KEY } from '../../constants/targets';

export const emptyComposer = () => ({
  drug: {
    id: '',
    name: '',
    class: 'Custom',
    typical_dose_mg: 100,
    dose_range: [10, 500],
    indications: [],
    molecularTargets: [],
    pharmacokinetics: { halfLife_hours: 24, tmax_hours: 2, bioavailability: 0.7 },
    active_metabolites: [],
  },
  target: { target: DEFAULT_TARGET_KEY, potency: 0.5 },
  indication: '',
  metabolitesEnabled: false,
  metabolite: {
    name: '',
    formation_fraction: 0.8,
    halfLife_hours: 24,
    tmax_hours: 4,
    targets: [],
  },
  metaboliteTarget: { target: DEFAULT_TARGET_KEY, potency: 0.5 },
});

function CustomDrugForm({ value, onChange, onSubmit }) {
  const { drug, target, indication, metabolitesEnabled, metabolite, metaboliteTarget } = value;

  const patch = (slice) => onChange({ ...value, ...slice });
  const patchDrug = (slice) => patch({ drug: { ...drug, ...slice } });
  const patchPk = (slice) => patchDrug({ pharmacokinetics: { ...drug.pharmacokinetics, ...slice } });

  const handleAddTarget = () => {
    if (!target.target) return;
    patch({
      drug: {
        ...drug,
        molecularTargets: [
          ...drug.molecularTargets,
          { target: target.target, action: 'mechanism', potency: target.potency },
        ],
      },
      target: { target: DEFAULT_TARGET_KEY, potency: 0.5 },
    });
  };

  const handleRemoveTarget = (index) => {
    patchDrug({ molecularTargets: drug.molecularTargets.filter((_, i) => i !== index) });
  };

  const handleAddIndication = () => {
    if (!indication.trim()) return;
    patch({ drug: { ...drug, indications: [...drug.indications, indication.trim()] }, indication: '' });
  };

  const handleRemoveIndication = (index) => {
    patchDrug({ indications: drug.indications.filter((_, i) => i !== index) });
  };

  const handleAddMetabolite = () => {
    if (!metabolite.name || metabolite.targets.length === 0) {
      alert('Give the metabolite a name and at least one target.');
      return;
    }
    patch({
      drug: { ...drug, active_metabolites: [...drug.active_metabolites, metabolite] },
      metabolite: emptyComposer().metabolite,
    });
  };

  const handleRemoveMetabolite = (index) => {
    patchDrug({ active_metabolites: drug.active_metabolites.filter((_, i) => i !== index) });
  };

  const canSubmit = Boolean(drug.name) && drug.molecularTargets.length > 0;

  return (
    <Box>
      <Panel label="Identity" index="01">
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Drug name"
              value={drug.name}
              onChange={(event) => patchDrug({ name: event.target.value })}
              placeholder="Compound A"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Drug class"
              value={drug.class}
              onChange={(event) => patchDrug({ class: event.target.value })}
              placeholder="SSRI, SNRI, Custom"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="Typical dose (mg)"
              value={drug.typical_dose_mg}
              onChange={(event) => patchDrug({ typical_dose_mg: parseFloat(event.target.value) })}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="Min dose (mg)"
              value={drug.dose_range[0]}
              onChange={(event) =>
                patchDrug({ dose_range: [parseFloat(event.target.value), drug.dose_range[1]] })
              }
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="Max dose (mg)"
              value={drug.dose_range[1]}
              onChange={(event) =>
                patchDrug({ dose_range: [drug.dose_range[0], parseFloat(event.target.value)] })
              }
            />
          </Grid>
        </Grid>
      </Panel>

      <Panel label="Molecular targets" index="02">
        <Alert severity="info" sx={{ mb: 2 }}>
          Target names have to match the simulator's mechanism keys exactly. Pick them from the list.
        </Alert>

        <Box sx={{ mb: 3 }}>
          <TargetChips targets={drug.molecularTargets} onDelete={handleRemoveTarget} />
        </Box>

        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <TargetSelect value={target.target} onChange={(next) => patch({ target: { ...target, target: next } })} />
          </Grid>
          <Grid item xs={12} md={4}>
            <PotencySlider
              value={target.potency}
              onChange={(potency) => patch({ target: { ...target, potency } })}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button fullWidth variant="outlined" onClick={handleAddTarget}>
              Add
            </Button>
          </Grid>
        </Grid>
      </Panel>

      <Panel label="Pharmacokinetics" index="03">
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              type="number"
              label="Half-life (hours)"
              value={drug.pharmacokinetics.halfLife_hours}
              onChange={(event) => patchPk({ halfLife_hours: parseFloat(event.target.value) })}
              helperText="96h is long (fluoxetine), 5h is short (venlafaxine)"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              type="number"
              label="Tmax (hours)"
              value={drug.pharmacokinetics.tmax_hours}
              onChange={(event) => patchPk({ tmax_hours: parseFloat(event.target.value) })}
              helperText="Time to peak concentration"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              type="number"
              label="Bioavailability"
              value={drug.pharmacokinetics.bioavailability}
              onChange={(event) => patchPk({ bioavailability: parseFloat(event.target.value) })}
              inputProps={{ min: 0, max: 1, step: 0.1 }}
              helperText="0.7 means 70% absorbed"
            />
          </Grid>
        </Grid>
      </Panel>

      <MetaboliteEditor
        metabolites={drug.active_metabolites}
        enabled={metabolitesEnabled}
        onEnabledChange={(metabolitesEnabled) => patch({ metabolitesEnabled })}
        draft={metabolite}
        onDraftChange={(next) => patch({ metabolite: next })}
        targetDraft={metaboliteTarget}
        onTargetDraftChange={(next) => patch({ metaboliteTarget: next })}
        onAddMetabolite={handleAddMetabolite}
        onRemoveMetabolite={handleRemoveMetabolite}
      />

      <Panel label="Indications" index="04">
        <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 0.75 }}>
          {drug.indications.map((entry, index) => (
            <Chip
              key={`${entry}-${index}`}
              label={entry}
              size="small"
              variant="outlined"
              onDelete={() => handleRemoveIndication(index)}
            />
          ))}
        </Box>

        <Grid container spacing={2} alignItems="center">
          <Grid item xs={9}>
            <TextField
              fullWidth
              label="Add indication"
              value={indication}
              onChange={(event) => patch({ indication: event.target.value })}
              onKeyDown={(event) => {
                if (event.key === 'Enter') handleAddIndication();
              }}
              placeholder="depression, anxiety"
            />
          </Grid>
          <Grid item xs={3}>
            <Button fullWidth variant="outlined" onClick={handleAddIndication}>
              Add
            </Button>
          </Grid>
        </Grid>
      </Panel>

      <Button fullWidth variant="contained" size="large" onClick={onSubmit} disabled={!canSubmit}>
        Use this compound
        {drug.active_metabolites.length > 0 && (
          <Typography component="span" sx={{ ml: 1, fontFamily: 'inherit' }}>
            (+{drug.active_metabolites.length} metabolites)
          </Typography>
        )}
      </Button>
    </Box>
  );
}

export default CustomDrugForm;
