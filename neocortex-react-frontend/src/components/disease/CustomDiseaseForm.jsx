import React from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Slider,
  TextField,
  Typography,
} from '@mui/material';
import Panel from '../../ui/Panel';
import {
  DISEASE_CATEGORIES,
  EMPTY_NT_PROFILE,
  NEUROTRANSMITTERS,
} from '../../constants/neurotransmitters';
import { signedPercent } from '../../lib/format';
import { color } from '../../theme/tokens';

const PROFILE_MARKS = [
  { value: -0.7, label: '−70 excess' },
  { value: 0, label: '0' },
  { value: 0.7, label: '+70 deficit' },
];

export const emptyDiseaseComposer = () => ({
  disease: {
    id: '',
    name: '',
    category: 'mood',
    description: '',
    symptoms: [],
    profile: { ...EMPTY_NT_PROFILE },
  },
  symptom: '',
});

function NeurotransmitterRow({ nt, value, onChange }) {
  return (
    <Box sx={{ py: 2, borderTop: `1px solid ${color.rule}` }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={4}>
          <Typography variant="subtitle2">{nt.label}</Typography>
          <Typography variant="caption">{nt.description}</Typography>
        </Grid>
        <Grid item xs={8} md={5}>
          <Slider
            value={value}
            onChange={(event, next) => onChange(next)}
            min={-0.7}
            max={0.7}
            step={0.05}
            marks={PROFILE_MARKS}
            valueLabelDisplay="auto"
            valueLabelFormat={signedPercent}
          />
        </Grid>
        <Grid item xs={4} md={3}>
          <TextField
            fullWidth
            size="small"
            type="number"
            label="Value"
            value={value}
            onChange={(event) => onChange(parseFloat(event.target.value))}
            inputProps={{ min: -0.7, max: 0.7, step: 0.05 }}
          />
        </Grid>
      </Grid>
    </Box>
  );
}

function CustomDiseaseForm({ value, onChange, onSubmit }) {
  const { disease, symptom } = value;

  const patch = (slice) => onChange({ ...value, ...slice });
  const patchDisease = (slice) => patch({ disease: { ...disease, ...slice } });

  const handleProfileChange = (key, next) => {
    patchDisease({ profile: { ...disease.profile, [key]: next } });
  };

  const handleAddSymptom = () => {
    if (!symptom.trim()) return;
    patch({ disease: { ...disease, symptoms: [...disease.symptoms, symptom.trim()] }, symptom: '' });
  };

  const handleRemoveSymptom = (index) => {
    patchDisease({ symptoms: disease.symptoms.filter((_, i) => i !== index) });
  };

  return (
    <Box>
      <Panel label="Identity" index="01">
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Disease name"
              value={disease.name}
              onChange={(event) => patchDisease({ name: event.target.value })}
              placeholder="Treatment-resistant depression"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={disease.category}
                label="Category"
                onChange={(event) => patchDisease({ category: event.target.value })}
              >
                {DISEASE_CATEGORIES.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Description"
              value={disease.description}
              onChange={(event) => patchDisease({ description: event.target.value })}
            />
          </Grid>
        </Grid>
      </Panel>

      <Panel label="Neurotransmitter profile" index="02">
        <Alert severity="info" sx={{ mb: 1 }}>
          Positive numbers mean a deficit, negative numbers mean an excess. Zero is baseline.
        </Alert>
        {NEUROTRANSMITTERS.map((nt) => (
          <NeurotransmitterRow
            key={nt.key}
            nt={nt}
            value={disease.profile[nt.key]}
            onChange={(next) => handleProfileChange(nt.key, next)}
          />
        ))}
      </Panel>

      <Panel label="Symptoms" index="03">
        <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 0.75 }}>
          {disease.symptoms.map((entry, index) => (
            <Chip
              key={`${entry}-${index}`}
              label={entry}
              size="small"
              variant="outlined"
              onDelete={() => handleRemoveSymptom(index)}
            />
          ))}
        </Box>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={9}>
            <TextField
              fullWidth
              label="Add symptom"
              value={symptom}
              onChange={(event) => patch({ symptom: event.target.value })}
              onKeyDown={(event) => {
                if (event.key === 'Enter') handleAddSymptom();
              }}
              placeholder="Persistent low mood"
            />
          </Grid>
          <Grid item xs={3}>
            <Button fullWidth variant="outlined" onClick={handleAddSymptom} disabled={!symptom.trim()}>
              Add
            </Button>
          </Grid>
        </Grid>
      </Panel>

      <Button fullWidth variant="contained" size="large" onClick={onSubmit} disabled={!disease.name}>
        Use this disease model
      </Button>
    </Box>
  );
}

export default CustomDiseaseForm;
