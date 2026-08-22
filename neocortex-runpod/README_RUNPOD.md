#  NeoCortex GPU Server - Biologically Realistic Brain Simulation & AI Drug Discovery

**Emergent neural simulation platform for psychiatric drug trials and AI-powered drug optimization**

---

##  **What is NeoCortex?**

NeoCortex is a **GPU-accelerated biologically realistic brain simulator** that models:

- **100,000+ spiking neurons** (cortical columns, realistic connectivity)
- **6 neurotransmitter systems** (5HT, DA, NE, ACh, GABA, Glutamate)
- **Emergent embodiment** (heart rate, breathing, gut feeling, muscle tension)
- **Psychiatric disease states** (Depression, Alzheimer's, Parkinson's, Schizophrenia, etc.)
- **Pharmacological interventions** (SSRIs, antipsychotics, cholinesterase inhibitors, etc.)

### **Key Features:**

[OK] **Drug Trial Simulation** - Test any psychiatric drug on any disease in minutes  
[OK] **AI Drug Discovery** - Genetic algorithm finds optimal multi-target drugs  
[OK] **Molecular Structure Generation** - Generates SMILES with drug-likeness validation  
[OK] **Molecular Docking** - AutoDock Vina validates real binding affinity  
[OK] **Emergent Psychology** - Mood, arousal, emotions emerge from neural dynamics  
[OK] **Zero Hardcoding** - Drug effects emerge from molecular mechanisms, not predefined rules

---

##  **Capabilities**

### **1 Drug Trial Simulation** (`run_gpu.py` - Port 8000)

Simulate how **any drug** affects **any disease** over time.

**Features:**
- Supports 50+ psychiatric/neurological drugs (SSRIs, antipsychotics, stimulants, etc.)
- Models pharmacokinetics (absorption, half-life, dosing)
- Tracks 6 neurotransmitters + 8 physiological parameters
- Outputs time-series data (hourly/daily samples)

**Example Request:**
```json
POST http://localhost:8000/simulate
{
  "drug": "fluoxetine",
  "disease": "depression",
  "dose_mg": 20,
  "duration_hours": 168,
  "neurons": 100000
}
```

**Output:**
```json
{
  "timepoints": [
    {
      "hours": 0,
      "serotonin": 0.45,
      "dopamine": 0.52,
      "arousal": 0.38,
      "valence": -0.25,
      "heart_rate": 0.45,
      ...
    },
    ...
  ]
}
```

---

### **2 AI Drug Discovery** (`run_discovery_server.py` - Port 8001)

**Genetic algorithm** evolves optimal multi-target drugs for any disease.

