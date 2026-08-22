import React, { useState } from 'react';
import { Button } from '@mui/material';
import WorkflowLayout from '../layout/WorkflowLayout';
import DrugDesigner from '../components/DrugDesigner';
import DiseaseDesigner from '../components/DiseaseDesigner';
import TrialRunner from '../components/TrialRunner';
import ResultsViewer from '../components/ResultsViewer';

const STEPS = ['Define drug', 'Select disease', 'Configure & run', 'Read results'];
const RUNNER_STEP = 2;

function DrugTrialPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [drugDefinition, setDrugDefinition] = useState(null);
  const [diseaseDefinition, setDiseaseDefinition] = useState(null);
  const [trialResults, setTrialResults] = useState(null);

  const handleNext = () => setActiveStep((step) => step + 1);
  const handleBack = () => setActiveStep((step) => step - 1);

  const handleReset = () => {
    setActiveStep(0);
    setDrugDefinition(null);
    setDiseaseDefinition(null);
    setTrialResults(null);
  };

  const handleTrialCompleted = (results) => {
    setTrialResults(results);
    handleNext();
  };

  const canProceed = () => {
    switch (activeStep) {
      case 0:
        return drugDefinition !== null;
      case 1:
        return diseaseDefinition !== null;
      case RUNNER_STEP:
        return false;
      default:
        return true;
    }
  };

  const renderStep = () => {
    switch (activeStep) {
      case 0:
        return <DrugDesigner onDrugConfigured={setDrugDefinition} currentDrug={drugDefinition} />;
      case 1:
        return (
          <DiseaseDesigner onDiseaseSelected={setDiseaseDefinition} currentDisease={diseaseDefinition} />
        );
      case RUNNER_STEP:
        return (
          <TrialRunner
            drug={drugDefinition}
            disease={diseaseDefinition}
            onTrialCompleted={handleTrialCompleted}
          />
        );
      case 3:
        return <ResultsViewer results={trialResults} />;
      default:
        return null;
    }
  };

  const renderPrimaryAction = () => {
    if (activeStep === STEPS.length - 1) {
      return (
        <Button variant="contained" onClick={handleReset}>
          Start a new trial
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

  return (
    <WorkflowLayout
      kicker="Virtual trial"
      title="Run a compound against a brain model and watch what it does."
      note="Pick or design a drug, choose the disease state to treat, then simulate the spiking model over days of exposure."
      steps={STEPS}
      activeStep={activeStep}
      onBack={handleBack}
      primaryAction={renderPrimaryAction()}
    >
      {renderStep()}
    </WorkflowLayout>
  );
}

export default DrugTrialPage;
