#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║              NEOCORTEX LOIHI DRUG DISCOVERY SERVER          ║
║                                                                    ║
║  FastAPI server separato per Drug Discovery                       ║
║  Gira su porta 8001 (run_gpu.py su 8000)                         ║
║                                                                    ║
║  NO MODIFICATIONS TO run_gpu.py NEEDED!                           ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import traceback

# Add NeoCortex to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uvicorn
# torch not needed on Loihi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from drug_discovery_loihi import discover_drug, OptimizationConfig, DiseaseProfile

DISCOVERY_RATE_LIMIT = "5/minute"
DEFICIT_KEYS = (
    'serotonin_deficit',
    'dopamine_deficit',
    'noradrenaline_deficit',
    'acetylcholine_deficit',
    'gaba_deficit',
    'glutamate_deficit',
)

# Import NeoCortex
try:
    from brain_loihi import create_brain
    NEOCORTEX_AVAILABLE = True
    print("[DISCOVERY] NeoCortex Loihi loaded successfully")
except ImportError as import_error:
    NEOCORTEX_AVAILABLE = False
    print(f"[DISCOVERY] NeoCortex not available: {import_error}")

try:
    from loihi_hardware_init import NXSDK_AVAILABLE as LOIHI_HARDWARE_AVAILABLE
except ImportError:
    LOIHI_HARDWARE_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════

class FitnessWeights(BaseModel):
    ntCorrection: float = Field(0.6, alias="nt_correction")
    sideEffects: float = Field(0.2, alias="side_effects")
    complexity: float = Field(0.1)
    speed: float = Field(0.1)

    class Config:
        populate_by_name = True


class OptimizationConfigRequest(BaseModel):
    iterations: int = Field(100, ge=10, le=1000)
    population_size: int = Field(50, ge=1, le=500, alias="populationSize")
    mutation_rate: float = Field(0.15, ge=0, le=1, alias="mutationRate")
    crossover_rate: float = Field(0.7, ge=0, le=1, alias="crossoverRate")
    elite_count: int = Field(5, ge=1, le=20, alias="eliteCount")
    selection_method: str = Field("tournament", alias="selectionMethod")
    weights: FitnessWeights = Field(default_factory=FitnessWeights)
    max_targets: int = Field(5, ge=1, le=10, alias="maxTargets")
    min_potency: float = Field(0.1, ge=0, le=1, alias="minPotency")
    max_potency: float = Field(1.0, ge=0, le=1, alias="maxPotency")
    trial_duration: int = Field(168, ge=24, le=672, alias="trialDuration")
    sampling_interval: int = Field(24, ge=6, le=48, alias="samplingInterval")

    class Config:
        populate_by_name = True


class DiscoveryRequest(BaseModel):
    disease_profile: Dict[str, float] = Field(..., alias="diseaseProfile")
    config: OptimizationConfigRequest
    neurons: int = Field(100000, ge=1000, le=1000000)
    jobId: Optional[str] = None

    class Config:
        populate_by_name = True


class MolecularStructure(BaseModel):
    smiles: str
    properties: Dict[str, float]
    alternatives: Optional[List[Dict]] = None


class OptimalDrug(BaseModel):
    name: str
    id: str
    drugClass: str = Field(..., alias="class")
    typical_dose_mg: float
    dose_range: List[float]
    molecularTargets: List[Dict]
    pharmacokinetics: Dict
    molecular_structure: Optional[MolecularStructure] = None
    optimization: Optional[Dict] = None

    class Config:
        populate_by_name = True


class DiscoveryResponse(BaseModel):
    optimal_drug: OptimalDrug
    fitness_history: List[Dict]
    final_fitness: float
    generations: int


