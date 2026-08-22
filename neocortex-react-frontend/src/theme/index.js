import { createTheme } from '@mui/material/styles';
import { color, font } from './tokens';

const labelType = {
  fontFamily: font.display,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.14em',
  fontVariationSettings: "'wdth' 110",
};

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: color.signal, dark: color.signalDeep, contrastText: '#ffffff' },
    secondary: { main: color.plate, contrastText: '#ffffff' },
    success: { main: color.affirm },
    warning: { main: color.caution },
    error: { main: color.signalDeep },
    info: { main: color.plate },
    divider: color.rule,
    background: { default: color.chassis, paper: color.panel },
    text: { primary: color.ink, secondary: color.inkMute, disabled: color.inkFaint },
  },
  shape: { borderRadius: 2 },
  typography: {
    fontFamily: font.body,
    h1: { fontFamily: font.display, fontWeight: 700, letterSpacing: '-0.01em' },
    h2: { fontFamily: font.display, fontWeight: 700, letterSpacing: '-0.01em' },
    h3: { fontFamily: font.display, fontWeight: 700, letterSpacing: '-0.01em' },
    h4: { fontFamily: font.display, fontWeight: 600, fontSize: '1.5rem', letterSpacing: '0.01em' },
    h5: { fontFamily: font.display, fontWeight: 600, fontSize: '1.2rem', letterSpacing: '0.01em' },
    h6: { ...labelType, fontSize: '0.78rem' },
    subtitle1: { fontSize: '0.95rem', color: color.inkMute },
    subtitle2: { ...labelType, fontSize: '0.68rem', color: color.inkMute },
    body1: { fontSize: '0.94rem', lineHeight: 1.6 },
    body2: { fontSize: '0.86rem', lineHeight: 1.6 },
    caption: { fontSize: '0.74rem', color: color.inkMute, lineHeight: 1.5 },
    button: { ...labelType, fontSize: '0.72rem' },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '::selection': { background: color.signal, color: '#fff' },
        ':focus-visible': { outline: `2px solid ${color.signal}`, outlineOffset: 2 },
      },
    },
    MuiPaper: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: { backgroundImage: 'none', border: `1px solid ${color.rule}` },
      },
    },
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          border: `1px solid ${color.rule}`,
          transition: 'border-color 120ms ease, background-color 120ms ease',
        },
      },
    },
    MuiCardContent: { styleOverrides: { root: { padding: 18, '&:last-child': { paddingBottom: 18 } } } },
    MuiCardActions: { styleOverrides: { root: { padding: '0 18px 16px' } } },
    MuiButton: {
      defaultProps: { disableElevation: true, disableRipple: true },
      styleOverrides: {
        root: { borderRadius: 2, padding: '9px 18px', minHeight: 38 },
        sizeLarge: { padding: '13px 22px', fontSize: '0.76rem' },
        sizeSmall: { padding: '6px 12px', fontSize: '0.66rem' },
        contained: { '&:hover': { backgroundColor: color.signalDeep } },
        outlined: {
          borderColor: color.ruleStrong,
          color: color.ink,
          '&:hover': { borderColor: color.ink, backgroundColor: 'transparent' },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 2, fontFamily: font.mono, fontSize: '0.7rem', letterSpacing: '0.02em' },
        sizeSmall: { height: 22 },
        outlined: { borderColor: color.rule },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: { minHeight: 40, borderBottom: `1px solid ${color.rule}` },
        indicator: { height: 2, backgroundColor: color.signal },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          ...labelType,
          fontSize: '0.7rem',
          minHeight: 40,
          padding: '0 16px',
          color: color.inkMute,
          '&.Mui-selected': { color: color.ink },
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        root: { height: 2, color: color.signal },
        rail: { opacity: 1, backgroundColor: color.chassisDeep },
        track: { border: 'none' },
        thumb: {
          width: 12,
          height: 12,
          borderRadius: 0,
          backgroundColor: color.ink,
          '&:hover, &.Mui-focusVisible': { boxShadow: `0 0 0 6px ${color.signalWash}` },
        },
        mark: { backgroundColor: color.ruleStrong, height: 5, width: 1 },
        markLabel: { fontFamily: font.mono, fontSize: '0.66rem', color: color.inkMute },
        valueLabel: {
          fontFamily: font.mono,
          fontSize: '0.68rem',
          borderRadius: 1,
          backgroundColor: color.ink,
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: { height: 6, borderRadius: 0, backgroundColor: color.chassisDeep },
        bar: { borderRadius: 0 },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 2,
          backgroundColor: color.panel,
          '& fieldset': { borderColor: color.rule },
          '&:hover fieldset': { borderColor: color.ruleStrong },
        },
        input: { fontFamily: font.mono, fontSize: '0.86rem' },
      },
    },
    MuiInputLabel: { styleOverrides: { root: { fontSize: '0.86rem', color: color.inkMute } } },
    MuiFormHelperText: { styleOverrides: { root: { marginLeft: 0, fontSize: '0.7rem' } } },
    MuiAlert: {
      variants: [
        { props: { severity: 'success' }, style: { backgroundColor: color.affirmWash, color: color.ink } },
        { props: { severity: 'warning' }, style: { backgroundColor: color.cautionWash, color: color.ink } },
        { props: { severity: 'error' }, style: { backgroundColor: color.signalWash, color: color.ink } },
        { props: { severity: 'info' }, style: { backgroundColor: color.plateWash, color: color.ink } },
      ],
      styleOverrides: {
        root: { borderRadius: 2, border: `1px solid ${color.rule}`, alignItems: 'center' },
        icon: { display: 'none' },
        message: { padding: '6px 0', fontSize: '0.84rem' },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderColor: color.rule, fontSize: '0.82rem' },
        head: { ...labelType, fontSize: '0.64rem', color: color.inkMute, backgroundColor: color.panelAlt },
        body: { fontFamily: font.mono },
      },
    },
    MuiDivider: { styleOverrides: { root: { borderColor: color.rule } } },
    MuiSwitch: {
      styleOverrides: {
        root: { padding: 8 },
        track: { borderRadius: 2, backgroundColor: color.ruleStrong, opacity: 1 },
        thumb: { borderRadius: 1, width: 14, height: 14, boxShadow: 'none' },
        switchBase: { padding: 11, '&.Mui-checked+.MuiSwitch-track': { opacity: 1 } },
      },
    },
    MuiCircularProgress: { styleOverrides: { root: { color: color.signal } } },
  },
});

export default theme;
