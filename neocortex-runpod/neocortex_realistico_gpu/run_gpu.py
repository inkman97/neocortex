#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              NEOCORTEX GPU - RUNNER PER RUNPOD                               ║
║                                                                              ║
║     Esegui con:                                                              ║
║       python run_gpu.py --neurons 1000000                                    ║
║                                                                              ║
║     Requisiti:                                                               ║
║       pip install torch numpy scipy                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import torch
import numpy as np
import time
import argparse
from typing import Dict, List, Tuple, Optional

# ============================================================
# CHECK GPU
# ============================================================

def check_gpu():
    """Verifica disponibilità GPU."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"[GPU] {gpu_name}")
        print(f"[GPU] Memoria: {gpu_mem:.1f} GB")
        return device
    else:
        print("[WARNING] GPU non disponibile, uso CPU")
        return torch.device("cpu")

DEVICE = check_gpu()

# ============================================================
# NEURONI LIF GPU
# ============================================================

class LIFNeuronsGPU:
    """Neuroni LIF su GPU con PyTorch."""
    
    def __init__(self, n: int, tau_m: float = 20.0, v_th: float = 1.0):
        self.n = n
        self.tau_m = tau_m
        self.v_th = v_th
        
        # Stato su GPU
        self.v = torch.zeros(n, device=DEVICE)
        self.spikes = torch.zeros(n, device=DEVICE)
        
        # Decay
        self.decay = torch.exp(torch.tensor(-1.0 / tau_m, device=DEVICE))
    
    def step(self, input_current: torch.Tensor) -> torch.Tensor:
        """Esegue un timestep."""
        # Decay e integra
        self.v = self.v * self.decay + input_current
        
        # Spike
        self.spikes = (self.v >= self.v_th).float()
        
        # Reset
        self.v = self.v * (1 - self.spikes)
        
        return self.spikes
    
    def reset(self):
        self.v.zero_()
        self.spikes.zero_()


# ============================================================
# SINAPSI SPARSE GPU
# ============================================================

class SparseSynapsesGPU:
    """Sinapsi sparse su GPU."""
    
    def __init__(
        self, 
        n_pre: int, 
        n_post: int, 
        prob: float = 0.01,
        weight: float = 0.1
    ):
        self.n_pre = n_pre
        self.n_post = n_post
        
        # Crea connettività sparsa
        print(f"    Creazione sinapsi {n_pre}x{n_post} (prob={prob})...")
        
        # Genera indici sparse
        n_synapses = int(n_pre * n_post * prob)
        
        # Indici casuali
        pre_idx = torch.randint(0, n_pre, (n_synapses,), device=DEVICE)
        post_idx = torch.randint(0, n_post, (n_synapses,), device=DEVICE)
        
        # Pesi
        values = torch.randn(n_synapses, device=DEVICE) * weight
        
        # Matrice sparsa COO -> CSR
        indices = torch.stack([pre_idx, post_idx])
        self.weights = torch.sparse_coo_tensor(
            indices, values, (n_pre, n_post), device=DEVICE
        ).coalesce()
        
        self.n_synapses = n_synapses
        print(f"    -> {n_synapses:,} sinapsi create")
    
    def propagate(self, spikes: torch.Tensor) -> torch.Tensor:
        """Propaga spike."""
        return torch.sparse.mm(self.weights.t(), spikes.unsqueeze(1)).squeeze()


# ============================================================
# NEUROMODULAZIONE GPU
# ============================================================

class NeuromodulationGPU:
    """Sistema neuromodulatorio su GPU."""
    
    def __init__(self):
        self.dopamine = torch.tensor(0.5, device=DEVICE)
        self.serotonin = torch.tensor(0.5, device=DEVICE)
        self.noradrenaline = torch.tensor(0.3, device=DEVICE)
        self.acetylcholine = torch.tensor(0.4, device=DEVICE)
        
        self.decay = 0.85
    
    def update(self, reward: float = 0.0, threat: float = 0.0, novelty: float = 0.0):
        """Aggiorna neuromodulatori."""
        # Decay verso baseline
        self.dopamine = self.dopamine * self.decay + 0.5 * (1 - self.decay)
        self.serotonin = self.serotonin * self.decay + 0.5 * (1 - self.decay)
        self.noradrenaline = self.noradrenaline * self.decay + 0.3 * (1 - self.decay)
        self.acetylcholine = self.acetylcholine * self.decay + 0.4 * (1 - self.decay)
        
        # Modulazione
        if reward > 0:
            self.dopamine = torch.clamp(self.dopamine + reward * 0.3, 0, 1)
        if threat > 0:
            self.noradrenaline = torch.clamp(self.noradrenaline + threat * 0.4, 0, 1)
            self.dopamine = torch.clamp(self.dopamine - threat * 0.2, 0, 1)
        if novelty > 0:
            self.acetylcholine = torch.clamp(self.acetylcholine + novelty * 0.2, 0, 1)
    
    def get_state(self) -> dict:
        return {
            'dopamine': self.dopamine.item(),
            'serotonin': self.serotonin.item(),
            'noradrenaline': self.noradrenaline.item(),
            'acetylcholine': self.acetylcholine.item(),
        }


# ============================================================
# EMBODIMENT GPU
# ============================================================

class EmbodimentGPU:
    """Sistema embodiment su GPU."""
    
    def __init__(self):
        self.heart_rate = torch.tensor(0.5, device=DEVICE)
        self.skin_conductance = torch.tensor(0.3, device=DEVICE)
        self.muscle_tension = torch.tensor(0.3, device=DEVICE)
        self.gut_feeling = torch.tensor(0.5, device=DEVICE)
        
        self.decay = 0.88
    
    def update(self, arousal: float = 0.0, valence: float = 0.0, threat: float = 0.0):
        """Aggiorna stato corporeo."""
        # Decay
        self.heart_rate = self.heart_rate * self.decay + 0.5 * (1 - self.decay)
        self.skin_conductance = self.skin_conductance * self.decay + 0.3 * (1 - self.decay)
        self.muscle_tension = self.muscle_tension * self.decay + 0.3 * (1 - self.decay)
        self.gut_feeling = self.gut_feeling * self.decay + 0.5 * (1 - self.decay)
        
        # Modulazione
        if threat > 0:
            self.heart_rate = torch.clamp(self.heart_rate + threat * 0.3, 0, 1)
            self.skin_conductance = torch.clamp(self.skin_conductance + threat * 0.4, 0, 1)
            self.muscle_tension = torch.clamp(self.muscle_tension + threat * 0.3, 0, 1)
            self.gut_feeling = torch.clamp(self.gut_feeling - threat * 0.3, 0, 1)
        
        if valence > 0:
            self.gut_feeling = torch.clamp(self.gut_feeling + valence * 0.2, 0, 1)
    
    def get_arousal(self) -> float:
        return ((self.heart_rate + self.skin_conductance + self.muscle_tension) / 3).item()
    
    def get_state(self) -> dict:
        return {
            'heart_rate': self.heart_rate.item(),
            'skin_conductance': self.skin_conductance.item(),
            'muscle_tension': self.muscle_tension.item(),
            'gut_feeling': self.gut_feeling.item(),
        }


# ============================================================
# AMIGDALA GPU
# ============================================================

class AmygdalaGPU:
    """Amigdala semplificata su GPU."""
    
    def __init__(self, pattern_size: int = 100):
        self.pattern_size = pattern_size
        self.fear_patterns: List[torch.Tensor] = []
        self.reward_patterns: List[torch.Tensor] = []
    
    def learn_fear(self, pattern: torch.Tensor):
        """Impara pattern di paura."""
        if len(pattern) != self.pattern_size:
            pattern = torch.nn.functional.interpolate(
                pattern.unsqueeze(0).unsqueeze(0), 
                size=self.pattern_size
            ).squeeze()
        self.fear_patterns.append(pattern.clone())
        if len(self.fear_patterns) > 50:
            self.fear_patterns.pop(0)
    
    def learn_reward(self, pattern: torch.Tensor):
        """Impara pattern di reward."""
        if len(pattern) != self.pattern_size:
            pattern = torch.nn.functional.interpolate(
                pattern.unsqueeze(0).unsqueeze(0),
                size=self.pattern_size
            ).squeeze()
        self.reward_patterns.append(pattern.clone())
        if len(self.reward_patterns) > 50:
            self.reward_patterns.pop(0)
    
    def evaluate(self, pattern: torch.Tensor) -> Tuple[float, float]:
        """Valuta pattern per paura/reward."""
        fear = 0.0
        reward = 0.0
        
        if len(pattern) != self.pattern_size:
            pattern = torch.nn.functional.interpolate(
                pattern.unsqueeze(0).unsqueeze(0),
                size=self.pattern_size
            ).squeeze()
        
        pattern_norm = pattern / (torch.norm(pattern) + 1e-6)
        
        for fp in self.fear_patterns:
            fp_norm = fp / (torch.norm(fp) + 1e-6)
            sim = torch.dot(pattern_norm, fp_norm).item()
            fear = max(fear, sim)
        
        for rp in self.reward_patterns:
            rp_norm = rp / (torch.norm(rp) + 1e-6)
            sim = torch.dot(pattern_norm, rp_norm).item()
            reward = max(reward, sim)
        
        return max(0, fear), max(0, reward)


# ============================================================
# BRAIN GPU
# ============================================================

class BrainGPU:
    """Cervello completo su GPU."""
    
    def __init__(self, n_neurons: int = 100000):
        print(f"\n{'='*60}")
        print(f"  NEOCORTEX GPU - {n_neurons:,} neuroni")
        print(f"{'='*60}\n")
        
        start = time.time()
        
        self.n_neurons = n_neurons
        
        # Distribuzione layer
        layer_dist = {
            'L4': 0.20,  # Input
            'L23': 0.30, # Processing
            'L5': 0.30,  # Output
            'L6': 0.20,  # Feedback
        }
        
        print("[1/4] Creazione neuroni...")
        self.layers = {}
        for name, frac in layer_dist.items():
            n = int(n_neurons * frac)
            self.layers[name] = LIFNeuronsGPU(n)
            print(f"    {name}: {n:,} neuroni")
        
        print("\n[2/4] Creazione sinapsi...")
        self.synapses = {}
        conn_prob = min(0.01, 10000 / n_neurons)  # Scala probabilità
        
        # Feedforward
        self.synapses['L4_L23'] = SparseSynapsesGPU(
            self.layers['L4'].n, self.layers['L23'].n, prob=conn_prob
        )
        self.synapses['L23_L5'] = SparseSynapsesGPU(
            self.layers['L23'].n, self.layers['L5'].n, prob=conn_prob
        )
        self.synapses['L5_L6'] = SparseSynapsesGPU(
            self.layers['L5'].n, self.layers['L6'].n, prob=conn_prob * 0.5
        )
        # Feedback
        self.synapses['L6_L4'] = SparseSynapsesGPU(
            self.layers['L6'].n, self.layers['L4'].n, prob=conn_prob * 0.3
        )
        
        print("\n[3/4] Sistemi modulatori...")
        self.neuromodulation = NeuromodulationGPU()
        self.embodiment = EmbodimentGPU()
        self.amygdala = AmygdalaGPU(pattern_size=100)
        
        print("[4/4] Inizializzazione completata")
        
        elapsed = time.time() - start
        total_synapses = sum(s.n_synapses for s in self.synapses.values())
        
        print(f"\n[OK] Creato in {elapsed:.2f}s")
        print(f"     Neuroni: {n_neurons:,}")
        print(f"     Sinapsi: {total_synapses:,}")
        print(f"     GPU Memory: {torch.cuda.memory_allocated()/1024**3:.2f} GB")
        
        self.timestep = 0
    
    def step(self, input_pattern: Optional[torch.Tensor] = None):
        """Esegue un timestep."""
        # Input a L4
        if input_pattern is not None:
            if len(input_pattern) != self.layers['L4'].n:
                input_pattern = torch.nn.functional.interpolate(
                    input_pattern.unsqueeze(0).unsqueeze(0),
                    size=self.layers['L4'].n
                ).squeeze()
            self.layers['L4'].step(input_pattern)
        else:
            self.layers['L4'].step(torch.zeros(self.layers['L4'].n, device=DEVICE))
        
        # Feedforward
        l4_out = self.layers['L4'].spikes
        l23_in = self.synapses['L4_L23'].propagate(l4_out)
        self.layers['L23'].step(l23_in)
        
        l23_out = self.layers['L23'].spikes
        l5_in = self.synapses['L23_L5'].propagate(l23_out)
        self.layers['L5'].step(l5_in)
        
        l5_out = self.layers['L5'].spikes
        l6_in = self.synapses['L5_L6'].propagate(l5_out)
        self.layers['L6'].step(l6_in)
        
        # Feedback
        l6_out = self.layers['L6'].spikes
        fb = self.synapses['L6_L4'].propagate(l6_out)
        # Feedback modula prossimo step
        
        self.timestep += 1
    
    def perceive(self, pattern: np.ndarray, threat: float = 0.0, reward: float = 0.0):
        """Percepisci input con contesto emotivo."""
        pattern_t = torch.tensor(pattern, dtype=torch.float32, device=DEVICE)
        
        # Valuta con amigdala
        fear, rew = self.amygdala.evaluate(pattern_t)
        
        # Aggiorna sistemi
        self.neuromodulation.update(reward=reward, threat=threat)
        self.embodiment.update(threat=threat, valence=reward - threat)
        
        # Apprendi
        if threat > 0.5:
            self.amygdala.learn_fear(pattern_t)
        if reward > 0.5:
            self.amygdala.learn_reward(pattern_t)
        
        # Step
        self.step(pattern_t)
        
        return fear, rew
    
    def get_state(self) -> dict:
        """Stato completo."""
        nm = self.neuromodulation.get_state()
        emb = self.embodiment.get_state()
        
        return {
            'timestep': self.timestep,
            'n_neurons': self.n_neurons,
            **nm,
            **emb,
            'arousal': self.embodiment.get_arousal(),
            'fear_memories': len(self.amygdala.fear_patterns),
            'reward_memories': len(self.amygdala.reward_patterns),
        }
    
    def benchmark(self, n_steps: int = 100) -> float:
        """Benchmark performance."""
        print(f"\n[Benchmark] {n_steps} step...")
        
        # Warmup
        for _ in range(10):
            self.step()
        
        torch.cuda.synchronize()
        start = time.time()
        
        for _ in range(n_steps):
            self.step()
        
        torch.cuda.synchronize()
        elapsed = time.time() - start
        
        ms_per_step = (elapsed / n_steps) * 1000
        print(f"[Benchmark] {ms_per_step:.2f} ms/step")
        print(f"[Benchmark] {n_steps/elapsed:.1f} step/sec")
        
        return ms_per_step


# ============================================================
# TEST EMOTIVO
# ============================================================

def test_emotivo(brain: BrainGPU):
    """Test emotivo completo."""
    print("\n" + "="*60)
    print("  TEST EMOTIVO")
    print("="*60)
    
    # Pattern
    pattern_neutro = np.ones(100) * 0.5
    pattern_minaccia = np.random.rand(100)
    pattern_piacere = np.random.rand(100)
    
    # FASE 1: Baseline
    print("\n[FASE 1] Stato iniziale")
    state = brain.get_state()
    print(f"  Dopamina: {state['dopamine']:.3f}")
    print(f"  Noradrenalina: {state['noradrenaline']:.3f}")
    print(f"  Battito: {state['heart_rate']:.3f}")
    print(f"  Arousal: {state['arousal']:.3f}")
    
    # FASE 2: Minaccia
    print("\n[FASE 2] Minaccia crescente")
    for i in range(10):
        threat = (i + 1) / 10
        brain.perceive(pattern_minaccia, threat=threat)
        if (i + 1) % 3 == 0:
            state = brain.get_state()
            print(f"  Threat={threat:.1f} -> HR={state['heart_rate']:.2f}, NE={state['noradrenaline']:.2f}")
    
    # FASE 3: Calma
    print("\n[FASE 3] Ritorno alla calma")
    for i in range(20):
        brain.perceive(pattern_neutro, threat=0, reward=0)
    state = brain.get_state()
    print(f"  Dopo calma: HR={state['heart_rate']:.2f}, NE={state['noradrenaline']:.2f}")
    
    # FASE 4: Piacere
    print("\n[FASE 4] Reward")
    for i in range(10):
        reward = (i + 1) / 10
        brain.perceive(pattern_piacere, reward=reward)
    state = brain.get_state()
    print(f"  Dopo reward: DA={state['dopamine']:.2f}, Gut={state['gut_feeling']:.2f}")
    
    # FASE 5: Memoria
    print("\n[FASE 5] Test memoria emotiva")
    fear, rew = brain.amygdala.evaluate(
        torch.tensor(pattern_minaccia, dtype=torch.float32, device=DEVICE)
    )
    print(f"  Pattern minaccia: fear={fear:.3f}")
    
    fear, rew = brain.amygdala.evaluate(
        torch.tensor(pattern_piacere, dtype=torch.float32, device=DEVICE)
    )
    print(f"  Pattern piacere:  reward={rew:.3f}")
    
    print("\n[OK] Test completato")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='NeoCortex GPU Runner')
    parser.add_argument('--neurons', '-n', type=int, default=100000,
                       help='Numero di neuroni (default: 100000)')
    parser.add_argument('--benchmark', '-b', action='store_true',
                       help='Esegui benchmark')
    parser.add_argument('--test', '-t', action='store_true',
                       help='Esegui test emotivo')
    parser.add_argument('--steps', '-s', type=int, default=100,
                       help='Step per benchmark')
    
    args = parser.parse_args()
    
    # Crea brain
    brain = BrainGPU(n_neurons=args.neurons)
    
    # Benchmark
    if args.benchmark:
        brain.benchmark(n_steps=args.steps)
    
    # Test
    if args.test or not args.benchmark:
        test_emotivo(brain)
    
    # Stato finale
    print("\n" + "="*60)
    print("  STATO FINALE")
    print("="*60)
    state = brain.get_state()
    for k, v in state.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.3f}")
        else:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
