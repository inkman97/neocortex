import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Box, Tab, Tabs } from '@mui/material';
import api from '../api';
import { toArray } from '../lib/collections';
import { initialDoseOf, slugify } from '../lib/dosing';
import DrugLibrary from './drug/DrugLibrary';
import CustomDrugForm, { emptyComposer } from './drug/CustomDrugForm';
import { color, font } from '../theme/tokens';

const LIBRARY_TAB = 0;

function DrugDesigner({ onDrugConfigured, currentDrug }) {
  const [tab, setTab] = useState(LIBRARY_TAB);
  const [knownDrugs, setKnownDrugs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDrug, setSelectedDrug] = useState(null);
  const [selectedDose, setSelectedDose] = useState(null);
  const [composer, setComposer] = useState(emptyComposer);

  const loadKnownDrugs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/trials/drugs/library');
      setKnownDrugs(toArray(response.data, 'drugs'));
    } catch (requestError) {
      setError('Could not load the drug library. Check the backend connection.');
      setKnownDrugs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadKnownDrugs();
  }, [loadKnownDrugs]);

  const handleSelectKnownDrug = (drug) => {
    setSelectedDrug(drug);
    setSelectedDose(initialDoseOf(drug));
  };

  const handleConfirmDrugWithDose = () => {
    if (!selectedDrug || !selectedDose) return;
    onDrugConfigured({
      ...selectedDrug,
      dose_mg: selectedDose,
      typical_dose_mg: selectedDrug.typical_dose_mg,
    });
  };

  const handleConfigureCustomDrug = () => {
    const { drug } = composer;
    if (!drug.name || drug.molecularTargets.length === 0) return;
    onDrugConfigured({ ...drug, id: drug.id || slugify(drug.name) });
  };

  return (
    <Box>
      {currentDrug && (
        <Alert severity="success" sx={{ mb: 2 }}>
          <Box component="span" sx={{ fontFamily: font.mono, fontSize: '0.82rem' }}>
            {currentDrug.name}
            {currentDrug.dose_mg ? ` · ${currentDrug.dose_mg} mg` : ''}
            {currentDrug.active_metabolites?.length
              ? ` · ${currentDrug.active_metabolites.length} metabolite(s)`
              : ''}
          </Box>
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Tabs value={tab} onChange={(event, next) => setTab(next)} sx={{ mb: 3, borderColor: color.rule }}>
        <Tab label="Library" />
        <Tab label="Design a compound" />
      </Tabs>

      {tab === LIBRARY_TAB ? (
        <DrugLibrary
          drugs={knownDrugs}
          loading={loading}
          selectedDrug={selectedDrug}
          selectedDose={selectedDose}
          onSelectDrug={handleSelectKnownDrug}
          onDoseChange={setSelectedDose}
          onConfirm={handleConfirmDrugWithDose}
        />
      ) : (
        <CustomDrugForm value={composer} onChange={setComposer} onSubmit={handleConfigureCustomDrug} />
      )}
    </Box>
  );
}

export default DrugDesigner;
