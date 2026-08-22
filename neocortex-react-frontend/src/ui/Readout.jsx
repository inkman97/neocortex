import React from 'react';
import { Box, Typography } from '@mui/material';
import { color, font } from '../theme/tokens';

function Readout({ label, value, unit, tone = 'ink' }) {
  const valueColor = { ink: color.ink, signal: color.signal, mute: color.inkMute }[tone] || color.ink;
  return (
    <Box sx={{ borderLeft: `2px solid ${color.rule}`, pl: 1.5, py: 0.25 }}>
      <Typography
        sx={{
          fontFamily: font.display,
          fontSize: '0.6rem',
          fontWeight: 600,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: color.inkMute,
        }}
      >
        {label}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.75 }}>
        <Typography sx={{ fontFamily: font.mono, fontSize: '1.35rem', fontWeight: 500, color: valueColor }}>
          {value}
        </Typography>
        {unit && (
          <Typography sx={{ fontFamily: font.mono, fontSize: '0.7rem', color: color.inkFaint }}>
            {unit}
          </Typography>
        )}
      </Box>
    </Box>
  );
}

export default Readout;
