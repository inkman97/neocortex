import React from 'react';
import { Box, Slider, Typography } from '@mui/material';
import { percent } from '../../lib/format';

function PotencySlider({ value, onChange, size }) {
  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Potency {percent(value)}
      </Typography>
      <Slider
        value={value}
        onChange={(event, next) => onChange(next)}
        min={0}
        max={1}
        step={0.05}
        size={size}
        valueLabelDisplay="auto"
        valueLabelFormat={(next) => percent(next)}
      />
    </Box>
  );
}

export default PotencySlider;
