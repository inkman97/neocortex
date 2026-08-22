"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    STRUTTURE SUBCORTICALI                                    ║
║                                                                              ║
║     TALAMO:                                                                  ║
║       - Gateway sensoriale                                                   ║
║       - Relay verso corteccia                                                ║
║       - Filtra informazioni                                                  ║
║                                                                              ║
║     GANGLI DELLA BASE:                                                       ║
║       - Selezione azioni (Go/NoGo)                                           ║
║       - Apprendimento per rinforzo                                           ║
║       - Movimenti volontari                                                  ║
║                                                                              ║
║     IPPOCAMPO:                                                               ║
║       - Memoria episodica                                                    ║
║       - Navigazione spaziale                                                 ║
║       - Consolidamento memoria                                               ║
║                                                                              ║
║     AMIGDALA:                                                                ║
║       - Elaborazione emozioni                                                ║
║       - Fear conditioning                                                    ║
║       - Valenza emotiva                                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from .neurons import NeuronType, NeuronGroup, create_neuron_group, BACKEND
if BACKEND == "torch":
    import torch
    from .neurons import DEVICE


# ============================================================
# TALAMO
# ============================================================

class Thalamus:
    """
    Talamo: relay station per input sensoriali.
    
    Funzioni:
    - Filtra input in base all'attenzione
    - Relay verso corteccia (principalmente L4)
    - Feedback dalla corteccia (L6)
    """
    
    def __init__(self, n_neurons: int = 100):
        self.n = n_neurons
        
        # Neuroni relay (eccitatori)
        self.relay = create_neuron_group(n_neurons, NeuronType.PYRAMIDAL, "Thalamus_Relay")
        
        # Neuroni reticolari (inibitori, gating)
        n_ret = max(10, n_neurons // 5)
        self.reticular = create_neuron_group(n_ret, NeuronType.PV, "Thalamus_Reticular")
        
        # Stato di gating (attenzione)
        if BACKEND == "torch":
            self.gate = torch.ones(n_neurons, device=DEVICE)
        else:
            self.gate = np.ones(n_neurons, dtype=np.float32)
    
    def receive_sensory(self, input_current):
        """Riceve input sensoriale."""
        if BACKEND == "torch":
            if isinstance(input_current, np.ndarray):
                input_current = torch.tensor(input_current, dtype=torch.float32, device=DEVICE)
            # Ridimensiona se necessario
            if len(input_current) != self.n:
                indices = torch.linspace(0, len(input_current)-1, self.n).long()
                input_current = input_current[indices]
        else:
            if len(input_current) != self.n:
                indices = np.linspace(0, len(input_current)-1, self.n).astype(int)
                input_current = input_current[indices]
        
        # Applica gating (attenzione)
        gated_input = input_current * self.gate
        self.relay.inject_current(gated_input, excitatory=True)
    
    def receive_cortical_feedback(self, feedback):
        """Riceve feedback da L6 corteccia."""
        # Feedback modula il gating
        if BACKEND == "torch":
            if isinstance(feedback, np.ndarray):
                feedback = torch.tensor(feedback, dtype=torch.float32, device=DEVICE)
            self.gate = 0.5 + feedback * 0.5
            self.gate = torch.clamp(self.gate, 0.1, 1.0)
        else:
            self.gate = 0.5 + feedback * 0.5
            self.gate = np.clip(self.gate, 0.1, 1.0)
    
    def step(self, dt: float = 1.0):
        """Simula un timestep."""
        # Relay neurons step
        self.relay.step(dt)
        
        # Reticular neurons (auto-inibizione)
        self.reticular.step(dt)
    
    def get_output(self):
        """Output verso corteccia (L4)."""
        if BACKEND == "torch":
            return self.relay.spike.clone()
        return self.relay.spike.copy()


# ============================================================
# GANGLI DELLA BASE
# ============================================================

class BasalGanglia:
    """
    Gangli della base: selezione delle azioni.
    
    Pathway:
    - Diretto (Go): facilita azione
    - Indiretto (NoGo): inibisce azione
    
    Dopamina modula:
    - D1 (Go): aumenta Go
    - D2 (NoGo): diminuisce NoGo
    """
    
    def __init__(self, n_actions: int = 10):
        self.n_actions = n_actions
        
        # Striato (input)
        self.d1_spn = create_neuron_group(n_actions, NeuronType.PYRAMIDAL, "D1_SPN")  # Go
        self.d2_spn = create_neuron_group(n_actions, NeuronType.PYRAMIDAL, "D2_SPN")  # NoGo
        
        # Output (SNr/GPi)
        self.output = create_neuron_group(n_actions, NeuronType.PV, "BG_Output")
        
        # Pesi (apprendimento per rinforzo)
        if BACKEND == "torch":
            self.w_go = torch.rand(n_actions, device=DEVICE) * 0.5
            self.w_nogo = torch.rand(n_actions, device=DEVICE) * 0.5
        else:
            self.w_go = np.random.rand(n_actions).astype(np.float32) * 0.5
            self.w_nogo = np.random.rand(n_actions).astype(np.float32) * 0.5
        
        # Dopamine level (modulazione)
        self.dopamine = 0.5
    
    def receive_cortical(self, cortical_input):
        """Riceve input dalla corteccia."""
        if BACKEND == "torch":
            if isinstance(cortical_input, np.ndarray):
                cortical_input = torch.tensor(cortical_input, dtype=torch.float32, device=DEVICE)
            if len(cortical_input) != self.n_actions:
                indices = torch.linspace(0, len(cortical_input)-1, self.n_actions).long()
                cortical_input = cortical_input[indices]
        else:
            if len(cortical_input) != self.n_actions:
                indices = np.linspace(0, len(cortical_input)-1, self.n_actions).astype(int)
                cortical_input = cortical_input[indices]
        
        # Go pathway (modulato da D1)
        d1_mod = 0.5 + self.dopamine  # Dopamina aumenta Go
        go_input = cortical_input * self.w_go * d1_mod
        self.d1_spn.inject_current(go_input, excitatory=True)
        
        # NoGo pathway (modulato da D2)
        d2_mod = 1.5 - self.dopamine  # Dopamina diminuisce NoGo
        nogo_input = cortical_input * self.w_nogo * d2_mod
        self.d2_spn.inject_current(nogo_input, excitatory=True)
    
    def set_dopamine(self, level: float):
        """Imposta livello di dopamina."""
        self.dopamine = np.clip(level, 0, 1)
    
    def step(self, dt: float = 1.0):
        """Simula un timestep."""
        self.d1_spn.step(dt)
        self.d2_spn.step(dt)
        
        # Calcola output (Go - NoGo)
        if BACKEND == "torch":
            go_activity = self.d1_spn.spike.float()
            nogo_activity = self.d2_spn.spike.float()
            net = go_activity - nogo_activity
            self.output.inject_current(net, excitatory=True)
        else:
            go_activity = self.d1_spn.spike.astype(np.float32)
            nogo_activity = self.d2_spn.spike.astype(np.float32)
            net = go_activity - nogo_activity
            self.output.inject_current(net, excitatory=True)
        
        self.output.step(dt)
    
    def learn(self, reward: float, chosen_action: int):
        """
        Apprendimento per rinforzo.
        
        Reward positivo: rafforza Go per azione scelta
        Reward negativo: rafforza NoGo per azione scelta
        """
        if BACKEND == "torch":
            if reward > 0:
                self.w_go[chosen_action] += reward * 0.1
                self.w_nogo[chosen_action] -= reward * 0.05
            else:
                self.w_go[chosen_action] += reward * 0.05
                self.w_nogo[chosen_action] -= reward * 0.1
            
            self.w_go = torch.clamp(self.w_go, 0.1, 2.0)
            self.w_nogo = torch.clamp(self.w_nogo, 0.1, 2.0)
        else:
            if reward > 0:
                self.w_go[chosen_action] += reward * 0.1
                self.w_nogo[chosen_action] -= reward * 0.05
            else:
                self.w_go[chosen_action] += reward * 0.05
                self.w_nogo[chosen_action] -= reward * 0.1
            
            self.w_go = np.clip(self.w_go, 0.1, 2.0)
            self.w_nogo = np.clip(self.w_nogo, 0.1, 2.0)
    
    def select_action(self) -> int:
        """Seleziona azione in base all'output."""
        if BACKEND == "torch":
            output = self.output.v.cpu().numpy()
        else:
            output = self.output.v
        return int(np.argmax(output))


# ============================================================
# IPPOCAMPO
# ============================================================

class Hippocampus:
    """
    Ippocampo: memoria episodica.
    
    Struttura:
    - DG (Dentate Gyrus): pattern separation
    - CA3: autoassociativa, pattern completion
    - CA1: output, confronto
    """
    
    def __init__(self, n_neurons: int = 200):
        self.n = n_neurons
        
        # Regioni
        n_dg = n_neurons // 2  # DG ha piu neuroni (sparse)
        n_ca3 = n_neurons // 4
        n_ca1 = n_neurons // 4
        
        self.dg = create_neuron_group(n_dg, NeuronType.PYRAMIDAL, "DG")
        self.ca3 = create_neuron_group(n_ca3, NeuronType.PYRAMIDAL, "CA3")
        self.ca1 = create_neuron_group(n_ca1, NeuronType.PYRAMIDAL, "CA1")
        
        # Memoria (pattern stored)
        self.stored_patterns: List[np.ndarray] = []
        self.pattern_contexts: List[dict] = []  # Contesto associato
        self.max_patterns = 200
        
        # Pesi CA3 (autoassociativa)
        if BACKEND == "torch":
            self.w_ca3 = torch.zeros(n_ca3, n_ca3, device=DEVICE)
        else:
            self.w_ca3 = np.zeros((n_ca3, n_ca3), dtype=np.float32)
    
    def encode(self, pattern, context: Optional[dict] = None):
        """
        Memorizza un pattern.
        
        Args:
            pattern: Pattern da memorizzare
            context: Informazioni contestuali (emozione, luogo, tempo)
        """
        if BACKEND == "torch":
            if isinstance(pattern, torch.Tensor):
                pattern = pattern.cpu().numpy()
        
        # Converti a dimensione corretta
        if len(pattern) != self.dg.n:
            indices = np.linspace(0, len(pattern)-1, self.dg.n).astype(int)
            pattern = np.array(pattern)[indices]
        
        pattern = pattern.astype(np.float32)
        
        # Limite memoria
        if len(self.stored_patterns) >= self.max_patterns:
            self.stored_patterns.pop(0)
            self.pattern_contexts.pop(0)
        
        self.stored_patterns.append(pattern.copy())
        self.pattern_contexts.append(context or {})
        
        # Aggiorna pesi CA3 (Hebbian)
        sparse = self._sparsify(pattern)
        if BACKEND == "torch":
            sparse_t = torch.tensor(sparse, device=DEVICE)
            self.w_ca3 += 0.1 * torch.outer(sparse_t, sparse_t)
            self.w_ca3 = torch.clamp(self.w_ca3, 0, 1)
        else:
            self.w_ca3 += 0.1 * np.outer(sparse, sparse)
            self.w_ca3 = np.clip(self.w_ca3, 0, 1)
    
    def _sparsify(self, pattern) -> np.ndarray:
        """DG: pattern separation (rende sparse)."""
        # Tiene solo i top 10% attivi
        threshold = np.percentile(pattern, 90)
        sparse = np.where(pattern > threshold, pattern, 0)
        
        # Ridimensiona a CA3
        if len(sparse) != self.ca3.n:
            indices = np.linspace(0, len(sparse)-1, self.ca3.n).astype(int)
            sparse = sparse[indices]
        
        return sparse.astype(np.float32)
    
    def recall(self, cue, threshold: float = 0.5) -> Tuple[Optional[np.ndarray], Optional[dict]]:
        """
        Richiama pattern simile al cue.
        
        Args:
            cue: Pattern parziale (cue)
            threshold: Soglia di similarita
        
        Returns:
            (pattern richiamato, contesto) o (None, None)
        """
        if len(self.stored_patterns) == 0:
            return None, None
        
        if BACKEND == "torch":
            if isinstance(cue, torch.Tensor):
                cue = cue.cpu().numpy()
        
        # Normalizza cue
        if len(cue) != self.dg.n:
            indices = np.linspace(0, len(cue)-1, self.dg.n).astype(int)
            cue = np.array(cue)[indices]
        
        cue = cue.astype(np.float32)
        cue_norm = cue / (np.linalg.norm(cue) + 1e-8)
        
        # Cerca pattern piu simile
        best_idx = -1
        best_sim = 0.0
        
        for i, pattern in enumerate(self.stored_patterns):
            pattern_norm = pattern / (np.linalg.norm(pattern) + 1e-8)
            sim = np.dot(cue_norm, pattern_norm)
            
            if sim > best_sim:
                best_sim = sim
                best_idx = i
        
        if best_sim >= threshold and best_idx >= 0:
            return self.stored_patterns[best_idx], self.pattern_contexts[best_idx]
        
        return None, None
    
    def step(self, dt: float = 1.0):
        """Simula un timestep."""
        self.dg.step(dt)
        
        # CA3 recurrent
        if BACKEND == "torch":
            ca3_input = torch.matmul(self.ca3.spike.float(), self.w_ca3)
            self.ca3.inject_current(ca3_input, excitatory=True)
        else:
            ca3_input = np.dot(self.ca3.spike.astype(np.float32), self.w_ca3)
            self.ca3.inject_current(ca3_input, excitatory=True)
        
        self.ca3.step(dt)
        self.ca1.step(dt)
    
    def clear(self):
        """Cancella memoria."""
        self.stored_patterns = []
        self.pattern_contexts = []


# ============================================================
# AMIGDALA
# ============================================================

class Amygdala:
    """
    Amigdala: elaborazione emotiva.
    
    Funzioni:
    - Valutazione rapida threat/reward
    - Fear conditioning
    - Modulazione memoria emotiva
    """
    
    def __init__(self, n_neurons: int = 50):
        self.n = n_neurons
        
        # Nuclei
        n_lateral = n_neurons // 2  # Input
        n_central = n_neurons // 2  # Output
        
        self.lateral = create_neuron_group(n_lateral, NeuronType.PYRAMIDAL, "Amygdala_Lateral")
        self.central = create_neuron_group(n_central, NeuronType.PYRAMIDAL, "Amygdala_Central")
        
        # Associazioni stimolo-emozione
        self.fear_associations: List[Tuple[np.ndarray, float]] = []
        self.reward_associations: List[Tuple[np.ndarray, float]] = []
        
        # Output emotivo
        self.fear_level = 0.0
        self.reward_level = 0.0
    
    def evaluate(self, stimulus) -> Tuple[float, float]:
        """
        Valuta stimolo per contenuto emotivo.
        
        Returns:
            (fear_level, reward_level)
        """
        if BACKEND == "torch":
            if isinstance(stimulus, torch.Tensor):
                stimulus = stimulus.cpu().numpy()
        
        stimulus = np.array(stimulus, dtype=np.float32)
        stim_norm = stimulus / (np.linalg.norm(stimulus) + 1e-8)
        
        # Valuta fear
        self.fear_level = 0.0
        for pattern, strength in self.fear_associations:
            min_len = min(len(pattern), len(stim_norm))
            pattern_adj = pattern[:min_len]
            stim_adj = stim_norm[:min_len]
            pattern_norm = pattern_adj / (np.linalg.norm(pattern_adj) + 1e-8)
            sim = max(0, np.dot(stim_adj, pattern_norm))
            self.fear_level += sim * strength
        
        # Valuta reward
        self.reward_level = 0.0
        for pattern, strength in self.reward_associations:
            min_len = min(len(pattern), len(stim_norm))
            pattern_adj = pattern[:min_len]
            stim_adj = stim_norm[:min_len]
            pattern_norm = pattern_adj / (np.linalg.norm(pattern_adj) + 1e-8)
            sim = max(0, np.dot(stim_adj, pattern_norm))
            self.reward_level += sim * strength
        
        # Normalizza
        self.fear_level = min(1.0, self.fear_level)
        self.reward_level = min(1.0, self.reward_level)
        
        return self.fear_level, self.reward_level
    
    def learn_fear(self, stimulus, strength: float = 1.0):
        """Associa stimolo a paura."""
        if BACKEND == "torch":
            if isinstance(stimulus, torch.Tensor):
                stimulus = stimulus.cpu().numpy()
        
        stimulus = np.array(stimulus, dtype=np.float32)
        self.fear_associations.append((stimulus.copy(), strength))
        
        if len(self.fear_associations) > 100:
            self.fear_associations.pop(0)
    
    def learn_reward(self, stimulus, strength: float = 1.0):
        """Associa stimolo a reward."""
        if BACKEND == "torch":
            if isinstance(stimulus, torch.Tensor):
                stimulus = stimulus.cpu().numpy()
        
        stimulus = np.array(stimulus, dtype=np.float32)
        self.reward_associations.append((stimulus.copy(), strength))
        
        if len(self.reward_associations) > 100:
            self.reward_associations.pop(0)
    
    def step(self, dt: float = 1.0):
        """Simula un timestep."""
        # Inietta corrente basata su fear/reward
        if BACKEND == "torch":
            fear_current = torch.full((self.lateral.n,), self.fear_level, device=DEVICE)
            reward_current = torch.full((self.central.n,), self.reward_level, device=DEVICE)
        else:
            fear_current = np.full(self.lateral.n, self.fear_level, dtype=np.float32)
            reward_current = np.full(self.central.n, self.reward_level, dtype=np.float32)
        
        self.lateral.inject_current(fear_current, excitatory=True)
        self.central.inject_current(reward_current, excitatory=True)
        
        self.lateral.step(dt)
        self.central.step(dt)
    
    def get_arousal(self) -> float:
        """Livello di arousal emotivo."""
        return max(self.fear_level, self.reward_level)
    
    def get_valence(self) -> float:
        """Valenza emotiva (-1 negativa, +1 positiva)."""
        return self.reward_level - self.fear_level
