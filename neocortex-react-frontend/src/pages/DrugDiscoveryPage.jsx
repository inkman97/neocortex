import React, { useState } from 'react';
import { Alert, Button } from '@mui/material';
import WorkflowLayout from '../layout/WorkflowLayout';
import DiseaseDesigner from '../components/DiseaseDesigner';
import OptimizationConfig from '../components/OptimizationConfig';
import DiscoveryRunner from '../components/DiscoveryRunner';
import DiscoveryResults from '../components/DiscoveryResults';

const STEPS = ['Target disease', 'Optimization', 'Search', 'Optimal drug'];
const RUNNER_STEP = 2;

const STEP_NOTES = [
  {
    severity: 'info',
    text: 'Define the disease to treat. The search will look for a target profile that normalizes every neurotransmitter deviation.',
  },
  {
    severity: 'info',
    text: 'Set the search parameters. More iterations give better candidates and take longer. 50 to 200 is a workable range.',
  },
  {
    severity: 'warning',
    text: 'A search takes 10 to 30 minutes depending on the iteration count. Keep this page open until it finishes.',
  },
];

function DrugDiscoveryPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [diseaseDefinition, setDiseaseDefinition] = useState(null);
  const [optimizationConfig, setOptimizationConfig] = useState(null);
  const [discoveryResults, setDiscoveryResults] = useState(null);

  const handleNext = () => setActiveStep((step) => step + 1);
  const handleBack = () => setActiveStep((step) => step - 1);

  const handleReset = () => {
    setActiveStep(0);
    setDiseaseDefinition(null);
    setOptimizationConfig(null);
    setDiscoveryResults(null);
  };

  const handleDiscoveryComplete = (results) => {
    setDiscoveryResults(results);
    handleNext();
  };

  const canProceed = () => {
    switch (activeStep) {
      case 0:
        return diseaseDefinition !== null;
      case 1:
        return optimizationConfig !== null;
      case RUNNER_STEP:
        return false;
      default:
        return true;
    }
  };

  const renderStep = () => {
    switch (activeStep) {
      case 0:
        return (
          <DiseaseDesigner
            onDiseaseSelected={setDiseaseDefinition}
            currentDisease={diseaseDefinition}
          />
        );
      case 1:
        return (
          <OptimizationConfig
            disease={diseaseDefinition}
            onConfigComplete={setOptimizationConfig}
            currentConfig={optimizationConfig}
          />
        );
      case RUNNER_STEP:
        return (
          <DiscoveryRunner
            disease={diseaseDefinition}
            config={optimizationConfig}
            onDiscoveryComplete={handleDiscoveryComplete}
          />
        );
      case 3:
        return <DiscoveryResults results={discoveryResults} disease={diseaseDefinition} />;
      default:
        return null;
    }
  };

  const renderPrimaryAction = () => {
    if (activeStep === STEPS.length - 1) {
      return (
        <Button variant="contained" onClick={handleReset}>
          Search again
        </Button>
      );
    }
    if (activeStep === RUNNER_STEP) return null;
    return (
      <Button variant="contained" onClick={handleNext} disabled={!canProceed()}>
        Next
      </Button>
    );
  };

  const stepNote = STEP_NOTES[activeStep];

  return (
    <WorkflowLayout
      kicker="Inverse pharmacology"
      title="Start from the disease. Let the search return the compound."
      note="A genetic algorithm proposes molecular target profiles, scores each one on the brain model, and keeps what works."
      steps={STEPS}
      activeStep={activeStep}
      onBack={handleBack}
      primaryAction={renderPrimaryAction()}
    >
      {stepNote && (
        <Alert severity={stepNote.severity} sx={{ mb: 3 }}>
          {stepNote.text}
        </Alert>
      )}
      {renderStep()}
    </WorkflowLayout>
  );
}

export default DrugDiscoveryPage;
