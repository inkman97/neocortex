# NeoCortex

A virtual drug trial platform. You describe a drug by its molecular targets and a disease by its neurotransmitter profile, and NeoCortex simulates what happens to a spiking brain model over days of exposure.

Nothing about the outcome is hardcoded. Fatigue, heart rate, pain, muscle tension and the other physiological readouts are not rules written into the system: they emerge from simulated neurotransmitter concentrations through a coupling matrix derived from clinical literature.

---

## What it does

**Virtual trials.** Pick a compound from the library or design one from scratch, choose a disease model, and run it. The output is a time series of six neurotransmitters, mental state, and eight physiological channels.

**Drug discovery, in reverse.** Give it a disease and a genetic algorithm searches the space of molecular target profiles, scoring each candidate by actually simulating it in the diseased brain. It returns a target profile and a generated chemical structure.

**Two backends.** The same model runs on GPU via PyTorch, or on Intel Loihi neuromorphic hardware with a NumPy fallback when no board is present.

## Model

| | |
|---|---|
| Neurons | 100,000 for validation runs, GPU-scalable to millions, runs on CPU |
| Structure | 4 cortical columns x 6 layers, plus subcortical structures |
| Neurotransmitters | Serotonin, dopamine, noradrenaline, acetylcholine, GABA, glutamate |
| Receptors | 13 subtypes |
| Plasticity | STDP, BCM, synaptic scaling, three-factor learning, short-term plasticity |
| Pharmacokinetics | One-compartment model with absorption and elimination, Hill dose-response |
| Metabolites | Active metabolites with independent kinetics and their own targets |
| Physiology | 8 emergent parameters from 48 coupling coefficients |

## Repository layout

```
neocortex-react-frontend/    React 18 + MUI, the trial and discovery UI
neocortex-spring-backend/    Spring Boot 3.2, REST API and drug/disease library
neocortex-runpod/            Python, GPU simulation servers
neocortex_loihi/             Python, Intel Loihi port
```

The four modules deploy independently. The frontend talks to the Spring backend, which calls whichever Python server is configured. If the Python server is unreachable the backend does not fail: it falls back to its own mathematical model and flags the response with `used_neocortex: false`.

## Quick start

You need three processes running. Start the Python servers first.

### Python simulation servers

Requires **Python 3.11**. The pinned dependencies match the CUDA base image used by the Dockerfile and have no wheels beyond 3.11.

```bash
cd neocortex-runpod
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python gpu_server.py               # port 8000, trials
python run_discovery.py            # port 8001, discovery, separate terminal
```

`torch` is a 192 MB wheel that unpacks to roughly 10,000 files. On Windows, antivirus scanning makes this take ten to twenty minutes with no console output. Do not interrupt it.

Only `gpu_server.py` is needed to run trials. The discovery server is required only for the inverse search.

See [neocortex-runpod/RUN_LOCAL.md](neocortex-runpod/RUN_LOCAL.md) for troubleshooting and timing.

### Spring backend

Requires **JDK 17 or newer** and Maven.

```bash
cd neocortex-spring-backend
mvn spring-boot:run                # port 8080
```

Point it elsewhere with `GPU_SERVER_URL` if the Python servers are not on localhost. The discovery URL is derived by swapping the port to 8001, so both servers must keep their default ports.

### Frontend

```bash
cd neocortex-react-frontend
npm ci
npm start                          # port 3000
```

Set `REACT_APP_BACKEND_URL` if the backend is not at `http://localhost:8080/api`.

## API

**Trials server, port 8000**

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Backend and GPU availability |
| POST | `/simulate` | Run one drug against one disease |

**Discovery server, port 8001**

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Backend availability |
| POST | `/discover` | Genetic search for an optimal compound |

**Spring backend, port 8080**

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/trials/health` | Chain health, including GPU server reachability |
| GET | `/api/trials/drugs/library` | Known drugs |
| GET | `/api/trials/diseases/library` | Known disease models |
| POST | `/api/trials/simulate` | Run a trial |
| POST | `/api/discovery/start` | Start an async discovery job |
| GET | `/api/discovery/status/{jobId}` | Poll progress |

Interactive docs at `http://localhost:8000/docs` and `http://localhost:8080/swagger-ui.html`.

### Example

```bash
curl -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "drug": {
      "name": "Fluoxetine",
      "drug_class": "SSRI",
      "molecularTargets": [
        {"target": "sert_inhibition", "action": "mechanism", "potency": 0.85}
      ],
      "pharmacokinetics": {
        "halfLife_hours": 96, "tmax_hours": 6, "bioavailability": 0.72
      },
      "active_metabolites": []
    },
    "disease": {
      "name": "Depression",
      "serotonin_deficit": 0.4,
      "dopamine_deficit": 0.3
    },
    "dose_mg": 20,
    "typical_dose_mg": 20,
    "neurons": 10000,
    "duration_hours": 24,
    "sampling_interval_hours": 24
  }'
```

Target names must match the mechanism keys the simulator knows. The full list is in `neocortex-runpod/server_support/target_mapping.py`.

## Performance

Warmup is a fixed 2,000 steps regardless of trial duration, then 60 steps per simulated hour.

| Neurons | Duration | Hardware | Time |
|---|---|---|---|
| 10,000 | 24h | CPU | ~3 min |
| 100,000 | 48h | A100 | ~1 min |
| 100,000 | 48h | Loihi, single chip | 2-3 min at 1/300 the power |

The frontend defaults to 100,000 neurons over 7 days. On CPU, start at 10,000 neurons and one day.

## Validation

The platform was tested against cases where the clinical outcome is already known.

**Fluoxetine versus Reboxetine.** Both are monoamine reuptake inhibitors developed for depression. Fluoxetine was approved in 1987; reboxetine was rejected by the FDA in 2001 for lack of substantial evidence of effectiveness. The model separates them: fluoxetine restores serotonin, reboxetine raises noradrenaline without touching the serotonergic deficit that drives the mood and fatigue endpoints. The system was never given a rule stating that depression requires serotonin.

**Lamotrigine in epilepsy.** Excitation-inhibition ratio normalises from a pathological baseline into the therapeutic range through emergent glutamate reduction and GABA recovery.

**Levodopa in advanced Parkinson's.** Limited dopamine recovery, reflecting that with 70 percent nigral neuron loss the enzymatic machinery for conversion is itself depleted. Matches the modest clinical benefit observed in advanced disease.

**Drug discovery.** For an Alzheimer's profile the genetic algorithm converged on a dual-target compound combining acetylcholinesterase inhibition with moderate serotonin transporter inhibition, addressing the cognitive and neuropsychiatric sides of the disease together, and generated a chemical structure for it.

Full methods and results are in the paper.

## Limitations

This is research software under active development, not a validated clinical tool.

- The model is stochastic. No fixed seed is set, so absolute values vary between runs of the same configuration. Relative changes and the direction of effect are stable; individual concentrations are not exactly reproducible.
- Generated compounds are candidates on paper. Nothing has been synthesised or tested experimentally.
- Genetic variants such as CYP2D6 and COMT polymorphisms are not implemented.
- Drug-drug interactions require multi-drug simulation, which does not exist yet.
- Molecular docking predictions await experimental validation.

## Roadmap

Expansion to bipolar disorder, anxiety and ADHD. Integration of neuroimaging data for patient-specific digital twins. Multi-GPU scaling toward millions of neurons. Frameworks for organs beyond the brain.