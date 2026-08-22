import React from 'react';
import { Box, Typography } from '@mui/material';
import { ResponsiveContainer } from 'recharts';
import { color, font } from '../theme/tokens';

function ChartWell({ caption, height = 320, children }) {
  return (
    <Box>
      {caption && (
        <Typography sx={{ fontFamily: font.mono, fontSize: '0.7rem', color: color.inkMute, mb: 1 }}>
          {caption}
        </Typography>
      )}
      <Box className="chart-well" sx={{ p: 1.5 }}>
        <ResponsiveContainer width="100%" height={height}>
          {children}
        </ResponsiveContainer>
      </Box>
    </Box>
  );
}

export default ChartWell;
