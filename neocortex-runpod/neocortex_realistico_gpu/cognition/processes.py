"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    COGNIZIONE - PROCESSI COGNITIVI                           ║
║                                                                              ║
║     PREDICTIVE CODING:                                                       ║
║       - Il cervello predice costantemente                                    ║
║       - Impara dagli errori di predizione                                    ║
║       - Minimizza "free energy"                                              ║
║                                                                              ║
║     GLOBAL WORKSPACE:                                                        ║
║       - Competizione per accesso alla coscienza                              ║
║       - Broadcasting dell'informazione                                       ║
║       - Integrazione multimodale                                             ║
║                                                                              ║
║     ATTENZIONE:                                                              ║
║       - Top-down (volontaria)                                                ║
║       - Bottom-up (salienza)                                                 ║
║       - Modula processing                                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.neurons import BACKEND
if BACKEND == "torch":
    import torch
    from core.neurons import DEVICE


# ============================================================
# PREDICTIVE CODING
# ============================================================

class PredictiveCodingLayer:
    """
    Layer di predictive coding.
    
    Ogni layer:
    - Riceve predizioni dal layer superiore
    - Calcola errore di predizione
    - Invia errore verso l'alto
    - Aggiorna modello interno
    """
    
    def __init__(self, size: int, name: str = ""):
        self.size = size
        self.name = name
        
        if BACKEND == "torch":
            self.prediction = torch.zeros(size, device=DEVICE)
            self.error = torch.zeros(size, device=DEVICE)
            self.representation = torch.zeros(size, device=DEVICE)
            self.precision = torch.ones(size, device=DEVICE)  # Certezza
        else:
            self.prediction = np.zeros(size, dtype=np.float32)
            self.error = np.zeros(size, dtype=np.float32)
            self.representation = np.zeros(size, dtype=np.float32)
            self.precision = np.ones(size, dtype=np.float32)
    
    def compute_error(self, input_signal):
        """Calcola errore di predizione."""
        if BACKEND == "torch":
            if isinstance(input_signal, np.ndarray):
                input_signal = torch.tensor(input_signal, device=DEVICE, dtype=torch.float32)
            self.error = (input_signal - self.prediction) * self.precision
        else:
            self.error = (input_signal - self.prediction) * self.precision
        return self.error
    
    def update_prediction(self, top_down_signal, learning_rate: float = 0.1):
        """Aggiorna predizione."""
        if BACKEND == "torch":
            if isinstance(top_down_signal, np.ndarray):
                top_down_signal = torch.tensor(top_down_signal, device=DEVICE, dtype=torch.float32)
            self.prediction = self.prediction + learning_rate * (top_down_signal - self.prediction)
        else:
            self.prediction = self.prediction + learning_rate * (top_down_signal - self.prediction)
    
    def get_surprise(self) -> float:
        """Quantifica sorpresa (errore totale)."""
        if BACKEND == "torch":
            return torch.abs(self.error).mean().item()
        else:
            return np.abs(self.error).mean()


