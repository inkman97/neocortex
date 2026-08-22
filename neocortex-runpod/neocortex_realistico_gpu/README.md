# NeoCortex GPU - RunPod / Colab

##  Due Modalità

### 1. Standalone Ottimizzato (MILIONI di neuroni)
```bash
python run_gpu.py --neurons 1000000 --test
```
- Usa PyTorch + CUDA
- Sinapsi sparse su GPU
- Fino a 10M+ neuroni

### 2. Modulare Compatibile (struttura completa)
```bash
python test_emozioni_automatico.py
```
- Stessa struttura di CPU
- Per testing e sviluppo
- ~100k neuroni max

## Quick Start su RunPod

### 1. Crea Pod
- Vai su **runpod.io** → GPU Cloud
- Scegli: **RTX 3090** ($0.44/hr) o **A100** ($1.99/hr)
- Template: **PyTorch 2.x**

### 2. Connetti al Pod
```bash
# Via web terminal o SSH
```

### 3. Upload File
```bash
# Opzione 1: wget da URL
wget https://your-url/run_gpu.py

# Opzione 2: copia-incolla nel terminale
cat > run_gpu.py << 'EOF'
# ... incolla codice ...
EOF
```

### 4. Esegui

```bash
# Test emotivo con 100k neuroni
python run_gpu.py --neurons 100000 --test

# 1 milione di neuroni
python run_gpu.py --neurons 1000000 --test

# Benchmark performance
python run_gpu.py --neurons 1000000 --benchmark --steps 1000

# 5 milioni (richiede A100 40GB)
python run_gpu.py --neurons 5000000 --benchmark
```

## Performance Attese

| GPU | Neuroni | ms/step | Sinapsi |
|-----|---------|---------|---------|
| RTX 3090 (24GB) | 100k | ~0.5 | ~10M |
| RTX 3090 (24GB) | 500k | ~2 | ~25M |
| RTX 3090 (24GB) | 1M | ~5 | ~100M |
| A100 (40GB) | 1M | ~2 | ~100M |
| A100 (40GB) | 5M | ~10 | ~500M |
| A100 (80GB) | 10M | ~20 | ~1B |

## Confronto con CPU

| Sistema | 1M neuroni |
|---------|------------|
| CPU (i9) | ~500 ms/step |
| RTX 3090 | ~5 ms/step |
| A100 | ~2 ms/step |
| **Speedup** | **100-250x** |

## Memoria GPU Richiesta

- 100k neuroni: ~2 GB
- 500k neuroni: ~6 GB
- 1M neuroni: ~12 GB
- 5M neuroni: ~40 GB
- 10M neuroni: ~80 GB

## Troubleshooting

### Out of Memory
```bash
# Riduci neuroni
python run_gpu.py --neurons 500000

# Oppure usa A100 più grande
```

### CUDA not available
```bash
# Verifica
python -c "import torch; print(torch.cuda.is_available())"

# Se False, reinstalla PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```
