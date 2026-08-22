import React from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import Panel from '../ui/Panel';
import Readout from '../ui/Readout';
import ChartWell from '../ui/ChartWell';
import DeficitChips from '../ui/DeficitChips';
import TargetChips from '../ui/TargetChips';
import MolecularStructure from './discovery/MolecularStructure';
import { targetNeurotransmitter, targetShortLabel } from '../constants/targets';
import { percent } from '../lib/format';
import { axisProps, gridProps, legendProps, tooltipProps, traceProps } from '../ui/chartDefaults';
import { color, font, trace } from '../theme/tokens';

const HISTORY_SERIES = [
  { key: 'bestFitness', name: 'Best', stroke: trace.best },
  { key: 'avgFitness', name: 'Average', stroke: trace.average },
];

const downloadJson = (payload, filename) => {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
};

function TargetTable({ targets }) {
  return (
    <TableContainer>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Target</TableCell>
            <TableCell>Neurotransmitter</TableCell>
            <TableCell align="right">Potency</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {targets.map((target, index) => (
            <TableRow key={`${target.target}-${index}`}>
              <TableCell>{targetShortLabel(target.target)}</TableCell>
              <TableCell>
                <Chip size="small" variant="outlined" label={targetNeurotransmitter(target.target)} />
              </TableCell>
              <TableCell align="right" sx={{ color: color.signal }}>
                {percent(target.potency)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

function DiscoveryResults({ results, disease }) {
  if (!results || !results.optimalDrug) {
    return <Alert severity="error">No result to show. The search did not return a compound.</Alert>;
  }

  const { optimalDrug, fitnessHistory, finalFitness, generations } = results;

  const rankedTargets = [...optimalDrug.molecularTargets].sort((a, b) => b.potency - a.potency);

  const radarData = optimalDrug.molecularTargets.map((target) => ({
    target: targetShortLabel(target.target),
    potency: target.potency * 100,
  }));

  const handleDownload = () =>
    downloadJson(optimalDrug, `${optimalDrug.name.replace(/\s+/g, '_')}.json`);

  return (
    <Box>
      <Alert severity="success" sx={{ mb: 3 }}>
        Search finished after {generations} generations at {percent(finalFitness, 1)} fitness.
      </Alert>

      <Panel label="Candidate" tone="alt">
        <Typography sx={{ fontFamily: font.display, fontSize: '2rem', fontWeight: 700, lineHeight: 1.1 }}>
          {optimalDrug.name}
        </Typography>
        <Typography variant="body2" sx={{ color: color.inkMute, mb: 3 }}>
          Optimized against {disease.name}
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={4}>
            <Readout label="Fitness" value={percent(finalFitness, 1)} tone="signal" />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Readout label="Targets" value={optimalDrug.molecularTargets.length} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Readout label="Class" value={optimalDrug.class} />
          </Grid>
        </Grid>
      </Panel>

      <Panel label="Target profile" index="01">
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <TargetTable targets={rankedTargets} />
          </Grid>
          <Grid item xs={12} md={6}>
            <Box className="chart-well" sx={{ p: 1.5 }}>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke={color.ruleStrong} />
                  <PolarAngleAxis
                    dataKey="target"
                    tick={{ fill: color.inkMute, fontSize: 11, fontFamily: font.mono }}
                  />
                  <PolarRadiusAxis
                    angle={90}
                    domain={[0, 100]}
                    tick={{ fill: color.inkFaint, fontSize: 10, fontFamily: font.mono }}
                  />
                  <Radar
                    name="Potency"
                    dataKey="potency"
                    stroke={color.signal}
                    fill={color.signal}
                    fillOpacity={0.25}
                  />
                  <Tooltip {...tooltipProps} />
                </RadarChart>
              </ResponsiveContainer>
            </Box>
          </Grid>
        </Grid>
      </Panel>

      {optimalDrug.molecular_structure?.smiles && (
        <MolecularStructure structure={optimalDrug.molecular_structure} />
      )}

      <Panel label="Disease against drug" index="02">
        <Typography variant="subtitle2" gutterBottom>
          Deviations in {disease.name}
        </Typography>
        <Box sx={{ mb: 3 }}>
          <DeficitChips disease={disease} />
        </Box>
        <Typography variant="subtitle2" gutterBottom>
          What the compound does
        </Typography>
        <TargetChips targets={optimalDrug.molecularTargets} />
      </Panel>

      {fitnessHistory?.length > 0 && (
        <Panel label="Search history" index="03">
          <ChartWell caption="fitness per generation" height={300}>
            <LineChart data={fitnessHistory} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="generation" {...axisProps} />
              <YAxis {...axisProps} />
              <Tooltip {...tooltipProps} />
              <Legend {...legendProps} />
              {HISTORY_SERIES.map((series) => (
                <Line
                  key={series.key}
                  {...traceProps}
                  dataKey={series.key}
                  name={series.name}
                  stroke={series.stroke}
                />
              ))}
            </LineChart>
          </ChartWell>
        </Panel>
      )}

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <Button fullWidth variant="contained" size="large" onClick={handleDownload}>
            Download definition
          </Button>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Button
            fullWidth
            variant="outlined"
            size="large"
            onClick={() => alert('Testing a discovered compound in a virtual trial is not wired up yet.')}
          >
            Test in a virtual trial
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DiscoveryResults;
