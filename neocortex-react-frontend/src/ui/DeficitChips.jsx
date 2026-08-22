import React from 'react';
import { Box, Chip, Typography } from '@mui/material';
import { activeDeficits } from '../constants/neurotransmitters';
import { signedPercent } from '../lib/format';
import { color } from '../theme/tokens';

function DeficitChips({ disease, empty = 'No deviation from baseline' }) {
  const deficits = activeDeficits(disease);

  if (deficits.length === 0) {
    return <Typography variant="caption">{empty}</Typography>;
  }

  return (
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75 }}>
      {deficits.map((nt) => (
        <Chip
          key={nt.key}
          size="small"
          label={`${nt.code} ${signedPercent(nt.value)}`}
          sx={{
            backgroundColor: nt.value > 0 ? color.signalWash : color.affirmWash,
            color: color.ink,
            border: `1px solid ${nt.value > 0 ? color.signal : color.affirm}`,
          }}
        />
      ))}
    </Box>
  );
}

export default DeficitChips;