class PredictiveCodingHierarchy:
    """
    Gerarchia di predictive coding.
    
    Implementa il framework di Karl Friston:
    - Free Energy Principle
    - Active Inference
    """
    
    def __init__(self, layer_sizes: List[int]):
        self.layers = [
            PredictiveCodingLayer(size, f"Layer_{i}")
            for i, size in enumerate(layer_sizes)
        ]
        
        # Connessioni tra layer
        self.n_layers = len(layer_sizes)
        
        # Pesi feedforward (bottom-up)
        self.w_up = []
        for i in range(self.n_layers - 1):
            if BACKEND == "torch":
                w = torch.randn(layer_sizes[i], layer_sizes[i+1], device=DEVICE) * 0.1
            else:
                w = np.random.randn(layer_sizes[i], layer_sizes[i+1]).astype(np.float32) * 0.1
            self.w_up.append(w)
        
        # Pesi feedback (top-down)
        self.w_down = []
        for i in range(self.n_layers - 1):
            if BACKEND == "torch":
                w = torch.randn(layer_sizes[i+1], layer_sizes[i], device=DEVICE) * 0.1
            else:
                w = np.random.randn(layer_sizes[i+1], layer_sizes[i]).astype(np.float32) * 0.1
            self.w_down.append(w)
    
    def process(self, sensory_input, n_iterations: int = 5):
        """
        Processa input attraverso la gerarchia.
        
        Args:
            sensory_input: Input sensoriale
            n_iterations: Iterazioni di settling
        """
        if BACKEND == "torch":
            if isinstance(sensory_input, np.ndarray):
                sensory_input = torch.tensor(sensory_input, device=DEVICE, dtype=torch.float32)
        
        for _ in range(n_iterations):
            # Bottom-up: propaga errori
            current = sensory_input
            for i in range(self.n_layers - 1):
                error = self.layers[i].compute_error(current)
                if BACKEND == "torch":
                    current = torch.matmul(error, self.w_up[i])
                else:
                    current = np.dot(error, self.w_up[i])
                self.layers[i+1].representation = current
            
            # Top-down: propaga predizioni
            for i in range(self.n_layers - 2, -1, -1):
                top_down = self.layers[i+1].representation
                if BACKEND == "torch":
                    prediction = torch.matmul(top_down, self.w_down[i])
                else:
                    prediction = np.dot(top_down, self.w_down[i])
                self.layers[i].update_prediction(prediction)
    
    def learn(self, learning_rate: float = 0.01):
        """Aggiorna pesi per minimizzare errore."""
        for i in range(self.n_layers - 1):
            error_below = self.layers[i].error
            repr_above = self.layers[i+1].representation
            
            if BACKEND == "torch":
                dw = torch.outer(error_below, repr_above) * learning_rate
                self.w_up[i] = self.w_up[i] + dw
                self.w_down[i] = self.w_down[i] + dw.T
            else:
                dw = np.outer(error_below, repr_above) * learning_rate
                self.w_up[i] = self.w_up[i] + dw
                self.w_down[i] = self.w_down[i] + dw.T
    
    def get_total_surprise(self) -> float:
        """Sorpresa totale (free energy proxy)."""
        return sum(layer.get_surprise() for layer in self.layers)


# ============================================================
# GLOBAL WORKSPACE
# ============================================================

@dataclass
class WorkspaceContent:
    """Contenuto del workspace globale."""
    source: str
    data: np.ndarray
    strength: float
    timestamp: int


class GlobalWorkspace:
    """
    Global Workspace Theory (Baars).
    
    L'informazione che "vince" la competizione
    viene broadcast a tutto il cervello.
    Questo e un correlato della coscienza.
    """
    
    def __init__(self, size: int = 100):
        self.size = size
        
        # Contenuto corrente
        if BACKEND == "torch":
            self.content = torch.zeros(size, device=DEVICE)
        else:
            self.content = np.zeros(size, dtype=np.float32)
        
        self.current_source = None
        self.activation = 0.0
        self.threshold = 0.5
        
        # Storico
        self.history: List[WorkspaceContent] = []
        self.time = 0
        
        # Moduli che competono per accesso
        self.competitors: Dict[str, np.ndarray] = {}
    
    def submit(self, source: str, data, strength: float):
        """
        Un modulo sottomette contenuto per accesso al workspace.
        
        Args:
            source: Nome del modulo sorgente
            data: Contenuto da broadcast
            strength: Forza della richiesta
        """
        if BACKEND == "torch":
            if isinstance(data, torch.Tensor):
                data = data.cpu().numpy()
        
        data = np.array(data, dtype=np.float32)
        
        # Ridimensiona se necessario
        if len(data) > self.size:
            data = data[:self.size]
        elif len(data) < self.size:
            padded = np.zeros(self.size, dtype=np.float32)
            padded[:len(data)] = data
            data = padded
        
        self.competitors[source] = data * strength
    
    def compete(self) -> Optional[str]:
        """
        Competizione per accesso al workspace.
        
        Returns:
            Nome del vincitore (o None)
        """
        if not self.competitors:
            return None
        
        self.time += 1
        
        # Trova il piu forte
        winner = None
        max_strength = 0.0
        
        for source, data in self.competitors.items():
            strength = np.linalg.norm(data)
            if strength > max_strength:
                max_strength = strength
                winner = source
        
        # Soglia per accesso
        if max_strength > self.threshold and winner:
            self.content = self.competitors[winner].copy()
            if BACKEND == "torch":
                self.content = torch.tensor(self.content, device=DEVICE, dtype=torch.float32)
            
            self.current_source = winner
            self.activation = max_strength
            
            # Salva in storico
            self.history.append(WorkspaceContent(
                source=winner,
                data=self.competitors[winner].copy(),
                strength=max_strength,
                timestamp=self.time
            ))
            if len(self.history) > 100:
                self.history.pop(0)
            
            # Pulisci competitors
            self.competitors.clear()
            
            return winner
        
        self.competitors.clear()
        return None
    
    def broadcast(self) -> Tuple[Optional[str], np.ndarray, float]:
        """
        Ottieni contenuto corrente per broadcasting.
        
        Returns:
            (source, content, activation)
        """
        if BACKEND == "torch":
            content = self.content.cpu().numpy()
        else:
            content = self.content.copy()
        
        return self.current_source, content, self.activation
    
    def is_conscious(self) -> bool:
        """Il workspace ha contenuto attivo?"""
        return self.activation > self.threshold
    
    def decay(self, rate: float = 0.1):
        """Decay dell'attivazione."""
        self.activation *= (1 - rate)
        if self.activation < 0.1:
            self.activation = 0.0
            self.current_source = None


