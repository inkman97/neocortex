import React from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  CircularProgress,
  Grid,
  Slider,
  TextField,
  Typography,
} from '@mui/material';
import Panel from '../../ui/Panel';
import TargetChips from '../../ui/TargetChips';
import { doseRangeOf, doseStepFor } from '../../lib/dosing';
import { color, font } from '../../theme/tokens';

function DrugCard({ drug, selected, onSelect }) {
  return (
    <Card
      onClick={onSelect}
      sx={{
        height: '100%',
        cursor: 'pointer',
        display: 'flex',
        flexDirection: 'column',
        borderColor: selected ? color.signal : color.rule,
        backgroundColor: selected ? color.signalWash : color.panel,
        '&:hover': { borderColor: color.ruleStrong },
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography sx={{ fontFamily: font.display, fontSize: '1.05rem', fontWeight: 600 }}>
          {drug.name}
        </Typography>
        <Typography sx={{ fontFamily: font.mono, fontSize: '0.7rem', color: color.inkMute, mb: 1.5 }}>
          {drug.class || 'unclassified'}
          {drug.typical_dose_mg ? ` · ${drug.typical_dose_mg} mg typical` : ''}
          {Array.isArray(drug.dose_range) && drug.dose_range.length === 2
            ? ` · ${drug.dose_range[0]}–${drug.dose_range[1]} mg`
            : ''}
        </Typography>
        <TargetChips targets={drug.molecularTargets || []} />
        {drug.active_metabolites?.length > 0 && (
          <Typography sx={{ fontFamily: font.mono, fontSize: '0.68rem', color: color.plate, mt: 1 }}>
            {drug.active_metabolites.length} active metabolite(s)
          </Typography>
        )}
      </CardContent>
      <CardActions>
        <Button size="small" fullWidth variant={selected ? 'contained' : 'outlined'}>
          {selected ? 'Selected' : 'Select'}
        </Button>
      </CardActions>
    </Card>
  );
}

function DoseSelector({ drug, dose, onDoseChange, onConfirm }) {
  const range = doseRangeOf(drug);
  const step = doseStepFor(range);

  return (
    <Panel label={`Dose · ${drug.name}`} index="mg">
      <Grid container spacing={4} alignItems="center">
        <Grid item xs={12} md={8}>
          <Slider
            value={dose}
            onChange={(event, next) => onDoseChange(next)}
            min={range.min}
            max={range.max}
            step={step}
            marks={[
              { value: range.min, label: `${range.min}` },
              { value: drug.typical_dose_mg, label: `${drug.typical_dose_mg} typical` },
              { value: range.max, label: `${range.max}` },
            ]}
            valueLabelDisplay="on"
            valueLabelFormat={(value) => `${value} mg`}
            sx={{ mt: 4 }}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            type="number"
            label="Dose (mg)"
            value={dose}
            onChange={(event) => onDoseChange(parseFloat(event.target.value))}
            inputProps={{ min: range.min, max: range.max, step }}
          />
        </Grid>
      </Grid>
      <Button fullWidth variant="contained" size="large" onClick={onConfirm} sx={{ mt: 3 }}>
        Confirm drug and dose
      </Button>
    </Panel>
  );
}

function DrugLibrary({ drugs, loading, selectedDrug, selectedDose, onSelectDrug, onDoseChange, onConfirm }) {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress size={28} />
      </Box>
    );
  }

  if (drugs.length === 0) {
    return (
      <Alert severity="warning">
        The library came back empty. Check the backend connection, or design a compound in the next tab.
      </Alert>
    );
  }

  return (
    <>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {drugs.map((drug, index) => (
          <Grid item xs={12} sm={6} lg={4} key={drug.id || drug.name || index}>
            <DrugCard
              drug={drug}
              selected={selectedDrug?.id === drug.id}
              onSelect={() => onSelectDrug(drug)}
            />
          </Grid>
        ))}
      </Grid>

      {selectedDrug && (
        <DoseSelector
          drug={selectedDrug}
          dose={selectedDose}
          onDoseChange={onDoseChange}
          onConfirm={onConfirm}
        />
      )}
    </>
  );
}

export default DrugLibrary;
