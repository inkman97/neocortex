import React from 'react';
import { Box, Grid, Typography } from '@mui/material';
import Panel from '../../ui/Panel';
import { color, font } from '../../theme/tokens';

const gradeColor = (value, good, fair, invert = false) => {
  const passesGood = invert ? value < good : value > good;
  const passesFair = invert ? value < fair : value > fair;
  if (passesGood) return color.affirm;
  if (passesFair) return color.caution;
  return color.signal;
};

const propertyCells = (properties) => [
  {
    label: 'Molecular weight',
    value: properties.molecular_weight.toFixed(1),
    unit: 'g/mol',
  },
  { label: 'LogP', value: properties.logp.toFixed(2), unit: 'lipophilicity' },
  { label: 'H-bond donors', value: properties.hbd },
  { label: 'H-bond acceptors', value: properties.hba },
  {
    label: 'QED',
    value: properties.qed_score.toFixed(2),
    unit: 'drug-likeness',
    tone: gradeColor(properties.qed_score, 0.7, 0.5),
  },
  {
    label: 'SA score',
    value: properties.sa_score.toFixed(1),
    unit: 'synthesizability',
    tone: gradeColor(properties.sa_score, 4, 6, true),
  },
  {
    label: 'Lipinski',
    value: properties.is_drug_like ? 'Pass' : 'Fail',
    unit: `${properties.lipinski_violations} violations`,
    tone: properties.is_drug_like ? color.affirm : color.signal,
  },
  {
    label: 'Synthesizable',
    value: properties.is_synthesizable ? 'Yes' : 'Difficult',
    tone: properties.is_synthesizable ? color.affirm : color.caution,
  },
];

function PropertyCell({ label, value, unit, tone }) {
  return (
    <Grid item xs={6} sm={4} lg={3}>
      <Box sx={{ borderTop: `2px solid ${tone || color.rule}`, pt: 1.25 }}>
        <Typography variant="subtitle2">{label}</Typography>
        <Typography sx={{ fontFamily: font.mono, fontSize: '1.2rem', color: tone || color.ink }}>
          {value}
        </Typography>
        {unit && <Typography variant="caption">{unit}</Typography>}
      </Box>
    </Grid>
  );
}

function MolecularStructure({ structure }) {
  const alternatives = structure.alternatives || [];

  return (
    <Panel label="Generated structure" index="smi">
      <Box
        sx={{
          p: 2,
          mb: 3,
          backgroundColor: color.panelAlt,
          border: `1px solid ${color.rule}`,
          borderLeft: `3px solid ${color.signal}`,
        }}
      >
        <Typography variant="subtitle2" gutterBottom>
          SMILES
        </Typography>
        <Typography sx={{ fontFamily: font.mono, fontSize: '0.95rem', wordBreak: 'break-all' }}>
          {structure.smiles}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {propertyCells(structure.properties).map((cell) => (
          <PropertyCell key={cell.label} {...cell} />
        ))}
      </Grid>

      {alternatives.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="subtitle2" gutterBottom>
            Alternatives
          </Typography>
          {alternatives.slice(0, 3).map((alternative, index) => (
            <Grid
              container
              key={`${alternative.smiles}-${index}`}
              spacing={2}
              sx={{ py: 1, borderTop: `1px solid ${color.rule}` }}
            >
              <Grid item xs={12} sm={8}>
                <Typography sx={{ fontFamily: font.mono, fontSize: '0.74rem', wordBreak: 'break-all' }}>
                  {alternative.smiles}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={2}>
                <Typography sx={{ fontFamily: font.mono, fontSize: '0.74rem', color: color.inkMute }}>
                  QED {alternative.qed.toFixed(2)}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={2}>
                <Typography sx={{ fontFamily: font.mono, fontSize: '0.74rem', color: color.inkMute }}>
                  SA {alternative.sa_score.toFixed(1)}
                </Typography>
              </Grid>
            </Grid>
          ))}
        </Box>
      )}
    </Panel>
  );
}

export default MolecularStructure;
