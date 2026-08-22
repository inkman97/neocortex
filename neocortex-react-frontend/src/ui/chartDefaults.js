import { color, font } from '../theme/tokens';

export const axisProps = {
  stroke: color.ruleStrong,
  tick: { fill: color.inkMute, fontSize: 11, fontFamily: font.mono },
  tickLine: false,
};

export const gridProps = {
  stroke: color.paperGridStrong,
  strokeOpacity: 0.35,
  vertical: false,
};

export const tooltipProps = {
  contentStyle: {
    background: color.panel,
    border: `1px solid ${color.ruleStrong}`,
    borderRadius: 2,
    fontFamily: font.mono,
    fontSize: 12,
  },
  labelStyle: { color: color.inkMute },
  cursor: { stroke: color.ruleStrong, strokeDasharray: '3 3' },
};

export const legendProps = {
  wrapperStyle: { fontFamily: font.mono, fontSize: 11, paddingTop: 8 },
  iconType: 'plainline',
  iconSize: 14,
};

export const traceProps = {
  type: 'monotone',
  dot: false,
  strokeWidth: 1.6,
  activeDot: { r: 3, strokeWidth: 0 },
};