# ============================================================
# ATTENZIONE
# ============================================================

class AttentionSystem:
    """
    Sistema attentivo.
    
    Combina:
    - Attenzione bottom-up (salienza)
    - Attenzione top-down (goal-directed)
    """
    
    def __init__(self, size: int = 100):
        self.size = size
        
        if BACKEND == "torch":
            self.salience_map = torch.zeros(size, device=DEVICE)
            self.goal_map = torch.zeros(size, device=DEVICE)
            self.attention_map = torch.zeros(size, device=DEVICE)
        else:
            self.salience_map = np.zeros(size, dtype=np.float32)
            self.goal_map = np.zeros(size, dtype=np.float32)
            self.attention_map = np.zeros(size, dtype=np.float32)
        
        # Pesi relativi
        self.bottom_up_weight = 0.4
        self.top_down_weight = 0.6
    
    def compute_salience(self, input_signal):
        """Calcola salienza bottom-up."""
        if BACKEND == "torch":
            if isinstance(input_signal, np.ndarray):
                input_signal = torch.tensor(input_signal, device=DEVICE, dtype=torch.float32)
            
            if len(input_signal) != self.size:
                indices = torch.linspace(0, len(input_signal)-1, self.size).long()
                input_signal = input_signal[indices]
            
            # Salienza = deviazione dalla media
            mean = input_signal.mean()
            self.salience_map = torch.abs(input_signal - mean)
            self.salience_map = self.salience_map / (self.salience_map.max() + 1e-8)
        else:
            if len(input_signal) != self.size:
                indices = np.linspace(0, len(input_signal)-1, self.size).astype(int)
                input_signal = input_signal[indices]
            
            mean = input_signal.mean()
            self.salience_map = np.abs(input_signal - mean)
            self.salience_map = self.salience_map / (self.salience_map.max() + 1e-8)
    
    def set_goal(self, goal_pattern):
        """Imposta goal per attenzione top-down."""
        if BACKEND == "torch":
            if isinstance(goal_pattern, np.ndarray):
                goal_pattern = torch.tensor(goal_pattern, device=DEVICE, dtype=torch.float32)
            
            if len(goal_pattern) != self.size:
                indices = torch.linspace(0, len(goal_pattern)-1, self.size).long()
                goal_pattern = goal_pattern[indices]
            
            self.goal_map = goal_pattern / (goal_pattern.max() + 1e-8)
        else:
            if len(goal_pattern) != self.size:
                indices = np.linspace(0, len(goal_pattern)-1, self.size).astype(int)
                goal_pattern = goal_pattern[indices]
            
            self.goal_map = goal_pattern / (goal_pattern.max() + 1e-8)
    
    def compute_attention(self):
        """Calcola mappa attentiva combinata."""
        if BACKEND == "torch":
            self.attention_map = (
                self.bottom_up_weight * self.salience_map +
                self.top_down_weight * self.goal_map
            )
            self.attention_map = self.attention_map / (self.attention_map.max() + 1e-8)
        else:
            self.attention_map = (
                self.bottom_up_weight * self.salience_map +
                self.top_down_weight * self.goal_map
            )
            self.attention_map = self.attention_map / (self.attention_map.max() + 1e-8)
    
    def apply_attention(self, signal):
        """Applica attenzione a un segnale."""
        if BACKEND == "torch":
            if isinstance(signal, np.ndarray):
                signal = torch.tensor(signal, device=DEVICE, dtype=torch.float32)
            
            if len(signal) != self.size:
                indices = torch.linspace(0, len(signal)-1, self.size).long()
                signal = signal[indices]
            
            return signal * (0.5 + self.attention_map)
        else:
            if len(signal) != self.size:
                indices = np.linspace(0, len(signal)-1, self.size).astype(int)
                signal = signal[indices]
            
            return signal * (0.5 + self.attention_map)
    
    def get_focus(self) -> int:
        """Indice del focus attentivo."""
        if BACKEND == "torch":
            return self.attention_map.argmax().item()
        else:
            return int(np.argmax(self.attention_map))
