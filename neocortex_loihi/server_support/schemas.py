"""Request and response payloads exposed by the GPU server."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MolecularTarget(BaseModel):
    target: str = Field(..., description="Target name (SERT, DAT, D2, etc.)")
    action: str = Field(..., description="Action type (inhibitor, antagonist, etc.)")
    potency: float = Field(..., ge=0, le=1, description="Potency 0-1")
    ki_nM: Optional[float] = Field(None, description="Ki in nM (optional)")


class Pharmacokinetics(BaseModel):
    halfLife_hours: float = Field(24.0, gt=0)
    tmax_hours: float = Field(2.0, gt=0)
    bioavailability: float = Field(0.7, ge=0, le=1)
    vd_L_kg: Optional[float] = Field(20.0, gt=0)


class ActiveMetaboliteRequest(BaseModel):
    name: str
    formation_fraction: float = Field(..., ge=0, le=1)
    halfLife_hours: float = Field(..., gt=0)
    tmax_hours: float = Field(..., gt=0)
    targets: List[Dict]


class DrugDefinition(BaseModel):
    name: str
    drug_class: Optional[str] = None
    molecularTargets: List[MolecularTarget]
    pharmacokinetics: Pharmacokinetics
    active_metabolites: Optional[List[ActiveMetaboliteRequest]] = None


class DiseaseDefinition(BaseModel):
    name: str
    serotonin_deficit: float = Field(0.0, ge=-1, le=1)
    dopamine_deficit: float = Field(0.0, ge=-1, le=1)
    noradrenaline_deficit: float = Field(0.0, ge=-1, le=1)
    acetylcholine_deficit: float = Field(0.0, ge=-1, le=1)
    gaba_deficit: float = Field(0.0, ge=-1, le=1)
    glutamate_deficit: float = Field(0.0, ge=-1, le=1)


class TrialRequest(BaseModel):
    drug: DrugDefinition
    disease: DiseaseDefinition
    dose_mg: float = Field(..., gt=0)
    typical_dose_mg: float = Field(..., gt=0)
    neurons: int = Field(100000, ge=10000, le=1000000)
    duration_hours: int = Field(168, ge=1, le=8760)
    sampling_interval_hours: int = Field(24, ge=1, le=168)


class TrialTimepoint(BaseModel):
    hours: float
    days: float
    phase: str

    drug_concentration: float

    serotonin: float
    dopamine: float
    noradrenaline: float
    acetylcholine: float
    gaba: float
    glutamate: float

    arousal: float
    valence: float
    firing_rate: float
    dominant_emotion: str

    heart_rate: float = Field(..., description="Heart rate 0-1 (0=bradycardia, 0.5=normal, 1=tachycardia)")
    respiratory_rate: float = Field(..., description="Respiratory rate 0-1 (0=slow, 0.5=normal, 1=hyperventilation)")
    skin_conductance: float = Field(..., description="Skin conductance 0-1 (arousal/stress)")
    muscle_tension: float = Field(..., description="Muscle tension 0-1 (0=relaxed, 1=tense)")
    gut_feeling: float = Field(..., description="Gut feeling 0-1 (0=discomfort, 0.5=neutral, 1=comfort)")
    temperature: float = Field(..., description="Body temperature sensation 0-1")
    pain: float = Field(..., description="Pain level 0-1")
    fatigue: float = Field(..., description="Fatigue level 0-1 (0=energetic, 1=exhausted)")


class TrialResponse(BaseModel):
    trial_id: str
    success: bool
    timepoints: List[TrialTimepoint]
    used_neocortex: bool
    neurons: int
    duration_hours: int
    gpu_info: Optional[Dict] = None
    fallback_reason: Optional[str] = None
