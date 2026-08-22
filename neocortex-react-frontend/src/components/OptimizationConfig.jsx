import React, { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Slider,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import Panel from '../ui/Panel';
import Readout from '../ui/Readout';
import DeficitChips from '../ui/DeficitChips';
import { percent } from '../lib/format';
import { color } from '../theme/tokens';

const SECONDS_PER_EVALUATION = 0.5;

const SELECTION_METHODS = [
  { value: 'tournament', label: 'Tournament' },
  { value: 'roulette', label: 'Roulette wheel' },
  { value: 'rank', label: 'Rank based' },
];

const SEARCH_SLIDERS = [
  {
    key: 'iterations',
    label: 'Iterations',
    min: 10,
    max: 500,
    step: 10,
    marks: [
      { value: 50, label: 'fast' },
      { value: 100, label: 'balanced' },
      { value: 200, label: 'thorough' },
    ],
    hint: 'More generations converge better and take longer. 100 to 200 is the usual range.',
    format: (value) => value,
  },
  {
    key: 'populationSize',
    label: 'Population size',
    min: 10,
    max: 200,
    step: 10,
    marks: [
      { value: 30, label: 'small' },
      { value: 50, label: 'medium' },
      { value: 100, label: 'large' },
    ],
    hint: 'A larger population explores more of the space per generation. 50 is a good default.',
    format: (value) => value,
  },
  {
    key: 'mutationRate',
    label: 'Mutation rate',
    min: 0.05,
    max: 0.3,
    step: 0.01,
    marks: [
      { value: 0.1, label: '10%' },
      { value: 0.15, label: '15%' },
      { value: 0.2, label: '20%' },
    ],
    hint: 'Higher mutation explores more and settles more slowly. 15% works for most runs.',
    format: percent,
  },
];

const WEIGHT_SLIDERS = [
  { key: 'ntCorrection', label: 'Neurotransmitter correction', min: 0.3, max: 0.9 },
  { key: 'sideEffects', label: 'Fewer side effects', min: 0.0, max: 0.5 },
  { key: 'complexity', label: 'Lower complexity', min: 0.0, max: 0.3 },
  { key: 'speed', label: 'Faster onset', min: 0.0, max: 0.3 },
  { key: 'docking', label: 'Docking score', min: 0.0, max: 0.5, step: 0.05 },
];

const defaultConfig = () => ({
  iterations: 100,
  populationSize: 50,
  mutationRate: 0.15,
  crossoverRate: 0.7,
  eliteCount: 5,
  selectionMethod: 'tournament',
  weights: {
    ntCorrection: 0.5,
    sideEffects: 0.2,
    complexity: 0.1,
    speed: 0.1,
    docking: 0.35,
  },
  useDocking: false,
  dockingExhaustiveness: 8,
  maxTargets: 5,
  minPotency: 0.1,
  maxPotency: 1.0,
  allowedCategories: [
    'reuptake_inhibitors',
    'enzyme_inhibitors',
    'receptor_agonists',
    'receptor_antagonists',
    'gaba_modulators',
    'glutamate_modulators',
  ],
  trialDuration: 168,
  samplingInterval: 24,
  neurons: 50000,
});

function LabelledSlider({ label, hint, value, display, ...sliderProps }) {
  return (
    <Box sx={{ mb: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
        <Typography variant="subtitle2">{label}</Typography>
        <Typography sx={{ fontFamily: 'inherit', fontSize: '0.8rem', color: color.signal }}>
          {display}
        </Typography>
      </Box>
      <Slider value={value} valueLabelDisplay="auto" {...sliderProps} />
      {hint && <Typography variant="caption">{hint}</Typography>}
    </Box>
  );
}

function OptimizationConfig({ disease, onConfigComplete, currentConfig }) {
  const [config, setConfig] = useState(currentConfig || defaultConfig);

  const patch = (slice) => setConfig({ ...config, ...slice });
  const patchWeight = (key, value) => patch({ weights: { ...config.weights, [key]: value } });

  const totalEvaluations = config.iterations * config.populationSize;
  const estimatedMinutes = Math.ceil((totalEvaluations * SECONDS_PER_EVALUATION) / 60);

  return (
    <Box>
      <Panel label="Target" tone="alt">
        <Typography variant="h5" sx={{ mb: 1.5 }}>
          {disease.name}
        </Typography>
        <Typography variant="subtitle2" gutterBottom>
          Deviations to correct
        </Typography>
        <DeficitChips disease={disease} />
      </Panel>

      <Panel label="Search parameters" index="01">
        <Grid container spacing={4}>
          {SEARCH_SLIDERS.map((slider) => (
            <Grid item xs={12} key={slider.key}>
              <LabelledSlider
                label={slider.label}
                hint={slider.hint}
                value={config[slider.key]}
                display={slider.format(config[slider.key])}
                min={slider.min}
                max={slider.max}
                step={slider.step}
                marks={slider.marks}
                onChange={(event, value) => patch({ [slider.key]: value })}
                valueLabelFormat={slider.format}
              />
            </Grid>
          ))}

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Max molecular targets"
              value={config.maxTargets}
              onChange={(event) => patch({ maxTargets: parseInt(event.target.value, 10) })}
              inputProps={{ min: 1, max: 10 }}
              helperText="Caps how complex a candidate compound may be"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Selection method</InputLabel>
              <Select
                value={config.selectionMethod}
                label="Selection method"
                onChange={(event) => patch({ selectionMethod: event.target.value })}
              >
                {SELECTION_METHODS.map((method) => (
                  <MenuItem key={method.value} value={method.value}>
                    {method.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Neurons"
              value={config.neurons}
              onChange={(event) => patch({ neurons: parseInt(event.target.value, 10) })}
              inputProps={{ min: 10000, max: 1000000, step: 10000 }}
              helperText="50K runs fast, 100K reads more accurately"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Trial duration (hours)"
              value={config.trialDuration}
              onChange={(event) => patch({ trialDuration: parseInt(event.target.value, 10) })}
              inputProps={{ min: 12, max: 672, step: 12 }}
              helperText={`${(config.trialDuration / 24).toFixed(1)} days, between 12h and 672h`}
            />
          </Grid>
        </Grid>
      </Panel>

      <Panel label="Molecular docking" index="02">
        <FormControlLabel
          control={
            <Switch
              checked={config.useDocking}
              onChange={(event) => patch({ useDocking: event.target.checked })}
            />
          }
          label={<Typography variant="body2">Validate binding with AutoDock Vina</Typography>}
        />
        <Typography variant="caption" sx={{ display: 'block', mb: 2 }}>
          Checks that candidates actually bind the target protein, picked from the disease. Adds roughly
          30 seconds per candidate.
        </Typography>

        {config.useDocking && (
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Docking exhaustiveness"
                value={config.dockingExhaustiveness}
                onChange={(event) =>
                  patch({ dockingExhaustiveness: parseInt(event.target.value, 10) })
                }
                inputProps={{ min: 4, max: 32, step: 4 }}
                helperText="4 fast, 8 balanced, 32 thorough"
              />
            </Grid>
          </Grid>
        )}
      </Panel>

      <Panel label="Fitness weights" index="03">
        <Alert severity="info" sx={{ mb: 3 }}>
          These set what the search optimizes for. The weights are meant to sum to 1.
        </Alert>
        <Grid container spacing={4}>
          {WEIGHT_SLIDERS.map((weight) => (
            <Grid item xs={12} sm={6} key={weight.key}>
              <LabelledSlider
                label={weight.label}
                value={config.weights[weight.key]}
                display={percent(config.weights[weight.key])}
                min={weight.min}
                max={weight.max}
                step={weight.step || 0.01}
                onChange={(event, value) => patchWeight(weight.key, value)}
                valueLabelFormat={percent}
              />
            </Grid>
          ))}
        </Grid>
      </Panel>

      <Panel label="Estimate" tone="alt">
        <Grid container spacing={3} sx={{ mb: 2 }}>
          <Grid item xs={6} sm={4}>
            <Readout label="Candidates" value={totalEvaluations.toLocaleString()} tone="signal" />
          </Grid>
          <Grid item xs={6} sm={4}>
            <Readout label="Runtime" value={`~${estimatedMinutes}`} unit="min" />
          </Grid>
        </Grid>
        <Alert severity="warning">
          The search simulates {totalEvaluations.toLocaleString()} virtual trials. It needs a stable
          connection for the whole run.
        </Alert>
      </Panel>

      <Button fullWidth variant="contained" size="large" onClick={() => onConfigComplete(config)}>
        Start the search
      </Button>
    </Box>
  );
}

export default OptimizationConfig;
