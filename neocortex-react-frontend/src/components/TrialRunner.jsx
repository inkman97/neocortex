import React, { useState } from 'react';
import { Alert, Backdrop, Box, Button, CircularProgress, Grid, Slider, Typography } from '@mui/material';
import api from '../api';
import Panel from '../ui/Panel';
import Readout from '../ui/Readout';
import { adaptDiseaseForBackend, adaptDrugForBackend } from '../lib/backendAdapters';
import { compactCount, pluralDays } from '../lib/format';
import { color, font } from '../theme/tokens';

const SAMPLING_INTERVAL_HOURS = 24;
const DEFAULT_DOSE_MG = 20;

const NEURON_MARKS = [
  { value: 10000, label: '10K' },
  { value: 500000, label: '500K' },
  { value: 1000000, label: '1M' },
];

const DURATION_MARKS = [
  { value: 1, label: '1d' },
  { value: 7, label: '1w' },
  { value: 14, label: '2w' },
];

const estimateRuntime = (durationDays) => {
  if (durationDays <= 2) return '1–3 minutes';
  if (durationDays <= 4) return '3–7 minutes';
  return '5–15 minutes';
};

function TrialRunner({ drug, disease, onTrialCompleted }) {
  const [neurons, setNeurons] = useState(100000);
  const [durationDays, setDurationDays] = useState(7);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);

  const handleRunTrial = async () => {
    setIsRunning(true);
    setError(null);

    const adaptedDrug = adaptDrugForBackend(drug);
    const adaptedDisease = adaptDiseaseForBackend(disease);

    if (!adaptedDrug.molecularTargets || adaptedDrug.molecularTargets.length === 0) {
      setError('This compound has no molecular targets. Add at least one before running the trial.');
      setIsRunning(false);
      return;
    }

    const trialRequest = {
      drug: adaptedDrug,
      disease: adaptedDisease,
      dose_mg: drug.typical_dose_mg || DEFAULT_DOSE_MG,
      typical_dose_mg: drug.typical_dose_mg || DEFAULT_DOSE_MG,
      neurons,
      duration_hours: durationDays * 24,
      sampling_interval_hours: SAMPLING_INTERVAL_HOURS,
    };

    try {
      const response = await api.post('/trials/simulate', trialRequest);
      onTrialCompleted(response.data);
    } catch (requestError) {
      setError(requestError.response?.data?.message || requestError.message || 'The trial did not run.');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Panel label="Model size" index="n">
            <Readout label="Neurons" value={compactCount(neurons)} />
            <Slider
              value={neurons}
              onChange={(event, next) => setNeurons(next)}
              min={10000}
              max={1000000}
              step={10000}
              marks={NEURON_MARKS}
              sx={{ mt: 3 }}
            />
            <Typography variant="caption">
              More neurons make the model more faithful and the run slower.
            </Typography>
          </Panel>
        </Grid>

        <Grid item xs={12} md={6}>
          <Panel label="Exposure" index="t">
            <Readout label="Duration" value={durationDays} unit={durationDays === 1 ? 'day' : 'days'} />
            <Slider
              value={durationDays}
              onChange={(event, next) => setDurationDays(next)}
              min={1}
              max={14}
              step={1}
              marks={DURATION_MARKS}
              sx={{ mt: 3 }}
            />
            <Typography variant="caption">
              Clinical antidepressant response is usually read at one to two weeks.
            </Typography>
          </Panel>
        </Grid>
      </Grid>

      <Panel label="Run sheet" tone="alt">
        <Grid container spacing={3}>
          <Grid item xs={6} sm={3}>
            <Readout label="Drug" value={drug.name} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <Readout label="Disease" value={disease.name} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <Readout label="Neurons" value={compactCount(neurons)} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <Readout label="Duration" value={pluralDays(durationDays)} />
          </Grid>
        </Grid>
      </Panel>

      <Button fullWidth variant="contained" size="large" onClick={handleRunTrial} disabled={isRunning}>
        {isRunning ? 'Simulating…' : 'Run the trial'}
      </Button>

      <Backdrop
        open={isRunning}
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: 'rgba(25,27,26,0.88)' }}
      >
        <Box sx={{ textAlign: 'center', color: color.panel }}>
          <CircularProgress color="inherit" size={44} />
          <Typography
            sx={{
              mt: 3,
              fontFamily: font.display,
              fontSize: '0.72rem',
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
            }}
          >
            Simulating
          </Typography>
          <Typography sx={{ mt: 1, fontFamily: font.mono, fontSize: '0.8rem' }}>
            {neurons.toLocaleString()} neurons · {pluralDays(durationDays)} ·{' '}
            {estimateRuntime(durationDays)}
          </Typography>
        </Box>
      </Backdrop>
    </Box>
  );
}

export default TrialRunner;
