import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Box, Tab, Tabs } from '@mui/material';
import api from '../api';
import { toArray } from '../lib/collections';
import { slugify } from '../lib/dosing';
import DiseaseLibrary from './disease/DiseaseLibrary';
import CustomDiseaseForm, { emptyDiseaseComposer } from './disease/CustomDiseaseForm';
import { font } from '../theme/tokens';

const LIBRARY_TAB = 0;

function DiseaseDesigner({ onDiseaseSelected, currentDisease }) {
  const [tab, setTab] = useState(LIBRARY_TAB);
  const [knownDiseases, setKnownDiseases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [composer, setComposer] = useState(emptyDiseaseComposer);

  const loadKnownDiseases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/trials/diseases/library');
      setKnownDiseases(toArray(response.data, 'diseases'));
    } catch (requestError) {
      setError('Could not load the disease library. Check the backend connection.');
      setKnownDiseases([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadKnownDiseases();
  }, [loadKnownDiseases]);

  const handleConfigureCustomDisease = () => {
    const { disease } = composer;
    if (!disease.name) return;
    onDiseaseSelected({ ...disease, id: disease.id || slugify(disease.name) });
  };

  return (
    <Box>
      {currentDisease && (
        <Alert severity="success" sx={{ mb: 2 }}>
          <Box component="span" sx={{ fontFamily: font.mono, fontSize: '0.82rem' }}>
            {currentDisease.name || currentDisease.id}
          </Box>
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Tabs value={tab} onChange={(event, next) => setTab(next)} sx={{ mb: 3 }}>
        <Tab label="Library" />
        <Tab label="Define a disease" />
      </Tabs>

      {tab === LIBRARY_TAB ? (
        <DiseaseLibrary
          diseases={knownDiseases}
          loading={loading}
          currentDisease={currentDisease}
          onSelect={onDiseaseSelected}
        />
      ) : (
        <CustomDiseaseForm
          value={composer}
          onChange={setComposer}
          onSubmit={handleConfigureCustomDisease}
        />
      )}
    </Box>
  );
}

export default DiseaseDesigner;
