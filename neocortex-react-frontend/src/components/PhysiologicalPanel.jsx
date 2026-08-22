import React from 'react';
import { Box, Grid, LinearProgress, Typography } from '@mui/material';
import Panel from '../ui/Panel';
import { PHYSIO_DESCRIPTIONS, PHYSIO_STATUS } from './physiology/statusScales';
import { PHYSIO_KEYS, PHYSIO_SERIES } from '../constants/series';
import { percent, timepointHours } from '../lib/format';
import { color, font } from '../theme/tokens';

const TONE_COLOR = {
  affirm: color.affirm,
  caution: color.caution,
  signal: color.signal,
  plate: color.plate,
  mute: color.inkMute,
};

function ParameterGauge({ paramKey, value }) {
  const status = PHYSIO_STATUS[paramKey](value ?? 0);
  const tone = TONE_COLOR[status.tone] || color.ink;

  return (
    <Box sx={{ borderTop: `2px solid ${tone}`, pt: 1.5 }}>
      <Typography variant="subtitle2" sx={{ color: color.ink }}>
        {PHYSIO_SERIES[paramKey].name}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mt: 0.5, mb: 1 }}>
        <Typography sx={{ fontFamily: font.mono, fontSize: '1.4rem', color: tone }}>
          {percent(value)}
        </Typography>
        <Typography sx={{ fontFamily: font.mono, fontSize: '0.7rem', color: color.inkMute }}>
          {status.label}
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={(value ?? 0) * 100}
        sx={{ '& .MuiLinearProgress-bar': { backgroundColor: tone } }}
      />
      <Typography variant="caption" sx={{ display: 'block', mt: 0.75 }}>
        {PHYSIO_DESCRIPTIONS[paramKey]}
      </Typography>
    </Box>
  );
}

function SummaryCell({ label, value }) {
  return (
    <Grid item xs={6} sm={3}>
      <Typography variant="subtitle2">{label}</Typography>
      <Typography sx={{ fontFamily: font.mono, fontSize: '0.9rem' }}>{value}</Typography>
    </Grid>
  );
}

function PhysiologicalPanel({ timepoint }) {
  const valence = timepoint.valence || 0;

  return (
    <Panel
      label="Physiological parameters"
      action={
        <Typography sx={{ fontFamily: font.mono, fontSize: '0.72rem', color: color.signal }}>
          hour {timepointHours(timepoint).toFixed(0)}
        </Typography>
      }
    >
      <Grid container spacing={3}>
        {PHYSIO_KEYS.map((key) => (
          <Grid item xs={12} sm={6} lg={3} key={key}>
            <ParameterGauge paramKey={key} value={timepoint[key]} />
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4, pt: 2.5, borderTop: `1px solid ${color.rule}` }}>
        <Grid container spacing={2}>
          <SummaryCell label="Phase" value={timepoint.phase || 'treatment'} />
          <SummaryCell label="Emotion" value={timepoint.dominant_emotion || 'neutral'} />
          <SummaryCell label="Arousal" value={percent(timepoint.arousal ?? 0.5)} />
          <SummaryCell label="Valence" value={`${valence > 0 ? '+' : ''}${percent(valence)}`} />
        </Grid>
      </Box>
    </Panel>
  );
}

export default PhysiologicalPanel;
