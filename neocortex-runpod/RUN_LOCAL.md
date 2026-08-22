# Running the RunPod servers locally

Two FastAPI servers, independent of each other:

| Server | File | Port | Purpose |
|---|---|---|---|
| Trials | `gpu_server.py` | 8000 | `POST /simulate` — run one drug against one disease |
| Discovery | `run_discovery.py` | 8001 | `POST /discover` — genetic search for a compound |

Both fall back to CPU when no CUDA device is present. Neither needs a GPU to start.

## Setup

`requirements.txt` is pinned to match the CUDA base image in the Dockerfile.
Those pins only resolve on **Python 3.8 to 3.11**:

| Pin | Wheels available for |
|---|---|
| `numpy==1.24.3` | 3.8 – 3.11 |
| `torch==2.1.0` | 3.8 – 3.11 |
| `rdkit-pypi>=2022.9.5` | 3.7 – 3.11 (project renamed to `rdkit`) |

On Python 3.12+ pip finds no wheel, falls back to building numpy from source and
fails with `Cannot import 'setuptools.build_meta'`. On Windows that build will
not succeed regardless, since it needs a full MSVC toolchain.

### Option A — Python 3.11 (recommended)

```bash
cd neocortex-runpod
py -3.11 -m venv .venv           # Windows
.venv\Scripts\activate
# macOS / Linux: python3.11 -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
```

### Option B — keep Python 3.12 / 3.13 / 3.14

```bash
pip install -r requirements-local.txt
```

That file drops the stale pins and swaps `rdkit-pypi` for `rdkit`, which does
ship wheels through 3.14. Everything else is unchanged.

`supervisor` in `requirements.txt` is only for the container; local runs do not need it.

## Start

```bash
# terminal 1
PORT=8000 python gpu_server.py

# terminal 2
PORT=8001 python run_discovery.py
```

Run them from this directory: both insert `neocortex_realistico_gpu/` on
`sys.path` relative to their own location.

## Check

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8001/health
```

Interactive docs: http://127.0.0.1:8000/docs and http://127.0.0.1:8001/docs

Expected on a machine without CUDA:

```json
{"status":"healthy","neocortex_available":true,"gpu_available":false,
 "gpu_info":null,"physiological_tracking":true}
```

`neocortex_available: false` means the brain model failed to import. Check the
startup log for the ImportError rather than the health output.

## Smoke test

```bash
curl -X POST http://127.0.0.1:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "drug": {
      "name": "Fluoxetine",
      "drug_class": "SSRI",
      "molecularTargets": [
        {"target":"sert_inhibition","action":"mechanism","potency":0.85}
      ],
      "pharmacokinetics": {"halfLife_hours":96,"tmax_hours":6,"bioavailability":0.72},
      "active_metabolites": []
    },
    "disease": {"name":"Depression","serotonin_deficit":0.4,"dopamine_deficit":0.3},
    "dose_mg": 20,
    "typical_dose_mg": 20,
    "neurons": 10000,
    "duration_hours": 24,
    "sampling_interval_hours": 24
  }'
```

## Timing

On CPU this is slow, and the cost scales with neurons x duration. Measured here:
10.000 neurons over 24 simulated hours took about 2 minutes 40 seconds.

The frontend defaults to 100.000 neurons over 7 days, which is roughly two
orders of magnitude more work. Start small when testing locally.

`/simulate` is rate limited to 10 requests per minute, `/discover` to 5.

## Wiring the Java backend

`application.yml` points at `http://localhost:8000` by default. The discovery
service derives its own URL by swapping the port to 8001, so both servers must
be up. Override with:

```bash
export GPU_SERVER_URL=http://localhost:8000
```

If port 8000 is unreachable the backend does not fail: it falls back to its own
mathematical model and flags the response with `used_neocortex: false`.
