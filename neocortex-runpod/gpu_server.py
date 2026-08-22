#!/usr/bin/env python3
"""NeoCortex GPU server.

FastAPI front end for drug trials run on GPU-accelerated spiking brain models.
Responses carry both neurochemistry and the eight physiological channels.
"""

import os
import sys
import traceback
from datetime import datetime
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'neocortex_realistico_gpu'))

import torch
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from drug_simulator import ActiveMetabolite, DiseaseProfile, DrugMechanism, DrugSimulator
from server_support.schemas import (
    DiseaseDefinition,
    DrugDefinition,
    MolecularTarget,
    Pharmacokinetics,
    TrialRequest,
    TrialResponse,
)
from server_support.target_mapping import UNRESOLVED, normalize_action, resolve_mechanism_key

try:
    from brain import RealisticBrain
    NEOCORTEX_AVAILABLE = True
    print("[GPU] NeoCortex GPU loaded successfully")
except ImportError as import_error:
    NEOCORTEX_AVAILABLE = False
    print(f"[GPU] NeoCortex not available: {import_error}")

SERVER_VERSION = "2.1.0"
DEFAULT_COLUMNS = 4
DEFAULT_METABOLITE_HILL = 1.5
RATE_LIMIT = "10/minute"

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="NeoCortex Virtual Drug Trial Server",
    description="GPU-accelerated brain simulation for drug trials",
    version=SERVER_VERSION,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _gpu_info(include_reserved=False):
    if not torch.cuda.is_available():
        return None

    info = {"name": torch.cuda.get_device_name(0)}
    if include_reserved:
        info["memory_allocated_gb"] = torch.cuda.memory_allocated(0) / 1e9
        info["memory_reserved_gb"] = torch.cuda.memory_reserved(0) / 1e9
    else:
        info["memory_used_gb"] = torch.cuda.memory_allocated(0) / 1e9
    return info


