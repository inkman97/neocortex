import React from 'react';
import { Box, Typography } from '@mui/material';
import { NavLink } from 'react-router-dom';
import { color, font, metric } from '../theme/tokens';

const MODES = [
  { to: '/trials', label: 'Drug Trials', hint: 'Test a known or custom compound' },
  { to: '/discovery', label: 'Drug Discovery', hint: 'Search for an optimal compound' },
];

function ModePlate({ to, label, hint }) {
  return (
    <NavLink to={to} style={{ textDecoration: 'none' }}>
      {({ isActive }) => (
        <Box
          sx={{
            px: 2,
            py: 1.5,
            borderLeft: '3px solid',
            borderLeftColor: isActive ? color.signal : 'transparent',
            backgroundColor: isActive ? color.panel : 'transparent',
            transition: 'background-color 120ms ease, border-color 120ms ease',
            '&:hover': { backgroundColor: isActive ? color.panel : 'rgba(255,255,255,0.4)' },
          }}
        >
          <Typography
            sx={{
              fontFamily: font.display,
              fontSize: '0.74rem',
              fontWeight: 600,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              color: isActive ? color.ink : color.inkMute,
            }}
          >
            {label}
          </Typography>
          <Typography sx={{ fontSize: '0.7rem', color: color.inkFaint, mt: 0.25 }}>{hint}</Typography>
        </Box>
      )}
    </NavLink>
  );
}

function AppShell({ children }) {
  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: color.chassis }}>
      <Box
        component="header"
        sx={{
          height: metric.mastheadHeight,
          px: { xs: 2, md: 3 },
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          backgroundColor: color.panel,
          borderBottom: `1px solid ${color.rule}`,
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <Typography
          sx={{
            fontFamily: font.display,
            fontWeight: 700,
            fontSize: '1rem',
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
          }}
        >
          NeoCortex
        </Typography>
        <Box className="feed-rule" sx={{ flexGrow: 1, height: 5, opacity: 0.45 }} />
        <Typography
          sx={{
            fontFamily: font.mono,
            fontSize: '0.68rem',
            color: color.inkMute,
            display: { xs: 'none', sm: 'block' },
          }}
        >
          emergent pharmacology · v2.0
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, alignItems: 'stretch' }}>
        <Box
          component="nav"
          sx={{
            width: { xs: '100%', md: metric.railWidth },
            flexShrink: 0,
            borderRight: { md: `1px solid ${color.rule}` },
            borderBottom: { xs: `1px solid ${color.rule}`, md: 'none' },
            display: 'flex',
            flexDirection: { xs: 'row', md: 'column' },
            position: { md: 'sticky' },
            top: { md: metric.mastheadHeight },
            alignSelf: { md: 'flex-start' },
            height: { md: `calc(100vh - ${metric.mastheadHeight}px)` },
          }}
        >
          <Typography
            sx={{
              display: { xs: 'none', md: 'block' },
              px: 2,
              pt: 3,
              pb: 1.5,
              fontFamily: font.display,
              fontSize: '0.62rem',
              fontWeight: 600,
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              color: color.inkFaint,
            }}
          >
            Bench
          </Typography>

          <Box sx={{ flexGrow: { xs: 1, md: 0 }, display: 'flex', flexDirection: { xs: 'row', md: 'column' } }}>
            {MODES.map((mode) => (
              <Box key={mode.to} sx={{ flex: { xs: 1, md: 'none' } }}>
                <ModePlate {...mode} />
              </Box>
            ))}
          </Box>

          <Box
            sx={{
              display: { xs: 'none', md: 'block' },
              mt: 'auto',
              px: 2,
              py: 2,
              borderTop: `1px solid ${color.rule}`,
            }}
          >
            <Typography sx={{ fontFamily: font.mono, fontSize: '0.66rem', color: color.inkFaint }}>
              6 neurotransmitter systems
            </Typography>
            <Typography sx={{ fontFamily: font.mono, fontSize: '0.66rem', color: color.inkFaint }}>
              spiking brain model
            </Typography>
          </Box>
        </Box>

        <Box component="main" sx={{ flexGrow: 1, minWidth: 0, backgroundColor: color.panelAlt }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}

export default AppShell;
