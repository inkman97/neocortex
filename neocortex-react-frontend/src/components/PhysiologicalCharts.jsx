import React, { useState } from 'react';
import { Box, Tab, Tabs, Typography } from '@mui/material';
import { CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis } from 'recharts';
import ChartWell from '../ui/ChartWell';
import { PHYSIO_GROUPS, PHYSIO_KEYS, PHYSIO_SERIES } from '../constants/series';
import { axisProps, gridProps, legendProps, tooltipProps, traceProps } from '../ui/chartDefaults';
import { timepointHours } from '../lib/format';

const toPercent = (value) => (value || 0) * 100;

function PhysiologicalCharts({ trialData }) {
  const [activeGroup, setActiveGroup] = useState(0);

  const chartData = trialData.timepoints.map((timepoint) => {
    const hours = timepointHours(timepoint);
    const channels = PHYSIO_KEYS.reduce(
      (acc, key) => ({ ...acc, [key]: toPercent(timepoint[key]) }),
      {}
    );
    return { hours, days: timepoint.days ?? hours / 24, ...channels };
  });

  const group = PHYSIO_GROUPS[activeGroup];

  return (
    <Box>
      <Tabs
        value={activeGroup}
        onChange={(event, next) => setActiveGroup(next)}
        variant="scrollable"
        allowScrollButtonsMobile
        sx={{ mb: 3 }}
      >
        {PHYSIO_GROUPS.map((entry) => (
          <Tab key={entry.id} label={entry.label} />
        ))}
      </Tabs>

      <Typography variant="body2" sx={{ mb: 2, maxWidth: 640 }}>
        {group.blurb}
      </Typography>

      <ChartWell caption="level (%) over elapsed hours" height={group.height}>
        <LineChart data={chartData} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid {...gridProps} />
          <XAxis dataKey="hours" {...axisProps} />
          <YAxis domain={[0, 100]} {...axisProps} />
          <Tooltip {...tooltipProps} />
          <Legend {...legendProps} />
          {group.keys.map((key) => (
            <Line
              key={key}
              {...traceProps}
              dataKey={key}
              name={group.compact ? PHYSIO_SERIES[key].short : PHYSIO_SERIES[key].name}
              stroke={PHYSIO_SERIES[key].stroke}
              strokeWidth={group.compact ? 1.2 : 1.8}
            />
          ))}
        </LineChart>
      </ChartWell>
    </Box>
  );
}

export default PhysiologicalCharts;