@app.get("/")
async def root():
    return {
        "service": "NeoCortex GPU Server",
        "version": SERVER_VERSION,
        "status": "online",
        "neocortex_available": NEOCORTEX_AVAILABLE,
        "gpu_available": torch.cuda.is_available() if NEOCORTEX_AVAILABLE else False,
        "features": {
            "neurochemistry": True,
            "physiological_parameters": True,
            "advanced_plasticity": True,
            "receptor_system": True,
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "neocortex_available": NEOCORTEX_AVAILABLE,
        "gpu_available": torch.cuda.is_available(),
        "gpu_info": _gpu_info(include_reserved=True),
        "physiological_tracking": True,
    }


@app.post("/simulate", response_model=TrialResponse)
@limiter.limit(RATE_LIMIT)
async def simulate_trial(request: Request, trial_request: TrialRequest):
    """Run a virtual drug trial and return neurochemical and physiological traces."""
    trial_id = f"trial_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    _log_trial_start(trial_id, trial_request.drug)

    if not NEOCORTEX_AVAILABLE:
        raise HTTPException(status_code=503, detail="NeoCortex not available")

    try:
        brain = _build_brain(trial_request.neurons)
        _enable_advanced_plasticity(brain)

        simulator = DrugSimulator(
            brain=brain,
            drug_mechanism=_create_drug_mechanism(trial_request.drug.molecularTargets),
            disease_profile=_build_disease_profile(trial_request.disease),
            pharmacokinetics=_build_pharmacokinetics(trial_request.drug.pharmacokinetics),
            active_metabolites=_build_metabolites(trial_request.drug.active_metabolites),
        )

        timepoints = simulator.run_trial(
            dose_mg=trial_request.dose_mg,
            typical_dose_mg=trial_request.typical_dose_mg,
            duration_hours=trial_request.duration_hours,
            sampling_interval_hours=trial_request.sampling_interval_hours,
        )

        print(f"[TRIAL] Complete, {len(timepoints)} timepoints recorded")

        return TrialResponse(
            trial_id=trial_id,
            success=True,
            timepoints=timepoints,
            used_neocortex=True,
            neurons=trial_request.neurons,
            duration_hours=trial_request.duration_hours,
            gpu_info=_gpu_info(),
        )

    except Exception as trial_error:
        print(f"[ERROR] Trial failed: {trial_error}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Trial simulation failed: {trial_error}")


def _log_trial_start(trial_id, drug: DrugDefinition):
    print(f"[TRIAL START] {trial_id} drug={drug.name}")
    for metabolite in drug.active_metabolites or []:
        print(
            f"  metabolite {metabolite.name}: "
            f"t1/2={metabolite.halfLife_hours}h, "
            f"formation={metabolite.formation_fraction:.0%}"
        )


def _build_brain(n_neurons: int):
    print(f"[BRAIN] Creating RealisticBrain with {n_neurons} neurons")
    brain = RealisticBrain(n_neurons=n_neurons, n_columns=DEFAULT_COLUMNS, debug=False)
    print("[BRAIN] Ready")
    return brain


def _enable_advanced_plasticity(brain):
    try:
        from plasticity_integration import integrate_advanced_plasticity
    except ImportError as plasticity_error:
        print(f"[PLASTICITY] Not available ({plasticity_error}), continuing with standard STDP")
        return None

    config = integrate_advanced_plasticity(brain=brain, enable_all=True, debug=False)
    print(
        "[PLASTICITY] Active - "
        f"BCM={config.use_bcm}, scaling={config.use_synaptic_scaling}, "
        f"three_factor={config.use_three_factor}, STP={config.use_stp}"
    )
    return config


def _build_disease_profile(disease: DiseaseDefinition) -> DiseaseProfile:
    profile = DiseaseProfile(
        serotonin_deficit=disease.serotonin_deficit,
        dopamine_deficit=disease.dopamine_deficit,
        noradrenaline_deficit=disease.noradrenaline_deficit,
        acetylcholine_deficit=disease.acetylcholine_deficit,
        gaba_deficit=disease.gaba_deficit,
        glutamate_deficit=disease.glutamate_deficit,
    )
    print(
        f"[DISEASE] {disease.name}: "
        f"5HT={disease.serotonin_deficit}, DA={disease.dopamine_deficit}, "
        f"NE={disease.noradrenaline_deficit}, ACh={disease.acetylcholine_deficit}, "
        f"GABA={disease.gaba_deficit}, Glu={disease.glutamate_deficit}"
    )
    return profile


def _build_pharmacokinetics(pk: Pharmacokinetics) -> Pharmacokinetics:
    return Pharmacokinetics(
        halfLife_hours=pk.halfLife_hours,
        tmax_hours=pk.tmax_hours,
        bioavailability=pk.bioavailability,
        vd_L_kg=pk.vd_L_kg,
    )


def _build_metabolites(metabolite_requests) -> List[ActiveMetabolite]:
    metabolites = []

    for request in metabolite_requests or []:
        targets = [
            {
                'target': target['target'],
                'action': target.get('action', 'mechanism'),
                'potency': target['potency'],
                'hill': target.get('hill', DEFAULT_METABOLITE_HILL),
            }
            for target in request.targets
        ]

        metabolites.append(
            ActiveMetabolite(
                name=request.name,
                formation_fraction=request.formation_fraction,
                halfLife_hours=request.halfLife_hours,
                tmax_hours=request.tmax_hours,
                targets=targets,
            )
        )

    if metabolites:
        print(f"[METABOLITES] {len(metabolites)} initialized")

    return metabolites


def _create_drug_mechanism(targets: List[MolecularTarget]) -> DrugMechanism:
    """Convert HTTP molecular targets into DrugMechanism keyword arguments."""
    kwargs = {}

    print(f"[DRUG MECHANISM] Converting {len(targets)} molecular targets")

    for target in targets:
        action = normalize_action(target.action)
        mechanism_key = resolve_mechanism_key(target.target, action)

        if mechanism_key is UNRESOLVED:
            print(f"  WARNING: unknown target '{target.target}' with action '{target.action}'")
            continue

        if mechanism_key is None:
            continue

        kwargs[mechanism_key] = target.potency
        print(f"  {target.target} ({target.action}) -> {mechanism_key} = {target.potency}")

    print(f"[DRUG MECHANISM] {len(kwargs)} parameters set")

    return DrugMechanism(**kwargs)


if __name__ == "__main__":
    print(f"NeoCortex GPU Server {SERVER_VERSION} - starting on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")), log_level="info")
