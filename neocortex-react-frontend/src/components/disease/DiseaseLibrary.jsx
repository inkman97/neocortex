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
  Typography,
} from '@mui/material';
import DeficitChips from '../../ui/DeficitChips';
import { color, font } from '../../theme/tokens';

function DiseaseCard({ disease, selected, onSelect }) {
  const displayName = disease.name || disease.id;
  const symptoms = Array.isArray(disease.symptoms) ? disease.symptoms : [];

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
          {displayName}
        </Typography>
        {disease.category && (
          <Typography sx={{ fontFamily: font.mono, fontSize: '0.7rem', color: color.inkMute }}>
            {disease.category}
          </Typography>
        )}
        {disease.description && (
          <Typography variant="body2" sx={{ mt: 1.25 }}>
            {disease.description}
          </Typography>
        )}
        {symptoms.length > 0 && (
          <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
            {symptoms.slice(0, 2).join(', ')}
            {symptoms.length > 2 ? '…' : ''}
          </Typography>
        )}
        <Box sx={{ mt: 2 }}>
          <DeficitChips disease={disease} />
        </Box>
      </CardContent>
      <CardActions>
        <Button size="small" fullWidth variant={selected ? 'contained' : 'outlined'}>
          {selected ? 'Selected' : 'Select'}
        </Button>
      </CardActions>
    </Card>
  );
}

function DiseaseLibrary({ diseases, loading, currentDisease, onSelect }) {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress size={28} />
      </Box>
    );
  }

  if (diseases.length === 0) {
    return (
      <Alert severity="warning">
        The library came back empty. Check the backend connection, or define a disease in the next tab.
      </Alert>
    );
  }

  return (
    <Grid container spacing={2}>
      {diseases.map((disease, index) => (
        <Grid item xs={12} sm={6} lg={4} key={disease.id || disease.name || index}>
          <DiseaseCard
            disease={disease}
            selected={Boolean(
              currentDisease &&
                (currentDisease.name === disease.name || currentDisease.id === disease.id)
            )}
            onSelect={() => onSelect(disease)}
          />
        </Grid>
      ))}
    </Grid>
  );
}

export default DiseaseLibrary;
