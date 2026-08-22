import React from 'react';
import {
  Alert,
  Box,
  Button,
  Collapse,
  FormControlLabel,
  Grid,
  IconButton,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import Panel from '../../ui/Panel';
import TargetChips from '../../ui/TargetChips';
import TargetSelect from './TargetSelect';
import PotencySlider from './PotencySlider';
import { percent } from '../../lib/format';
import { color, font } from '../../theme/tokens';

const DEFAULT_METABOLITE_HILL = 1.5;

function MetaboliteRow({ metabolite, onRemove }) {
  return (
    <Box sx={{ display: 'flex', gap: 2, py: 1.5, borderTop: `1px solid ${color.rule}` }}>
      <Box sx={{ flexGrow: 1 }}>
        <Typography sx={{ fontFamily: font.display, fontWeight: 600, fontSize: '0.95rem' }}>
          {metabolite.name}
        </Typography>
        <Typography sx={{ fontFamily: font.mono, fontSize: '0.7rem', color: color.inkMute, mb: 1 }}>
          formation {percent(metabolite.formation_fraction)} · t½ {metabolite.halfLife_hours}h · tmax{' '}
          {metabolite.tmax_hours}h
        </Typography>
        <TargetChips targets={metabolite.targets} tone="plate" />
      </Box>
      <IconButton size="small" onClick={onRemove} aria-label={`Remove ${metabolite.name}`}>
        <DeleteIcon fontSize="small" />
      </IconButton>
    </Box>
  );
}

function MetaboliteEditor({
  metabolites,
  enabled,
  onEnabledChange,
  draft,
  onDraftChange,
  targetDraft,
  onTargetDraftChange,
  onAddMetabolite,
  onRemoveMetabolite,
}) {
  const patchDraft = (patch) => onDraftChange({ ...draft, ...patch });

  const handleAddTarget = () => {
    if (!targetDraft.target) return;
    patchDraft({
      targets: [
        ...draft.targets,
        {
          target: targetDraft.target,
          action: 'mechanism',
          potency: targetDraft.potency,
          hill: DEFAULT_METABOLITE_HILL,
        },
      ],
    });
    onTargetDraftChange({ target: 'sert_inhibition', potency: 0.5 });
  };

  const handleRemoveTarget = (index) => {
    patchDraft({ targets: draft.targets.filter((_, i) => i !== index) });
  };

  return (
    <Panel
      label="Active metabolites"
      index="opt"
      action={
        <FormControlLabel
          control={
            <Switch checked={enabled} onChange={(event) => onEnabledChange(event.target.checked)} />
          }
          label={<Typography variant="subtitle2">Enable</Typography>}
          sx={{ mr: 0 }}
        />
      }
    >
      <Collapse in={enabled}>
        <Alert severity="info" sx={{ mb: 2 }}>
          Metabolites act on their own pharmacokinetics, independently of the parent compound. Fluoxetine
          forms norfluoxetine, t½ 336h, which is why its action outlasts the dose.
        </Alert>

        {metabolites.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Configured ({metabolites.length})
            </Typography>
            {metabolites.map((metabolite, index) => (
              <MetaboliteRow
                key={`${metabolite.name}-${index}`}
                metabolite={metabolite}
                onRemove={() => onRemoveMetabolite(index)}
              />
            ))}
          </Box>
        )}

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              size="small"
              label="Metabolite name"
              value={draft.name}
              onChange={(event) => patchDraft({ name: event.target.value })}
              placeholder="Norfluoxetine"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              size="small"
              type="number"
              label="Formation fraction"
              value={draft.formation_fraction}
              onChange={(event) => patchDraft({ formation_fraction: parseFloat(event.target.value) })}
              inputProps={{ min: 0, max: 1, step: 0.1 }}
              helperText="0.8 means 80% of the parent converts"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              size="small"
              type="number"
              label="Half-life (hours)"
              value={draft.halfLife_hours}
              onChange={(event) => patchDraft({ halfLife_hours: parseFloat(event.target.value) })}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              size="small"
              type="number"
              label="Tmax (hours)"
              value={draft.tmax_hours}
              onChange={(event) => patchDraft({ tmax_hours: parseFloat(event.target.value) })}
            />
          </Grid>
        </Grid>

        <Typography variant="subtitle2" gutterBottom>
          Metabolite targets
        </Typography>
        <Box sx={{ mb: 2 }}>
          <TargetChips targets={draft.targets} tone="plate" onDelete={handleRemoveTarget} />
        </Box>

        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={5}>
            <TargetSelect
              size="small"
              showDescription={false}
              label="Target"
              value={targetDraft.target}
              onChange={(target) => onTargetDraftChange({ ...targetDraft, target })}
            />
          </Grid>
          <Grid item xs={12} md={5}>
            <PotencySlider
              size="small"
              value={targetDraft.potency}
              onChange={(potency) => onTargetDraftChange({ ...targetDraft, potency })}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button fullWidth variant="outlined" size="small" onClick={handleAddTarget}>
              Add target
            </Button>
          </Grid>
        </Grid>

        <Button
          fullWidth
          variant="contained"
          color="secondary"
          onClick={onAddMetabolite}
          disabled={!draft.name || draft.targets.length === 0}
          sx={{ mt: 3 }}
        >
          Add metabolite
        </Button>
      </Collapse>
    </Panel>
  );
}

export default MetaboliteEditor;
