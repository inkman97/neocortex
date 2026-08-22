import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Alert,
  Box,
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis } from 'recharts';
import api from '../api';
import Panel from '../ui/Panel';
import Readout from '../ui/Readout';
import ChartWell from '../ui/ChartWell';
import { adaptDiseaseForDiscovery } from '../lib/backendAdapters';
import { percent } from '../lib/format';
import { axisProps, gridProps, legendProps, tooltipProps, traceProps } from '../ui/chartDefaults';
import { color, font, trace } from '../theme/tokens';

const POLL_INTERVAL_MS = 10000;
const DEFAULT_NEURONS = 50000;
const PLACEHOLDER_DIVERSITY = 0.5;

const FITNESS_SERIES = [
  { key: 'bestFitness', name: 'Best', stroke: trace.best },
  { key: 'avgFitness', name: 'Average', stroke: trace.average },
  { key: 'diversity', name: 'Diversity', stroke: trace.diversity },
];

function DiscoveryRunner({ disease, config, onDiscoveryComplete }) {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentGeneration, setCurrentGeneration] = useState(0);
  const [bestFitness, setBestFitness] = useState(0);
  const [fitnessHistory, setFitnessHistory] = useState([]);
  const [error, setError] = useState(null);
  const [log, setLog] = useState([]);

  const hasStarted = useRef(false);
  const pollRef = useRef(null);

  const addLog = useCallback((message) => {
    setLog((entries) => [...entries, { time: new Date().toLocaleTimeString(), message }]);
  }, []);

  const startDiscovery = useCallback(async () => {
    setRunning(true);
    setError(null);

    try {
      addLog('Starting the search');
      addLog(`Target: ${disease.name}`);

      const { data } = await api.post('/discovery/start', {
        disease: adaptDiseaseForDiscovery(disease),
        config,
        neurons: config.neurons || DEFAULT_NEURONS,
      });

      const jobId = data.jobId;
      addLog(`Job ${jobId} accepted`);
      addLog('Polling every 10 seconds');

      pollRef.current = setInterval(async () => {
        try {
          const { data: job } = await api.get(`/discovery/status/${jobId}`);

          setCurrentGeneration(job.currentGeneration);
          setBestFitness(job.bestFitness);
          setProgress((job.currentGeneration / job.totalGenerations) * 100);

          if (job.currentGeneration > 0) {
            setFitnessHistory((history) =>
              history.some((entry) => entry.generation === job.currentGeneration)
                ? history
                : [
                    ...history,
                    {
                      generation: job.currentGeneration,
                      bestFitness: job.bestFitness,
                      avgFitness: job.avgFitness,
                      diversity: PLACEHOLDER_DIVERSITY,
                    },
                  ]
            );
          }

          addLog(
            `Generation ${job.currentGeneration}/${job.totalGenerations} · fitness ${job.bestFitness.toFixed(3)}`
          );

          if (job.status === 'completed') {
            clearInterval(pollRef.current);
            setRunning(false);
            addLog('Search complete');
            onDiscoveryComplete({
              optimalDrug: job.result.optimalDrug,
              fitnessHistory: job.result.fitnessHistory,
              finalFitness: job.result.finalFitness,
              generations: job.result.generations,
            });
          }

          if (job.status === 'failed') {
            clearInterval(pollRef.current);
            setError(job.error);
            setRunning(false);
            addLog(`Failed: ${job.error}`);
          }
        } catch (pollError) {
          addLog('Status check failed, retrying');
        }
      }, POLL_INTERVAL_MS);
    } catch (startError) {
      setError(startError.message || 'The search did not start.');
      setRunning(false);
    }
  }, [addLog, config, disease, onDiscoveryComplete]);

  useEffect(() => {
    if (!hasStarted.current) {
      hasStarted.current = true;
      startDiscovery();
    }
    return () => clearInterval(pollRef.current);
  }, [startDiscovery]);

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Panel label="Progress">
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography sx={{ fontFamily: font.mono, fontSize: '0.76rem', color: color.inkMute }}>
            generation {currentGeneration} / {config.iterations}
          </Typography>
          <Typography sx={{ fontFamily: font.mono, fontSize: '0.76rem', color: color.signal }}>
            {progress.toFixed(1)}%
          </Typography>
        </Box>
        <LinearProgress variant="determinate" value={progress} sx={{ height: 8 }} />

        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} sm={4}>
            <Readout label="Best fitness" value={percent(bestFitness, 1)} tone="signal" />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Readout
              label="Candidates scored"
              value={(currentGeneration * config.populationSize).toLocaleString()}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Readout label="Status" value={running ? 'Running' : 'Idle'} tone={running ? 'signal' : 'mute'} />
          </Grid>
        </Grid>
      </Panel>

      {fitnessHistory.length > 0 && (
        <Panel label="Fitness evolution">
          <ChartWell caption="fitness per generation" height={300}>
            <LineChart data={fitnessHistory} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="generation" {...axisProps} />
              <YAxis {...axisProps} />
              <Tooltip {...tooltipProps} />
              <Legend {...legendProps} />
              {FITNESS_SERIES.map((series) => (
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

      <Panel label="Log" dense>
        <TableContainer sx={{ maxHeight: 300 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Time</TableCell>
                <TableCell>Event</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {log
                .slice()
                .reverse()
                .map((entry, index) => (
                  <TableRow key={`${entry.time}-${index}`}>
                    <TableCell sx={{ whiteSpace: 'nowrap', color: color.inkMute }}>{entry.time}</TableCell>
                    <TableCell>{entry.message}</TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Panel>
    </Box>
  );
}

export default DiscoveryRunner;
