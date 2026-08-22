import React from 'react';
import { Box, Typography } from '@mui/material';
import { color, font } from '../theme/tokens';

function Panel({ label, index, action, dense = false, tone = 'panel', children }) {
  return (
    <Box
      component="section"
      sx={{
        backgroundColor: tone === 'alt' ? color.panelAlt : color.panel,
        border: `1px solid ${color.rule}`,
        mb: 3,
      }}
    >
      {label && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            px: dense ? 2 : 2.5,
            py: 1.25,
            borderBottom: `1px solid ${color.rule}`,
          }}
        >
          {index && (
            <Typography sx={{ fontFamily: font.mono, fontSize: '0.68rem', color: color.signal }}>
              {index}
            </Typography>
          )}
          <Typography
            sx={{
              fontFamily: font.display,
              fontSize: '0.68rem',
              fontWeight: 600,
              letterSpacing: '0.16em',
              textTransform: 'uppercase',
            }}
          >
            {label}
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          {action}
        </Box>
      )}
      <Box sx={{ p: dense ? 2 : 2.5 }}>{children}</Box>
    </Box>
  );
}

export default Panel;
