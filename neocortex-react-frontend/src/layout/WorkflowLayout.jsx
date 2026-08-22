import React from 'react';
import { Box, Button, Typography } from '@mui/material';
import { color, font, metric } from '../theme/tokens';

function StepRuler({ steps, activeStep }) {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', sm: `repeat(${steps.length}, 1fr)` },
        borderTop: `1px solid ${color.rule}`,
        borderBottom: `1px solid ${color.rule}`,
        backgroundColor: color.panel,
      }}
    >
      {steps.map((label, index) => {
        const reached = index <= activeStep;
        const current = index === activeStep;
        return (
          <Box
            key={label}
            sx={{
              px: 2,
              py: 1.5,
              borderLeft: { sm: index === 0 ? 'none' : `1px solid ${color.rule}` },
              borderTop: { xs: index === 0 ? 'none' : `1px solid ${color.rule}`, sm: 'none' },
              opacity: reached ? 1 : 0.55,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
              <Typography
                sx={{
                  fontFamily: font.mono,
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  color: current ? color.signal : color.inkMute,
                }}
              >
                {String(index + 1).padStart(2, '0')}
              </Typography>
              <Typography
                sx={{
                  fontFamily: font.display,
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  color: current ? color.ink : color.inkMute,
                }}
              >
                {label}
              </Typography>
            </Box>
            <Box
              sx={{
                mt: 1,
                height: 3,
                backgroundColor: reached ? color.signal : color.chassisDeep,
                transition: 'background-color 160ms ease',
              }}
            />
          </Box>
        );
      })}
    </Box>
  );
}

function WorkflowLayout({ title, kicker, note, steps, activeStep, onBack, primaryAction, children }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: `calc(100vh - ${metric.mastheadHeight}px)` }}>
      <Box sx={{ px: { xs: 2, md: 4 }, pt: { xs: 3, md: 5 }, pb: 3, backgroundColor: color.panel }}>
        <Typography
          sx={{
            fontFamily: font.display,
            fontSize: '0.64rem',
            fontWeight: 600,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: color.signal,
          }}
        >
          {kicker}
        </Typography>
        <Typography
          component="h1"
          sx={{
            fontFamily: font.display,
            fontSize: { xs: '1.9rem', md: '2.6rem' },
            fontWeight: 700,
            lineHeight: 1.05,
            letterSpacing: '-0.015em',
            mt: 1,
            maxWidth: 780,
          }}
        >
          {title}
        </Typography>
        {note && (
          <Typography sx={{ mt: 1.5, maxWidth: 620, color: color.inkMute, fontSize: '0.92rem' }}>
            {note}
          </Typography>
        )}
      </Box>

      <StepRuler steps={steps} activeStep={activeStep} />

      <Box sx={{ flexGrow: 1, px: { xs: 2, md: 4 }, py: { xs: 3, md: 4 } }}>{children}</Box>

      <Box
        sx={{
          position: 'sticky',
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          px: { xs: 2, md: 4 },
          py: 2,
          backgroundColor: color.panel,
          borderTop: `1px solid ${color.rule}`,
        }}
      >
        <Button variant="outlined" disabled={activeStep === 0} onClick={onBack}>
          Back
        </Button>
        <Typography sx={{ fontFamily: font.mono, fontSize: '0.68rem', color: color.inkFaint }}>
          {String(activeStep + 1).padStart(2, '0')} / {String(steps.length).padStart(2, '0')}
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        {primaryAction}
      </Box>
    </Box>
  );
}

export default WorkflowLayout;
