import React from 'react';
import { Box, Chip } from '@mui/material';
import { targetShortLabel } from '../constants/targets';
import { percent } from '../lib/format';
import { color } from '../theme/tokens';

function TargetChips({ targets = [], onDelete, tone = 'signal' }) {
  const border = tone === 'plate' ? color.plate : color.signal;
  const wash = tone === 'plate' ? color.plateWash : color.signalWash;

  return (
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75 }}>
      {targets.map((target, index) => (
        <Chip
          key={`${target.target}-${index}`}
          size="small"
          label={`${targetShortLabel(target.target)} ${percent(target.potency)}`}
          onDelete={onDelete ? () => onDelete(index) : undefined}
          sx={{ backgroundColor: wash, border: `1px solid ${border}`, color: color.ink }}
        />
      ))}
    </Box>
  );
}

export default TargetChips;