**Features:**
- Explores 23 molecular targets (SERT, DAT, AChE, D2, MAO-A, GABA-A, etc.)
- Optimizes for NT correction, side effects, complexity, speed
- Generates molecular structures (SMILES)
- **NEW: Molecular docking validation** (AutoDock Vina)
- Auto-selects target protein based on disease (e.g., AChE for Alzheimer's)

**Optimization Objectives:**
1. **NT Correction** (50%): Normalize neurotransmitter deficits
2. **Docking Score** (35%): Real binding affinity to target protein
3. **Minimize Side Effects** (8%): Avoid off-target changes
4. **Drug Complexity** (4%): Prefer simpler molecules
5. **Action Speed** (3%): Prefer faster-acting drugs

**Example Request:**
```json
POST http://localhost:8001/discover
{
  "disease": {
    "name": "Alzheimer's Disease",
    "profile": {
      "acetylcholine_deficit": 0.60,
      "serotonin_deficit": 0.15
    }
  },
  "config": {
    "iterations": 100,
    "populationSize": 50,
    "weights": {
      "ntCorrection": 0.50,
      "docking": 0.35,
      "sideEffects": 0.08
    },
    "useDocking": true
  },
  "neurons": 100000
}
```

**Output:**
```json
{
  "optimal_drug": {
    "name": "AI-Discovered-825",
    "molecularTargets": [
      {"target": "ache_inhibition", "potency": 0.87},
      {"target": "sert_inhibition", "potency": 0.31}
    ],
    "molecular_structure": {
      "smiles": "C1CCN(CC1)CCc2ccc(OC)c(OC)c2C(=O)Nc3ccccc3",
      "properties": {
        "molecular_weight": 368.5,
        "logp": 3.2,
        "qed_score": 0.72,
        "binding_affinity_kcal_mol": -9.2
      }
    }
  },
  "final_fitness": 0.825
}
```

---

### **3 Molecular Docking** (AutoDock Vina Integration)

**Validates** that generated molecules **actually bind** to target proteins.

**Supported Targets:**
- **AChE** (Acetylcholinesterase) - Alzheimer's, dementia
- **SERT** (Serotonin Transporter) - Depression, anxiety
- **DAT** (Dopamine Transporter) - Parkinson's, ADHD
- **MAO-A** (Monoamine Oxidase A) - Depression
- **D2** (Dopamine D2 Receptor) - Schizophrenia, psychosis
- **GABA-A** (GABA-A Receptor) - Anxiety, epilepsy

**Auto-Selection:**
System automatically picks the correct protein based on disease profile:
- **Alzheimer's** → AChE
- **Depression** → SERT
- **Parkinson's** → DAT
- **Schizophrenia** → D2
- **Anxiety** → GABA-A

**Docking Scores:**
- `-5 kcal/mol` = Weak binding (poor drug candidate)
- `-9 kcal/mol` = Good binding (promising)
- `-11 kcal/mol` = Strong binding (excellent)

---

##  **Setup**

### **1. Prepare Files**
```bash
# Copy NeoCortex GPU module
cp -r /path/to/neocortex_realistico/neocortex_realistico_gpu ./

# You should have:
runpod_server/
├── run_gpu.py                    # Drug trial server (port 8000)
├── run_discovery_server.py       # Drug discovery server (port 8001)
├── drug_simulator.py
├── drug_discovery.py
├── molecular_generator_ai.py
├── docking_utils.py              # NEW: Docking integration
├── download_protein.py           # NEW: PDB downloader
├── prepare_receptor.py           # NEW: PDBQT preparation
├── requirements.txt
├── Dockerfile
├── README.md
└── neocortex_realistico_gpu/
    ├── __init__.py
    ├── brain.py
    ├── core/
    ├── embodiment/
    └── ...
```

### **2. Install Dependencies**
```bash
# Python packages
pip install -r requirements.txt

# Molecular docking tools (REQUIRED for docking)
conda install -c conda-forge autodock-vina openbabel

# Verify installation
vina --version
obabel --version
```

### **3. Download Protein Structures** (for docking)
```bash
cd neocortex_realistico_gpu

# Minimum: AChE for Alzheimer's
python download_protein.py 4EY7
python prepare_receptor.py 4EY7

# Optional: Other targets
python download_protein.py 5I6X  # SERT (Depression)
python download_protein.py 4XP4  # DAT (Parkinson's)
python download_protein.py 6CM4  # D2 (Schizophrenia)
python download_protein.py 6D6U  # GABA-A (Anxiety)
```

### **4. Build Docker Image**
```bash
docker build -t neocortex-gpu-server .
```

### **5. Test Locally** (Optional)
```bash
# Start both servers
docker run --gpus all -p 8000:8000 -p 8001:8001 neocortex-gpu-server

# Or run separately:
python run_gpu.py              # Port 8000 (trials)
python run_discovery_server.py # Port 8001 (discovery)
```

Test endpoints:
```bash
# Drug trials
curl http://localhost:8000/health

# Drug discovery
curl http://localhost:8001/health
```

---

##  **Deploy to RunPod**

### **Option A: Docker Hub**

1. Push image:
```bash
docker tag neocortex-gpu-server yourusername/neocortex-gpu-server:latest
docker push yourusername/neocortex-gpu-server:latest
```

2. On RunPod:
    - Go to "Deploy" → "GPU Instances"
    - Choose GPU (RTX 3090 or A6000 recommended)
    - Select "Docker Image"
    - Enter: `yourusername/neocortex-gpu-server:latest`
    - Expose ports: **8000, 8001**
    - Deploy!

### **Option B: GitHub + RunPod Automatic Build**

1. Push code to GitHub repo
2. On RunPod:
    - Connect GitHub repo
    - RunPod will auto-build from Dockerfile
    - Deploy

---

##  **Configuration**

### **Environment Variables**

- `PORT`: Drug trial server port (default: 8000)
- `DISCOVERY_PORT`: Drug discovery port (default: 8001)

### **GPU Requirements**

| Use Case | Minimum GPU | Recommended GPU | Notes |
|----------|-------------|-----------------|-------|
| **Drug Trials** (100K neurons) | RTX 3060 (12GB) | RTX 3090 (24GB) | 1-3 min/trial |
| **Drug Discovery** (10 gen, 50 pop) | RTX 3090 (24GB) | A6000 (48GB) | 4-8 hours |
| **Drug Discovery + Docking** | RTX 3090 (24GB) | A100 (40GB) | 8-12 hours |
| **Large Simulations** (>500K neurons) | A6000 (48GB) | A100 (80GB) | Research |

**Docking Impact:**
- Adds ~30 seconds per candidate
- 10 generations × 50 candidates = 25 minutes extra
- Use `exhaustiveness=4` for faster (less accurate) docking

---

##  **Testing**

Once deployed, get your RunPod URL: `https://your-pod-id.runpod.io`

### **1. Health Checks**
```bash
# Drug trials server
curl https://your-pod-id.runpod.io:8000/health

# Drug discovery server
curl https://your-pod-id.runpod.io:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "neocortex_available": true,
  "gpu_available": true,
  "docking_available": true,
  "gpu_info": {
    "name": "NVIDIA RTX 3090",
    "memory_gb": 24.0
  }
}
```

### **2. Run Drug Trial**
```bash
curl -X POST https://your-pod-id.runpod.io:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "drug": "fluoxetine",
    "disease": "depression",
    "dose_mg": 20,
    "duration_hours": 168,
    "neurons": 100000
  }'
```

### **3. Run Drug Discovery**
```bash
curl -X POST https://your-pod-id.runpod.io:8001/discover \
  -H "Content-Type: application/json" \
  -d '{
    "disease": {
      "name": "Alzheimers Disease",
      "profile": {
        "acetylcholine_deficit": 0.60
      }
    },
    "config": {
      "iterations": 10,
      "populationSize": 10,
      "weights": {
        "ntCorrection": 0.50,
        "docking": 0.35
      },
      "useDocking": true
    },
    "neurons": 50000
  }'
```

---

##  **Cost Optimization**

| Strategy | Savings | Notes |
|----------|---------|-------|
| **Auto-pause** | ~80% | Enable in RunPod settings |
| **Spot instances** | 50-70% | May be interrupted |
| **Right-size GPU** | 30-50% | Don't use A100 for small trials |
| **Reduce neurons** | 40% | 50K vs 100K (minimal accuracy loss) |
| **Disable docking** | 30% | For fast exploration |
| **Lower exhaustiveness** | 20% | `exhaustiveness=4` vs 8 |

**Estimated Costs (RTX 3090, on-demand):**
- Drug trial (1 week, 100K neurons): $0.05
- Drug discovery (100 gen, no docking): $2-3
- Drug discovery (100 gen, with docking): $4-6

---

##  **Troubleshooting**

### **Out of Memory**

**Symptoms:** CUDA OOM errors

**Solutions:**
- [OK] Reduce `neurons` (try 50K instead of 100K)
- [OK] Reduce `duration_hours` (try 24h instead of 168h)
- [OK] Reduce `populationSize` (try 30 instead of 50)
- [OK] Disable docking (`useDocking: false`)
- [OK] Use larger GPU (A6000 or A100)

### **Slow Drug Discovery**

**Expected Times:**
- 10 generations, 10 candidates, no docking: ~5 minutes
- 100 generations, 50 candidates, no docking: ~2 hours
- 100 generations, 50 candidates, with docking: ~8 hours

**Speed Up:**
- [OK] Reduce `iterations` (try 50 instead of 100)
- [OK] Reduce `populationSize` (try 30 instead of 50)
- [OK] Set `dockingExhaustiveness: 4` (faster but less accurate)
- [OK] Disable docking for initial exploration

### **Docking Failures**

**Symptoms:** `[DOCKING] ERROR: Receptor file not found`

**Solutions:**
- [OK] Run `python download_protein.py 4EY7` (AChE)
- [OK] Run `python prepare_receptor.py 4EY7`
- [OK] Verify `protein_structures/4EY7_prepared.pdbqt` exists
- [OK] Install OpenBabel: `conda install -c conda-forge openbabel`

### **Import Errors**

**Solutions:**
- [OK] Ensure `neocortex_realistico_gpu` folder is copied correctly
- [OK] Check Dockerfile COPY commands
- [OK] Verify all Python files are present

---

##  **API Reference**

### **Drug Trial Simulation** (Port 8000)

**POST `/simulate`**

Request:
```json
{
  "drug": "fluoxetine",
  "disease": "depression",
  "dose_mg": 20,
  "duration_hours": 168,
  "neurons": 100000,
  "sampling_interval_hours": 24
}
```

Response:
```json
{
  "timepoints": [
    {
      "hours": 0,
      "serotonin": 0.45,
      "dopamine": 0.52,
      "noradrenaline": 0.38,
      "acetylcholine": 0.51,
      "gaba": 0.58,
      "glutamate": 0.49,
      "arousal": 0.38,
      "valence": -0.25,
      "heart_rate": 0.45,
      "respiratory_rate": 0.42,
      "gut_feeling": 0.35
    },
    ...
  ]
}
```

---

### **Drug Discovery** (Port 8001)

**POST `/discover`**

Request:
```json
{
  "disease": {
    "name": "Alzheimers Disease",
    "profile": {
      "acetylcholine_deficit": 0.60,
      "serotonin_deficit": 0.15
    }
  },
  "config": {
    "iterations": 100,
    "populationSize": 50,
    "weights": {
      "ntCorrection": 0.50,
      "docking": 0.35,
      "sideEffects": 0.08,
      "complexity": 0.04,
      "speed": 0.03
    },
    "useDocking": true,
    "dockingExhaustiveness": 8,
    "trialDuration": 168
  },
  "neurons": 100000
}
```

Response:
```json
{
  "optimal_drug": {
    "name": "AI-Discovered-825",
    "class": "AI-Optimized Multi-Target",
    "molecularTargets": [
      {
        "target": "ache_inhibition",
        "potency": 0.87
      },
      {
        "target": "sert_inhibition",
        "potency": 0.31
      }
    ],
    "molecular_structure": {
      "smiles": "C1CCN(CC1)CCc2ccc(OC)c(OC)c2C(=O)Nc3ccccc3",
      "generation_method": "hybrid",
      "properties": {
        "molecular_weight": 368.5,
        "logp": 3.2,
        "qed_score": 0.72,
        "sa_score": 3.5,
        "is_drug_like": true,
        "is_synthesizable": true,
        "binding_affinity_kcal_mol": -9.2
      }
    },
    "optimization": {
      "fitness": 0.825,
      "generations": 100
    }
  },
  "fitness_history": [...],
  "final_fitness": 0.825
}
```

---

##  **Supported Diseases**

### **Mood Disorders:**
- Major Depressive Disorder
- Persistent Depressive Disorder (Dysthymia)
- Bipolar Disorder (Depressive Phase)

### **Anxiety Disorders:**
- Generalized Anxiety Disorder
- Panic Disorder
- Social Anxiety Disorder
- OCD
- PTSD

### **Psychotic Disorders:**
- Schizophrenia
- Schizoaffective Disorder

### **Neurodegenerative:**
- Alzheimer's Disease
- Mild Cognitive Impairment
- Parkinson's Disease

### **Neurodevelopmental:**
- ADHD

### **Neurological:**
- Epilepsy
- Chronic Insomnia
- Restless Legs Syndrome

---

##  **Supported Drugs**

### **Antidepressants:**
SSRIs, SNRIs, TCAs, MAOIs, Atypicals

### **Antipsychotics:**
Typical, Atypical (D2 antagonists, partial agonists)

### **Anxiolytics:**
Benzodiazepines, Buspirone, Pregabalin

### **Stimulants:**
Methylphenidate, Amphetamines

### **Cholinesterase Inhibitors:**
Donepezil, Rivastigmine, Galantamine

### **Anticonvulsants:**
Lamotrigine, Valproate, Topiramate

### **Custom Drugs:**
Any combination of 23 molecular mechanisms

---

##  **Notes**

- **Two Servers:** Port 8000 (trials), Port 8001 (discovery)
- **No Persistent State:** Each request creates new brain instance
- **GPU Memory:** Concurrent requests share GPU memory
- **Docking Optional:** Can be disabled for faster discovery
- **Auto-Selection:** Docking target chosen automatically from disease
- **SMILES Validation:** All molecules validated for drug-likeness
- **Reproducible:** Fixed random seeds for consistent results

---

##  **Scientific Background**

### **Biological Realism:**
- Leaky Integrate-and-Fire neurons
- Dale's principle (E/I separation)
- Cortical column architecture
- Realistic synaptic plasticity
- Neurotransmitter-specific dynamics

### **Emergent Properties:**
- Mood states emerge from NT balance
- Arousal from NE/5HT ratio
- Cognitive function from ACh levels
- Motor control from DA/ACh balance
- Sleep/wake from GABA/Glutamate

### **Drug Mechanisms:**
- Reuptake inhibition (SERT, DAT, NET)
- Enzyme inhibition (MAO-A, AChE)
- Receptor modulation (D2, 5-HT1A, GABA-A)
- Neurotransmitter precursors (L-DOPA)

---
