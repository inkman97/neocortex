import React, { useState } from 'react';
import { Alert, Box, Slider, Tab, Tabs } from '@mui/material';
import { CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis } from 'recharts';
import Panel from '../ui/Panel';
import ChartWell from '../ui/ChartWell';
import PhysiologicalPanel from './PhysiologicalPanel';
import PhysiologicalCharts from './PhysiologicalCharts';
import { MENTAL_STATE_SERIES, NEUROCHEM_SERIES } from '../constants/series';
import { axisProps, gridProps, legendProps, tooltipProps, traceProps } from '../ui/chartDefaults';
import { timepointHours } from '../lib/format';

const MAX_TIMELINE_MARKS = 8;

const buildSeriesData = (timepoints, series) =>
  timepoints.map((timepoint) =>
    series.reduce((row, entry) => ({ ...row, [entry.key]: timepoint[entry.key] * 100 }), {
      hours: timepointHours(timepoint),
    })
  );

function TraceChart({ caption, data, series, height = 320 }) {
  return (
    <ChartWell caption={caption} height={height}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid {...gridProps} />
        <XAxis dataKey="hours" {...axisProps} />
        <YAxis {...axisProps} />
        <Tooltip {...tooltipProps} />
        <Legend {...legendProps} />
        {series.map((entry) => (
          <Line key={entry.key} {...traceProps} dataKey={entry.key} name={entry.name} stroke={entry.stroke} />
        ))}
      </LineChart>
    </ChartWell>
  );
}

function TimelineSelector({ timepoints, value, onChange }) {
  const stride = Math.max(1, Math.ceil(timepoints.length / MAX_TIMELINE_MARKS));
  const marks = timepoints
    .filter((_, index) => index % stride === 0)
    .map((timepoint, index) => ({
      value: index * stride,
      label: `${timepointHours(timepoint)}h`,
    }));

  return (
    <Panel label="Timepoint" tone="alt">
      <Box sx={{ px: 1, pt: 1 }}>
        <Slider
          value={value}
          onChange={(event, next) => onChange(next)}
          min={0}
          max={timepoints.length - 1}
          step={1}
          marks={marks}
          valueLabelDisplay="auto"
          valueLabelFormat={(index) => `${timepointHours(timepoints[index])}h`}
        />
      </Box>
    </Panel>
  );
}

function ResultsViewer({ results }) {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedTimepoint, setSelectedTimepoint] = useState(0);

  if (!results) {
    return <Alert severity="info">No results yet. Run a trial first.</Alert>;
  }

  const { timepoints, used_neocortex: usedNeoCortex } = results;
  const hasPhysiology = timepoints[0]?.heart_rate !== undefined;

  const missingPhysiology = (
    <Alert severity="warning">
      This run returned no physiological channels. Update the backend to emit them.
    </Alert>
  );

  return (
    <Box>
      <Alert severity={usedNeoCortex ? 'success' : 'warning'} sx={{ mb: 3 }}>
        {usedNeoCortex
          ? `Simulated on the NeoCortex GPU model with ${results.neurons?.toLocaleString() || 'an unreported number of'} neurons.`
          : 'The GPU server was unavailable, so these numbers come from the mathematical fallback. Treat them as approximate.'}
      </Alert>

      <Tabs value={activeTab} onChange={(event, next) => setActiveTab(next)} sx={{ mb: 3 }}>
        <Tab label="Neurochemistry" />
        <Tab label="Physiology" />
        <Tab label="Time evolution" />
      </Tabs>

      {activeTab === 0 && (
        <>
          <Panel label="Neurotransmitter levels">
            <TraceChart
              caption="concentration (%) over hours after dose"
              data={buildSeriesData(timepoints, NEUROCHEM_SERIES)}
              series={NEUROCHEM_SERIES}
            />
          </Panel>
          <Panel label="Mental state">
            <TraceChart
              caption="level (%) over hours after dose"
              data={buildSeriesData(timepoints, MENTAL_STATE_SERIES)}
              series={MENTAL_STATE_SERIES}
              height={260}
            />
          </Panel>
        </>
      )}

      {activeTab === 1 &&
        (hasPhysiology ? (
          <>
            <TimelineSelector
              timepoints={timepoints}
              value={selectedTimepoint}
              onChange={setSelectedTimepoint}
            />
            <PhysiologicalPanel timepoint={timepoints[selectedTimepoint]} />
          </>
        ) : (
          missingPhysiology
        ))}

      {activeTab === 2 &&
        (hasPhysiology ? <PhysiologicalCharts trialData={results} /> : missingPhysiology)}
    </Box>
  );
}

export default ResultsViewer;