# ═══════════════════════════════════════════════════════════════════
# API
# ═══════════════════════════════════════════════════════════════════
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="NeoCortex Drug Discovery Server",
    description="Standalone server for AI-powered drug discovery",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Service banner."""
    return {
        "service": "NeoCortex Loihi Drug Discovery Server",
        "version": "1.0.0",
        "status": "online",
        "neocortex_available": NEOCORTEX_AVAILABLE,
        "backend": _available_backend(),
        "port": 8001,
        "features": {
            "drug_discovery": True,
            "molecular_structure_generation": True,
            "genetic_algorithm": True
        }
    }


@app.get("/health")
async def health():
    """Report whether the neuromorphic board is reachable."""
    return {
        "status": "healthy",
        "neocortex_available": NEOCORTEX_AVAILABLE,
        "backend": _available_backend(),
        "loihi_hardware": LOIHI_HARDWARE_AVAILABLE,
    }


def _available_backend() -> str:
    return "loihi" if LOIHI_HARDWARE_AVAILABLE else "numpy"

@app.post("/discover", response_model=DiscoveryResponse)
@limiter.limit(DISCOVERY_RATE_LIMIT)
async def discover_optimal_drug(request: Request, discovery_request: DiscoveryRequest):
    """Search for the compound that best corrects a disease profile."""
    print("[DISCOVERY] Request received")

    if not NEOCORTEX_AVAILABLE:
        raise HTTPException(status_code=503, detail="NeoCortex not available")

    try:
        disease_profile = _build_disease_profile(discovery_request.disease_profile)
        config = _build_optimization_config(discovery_request.config)
        brain = _build_brain(discovery_request.neurons)

        print("[DISCOVERY] Starting genetic algorithm")

        result = discover_drug(
            brain=brain,
            disease_profile=disease_profile,
            config=config,
            generate_structure=True,
            job_id=discovery_request.jobId
        )

        _log_result(result)

        return result

    except Exception as discovery_error:
        print(f"[ERROR] Discovery failed: {discovery_error}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Drug discovery optimization failed: {discovery_error}"
        )


def _build_disease_profile(disease_data: Dict) -> DiseaseProfile:
    profile = DiseaseProfile(**{
        key: float(disease_data.get(key, 0.0)) for key in DEFICIT_KEYS
    })

    print("[DISEASE] "
          f"5HT={profile.serotonin_deficit:+.2f}, DA={profile.dopamine_deficit:+.2f}, "
          f"NE={profile.noradrenaline_deficit:+.2f}, ACh={profile.acetylcholine_deficit:+.2f}, "
          f"GABA={profile.gaba_deficit:+.2f}, Glu={profile.glutamate_deficit:+.2f}")

    return profile


def _build_optimization_config(config_data) -> OptimizationConfig:
    weights = config_data.weights

    config = OptimizationConfig(
        iterations=config_data.iterations,
        population_size=config_data.population_size,
        mutation_rate=config_data.mutation_rate,
        crossover_rate=config_data.crossover_rate,
        elite_count=config_data.elite_count,
        selection_method=config_data.selection_method,
        weight_nt_correction=weights.ntCorrection,
        weight_side_effects=weights.sideEffects,
        weight_complexity=weights.complexity,
        weight_speed=weights.speed,
        max_targets=config_data.max_targets,
        min_potency=config_data.min_potency,
        max_potency=config_data.max_potency,
        trial_duration=config_data.trial_duration,
        sampling_interval=config_data.sampling_interval,
        weight_docking=getattr(weights, 'docking', 0.0),
        use_docking=getattr(config_data, 'use_docking', False),
        docking_exhaustiveness=getattr(config_data, 'docking_exhaustiveness', 8),
    )

    print(f"[CONFIG] {config.iterations} generations x {config.population_size} candidates "
          f"= {config.iterations * config.population_size} evaluations, "
          f"trial {config.trial_duration}h ({config.trial_duration / 24:.1f} days), "
          f"sampled every {config.sampling_interval}h")

    return config


def _build_brain(neurons: int):
    """Prefer the neuromorphic board, fall back to the NumPy simulation."""
    print(f"[BRAIN] {neurons:,} neurons, attempting Loihi hardware")

    try:
        brain = create_brain(n_neurons=neurons, backend="loihi", debug=False)
        print("[BRAIN] Running on Loihi hardware")
    except RuntimeError as hardware_error:
        print(f"[BRAIN] Hardware unavailable ({hardware_error}), using NumPy")
        brain = create_brain(n_neurons=neurons, backend="numpy", debug=False)
        print("[BRAIN] Running on NumPy")

    print("[BRAIN] Ready, disease will be applied by the fitness evaluator")
    return brain


def _log_result(result: Dict):
    optimal = result['optimal_drug']
    print(f"[DISCOVERY] Complete: {optimal['name']}, "
          f"fitness {result['final_fitness']:.3f} after {result['generations']} generations")

    structure = optimal.get('molecular_structure')
    if structure:
        print(f"[DISCOVERY] SMILES: {structure['smiles']}")


if __name__ == "__main__":
    print("NeoCortex Loihi Drug Discovery Server - starting on http://0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")), log_level="info")
