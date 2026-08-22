"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    NEOCORTEX-Omega REALISTICO                                ║
║                                                                              ║
║     Cervello biologicamente realistico con:                                  ║
║                                                                              ║
║     CORTECCIA:                                                               ║
║       - 6 layer corticali                                                    ║
║       - 5 tipi di neuroni (Pyramidal, Stellate, PV, SST, VIP)               ║
║       - Connessioni canoniche                                                ║
║       - STDP + Three-factor learning                                         ║
║                                                                              ║
║     STRUTTURE SUBCORTICALI:                                                  ║
║       - Talamo (gateway sensoriale)                                          ║
║       - Gangli della base (selezione azioni)                                 ║
║       - Ippocampo (memoria episodica)                                        ║
║       - Amigdala (emozioni)                                                  ║
║                                                                              ║
║     NEUROMODULAZIONE:                                                        ║
║       - Dopamina, Serotonina, Noradrenalina, Acetilcolina                   ║
║                                                                              ║
║     EMBODIMENT:                                                              ║
║       - Interocezione                                                        ║
║       - Marcatori somatici                                                   ║
║                                                                              ║
║     COGNIZIONE:                                                              ║
║       - Predictive coding                                                    ║
║       - Global workspace                                                     ║
║       - Attenzione                                                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from core import (
    NeuronType,
    BACKEND,
    CorticalColumn,
    create_cortical_column,
    Thalamus,
    BasalGanglia,
    Hippocampus,
    Amygdala,
    Neuromodulator
)

from embodiment import Embodiment
from cognition import (
    PredictiveCodingHierarchy,
    GlobalWorkspace,
    AttentionSystem
)

if BACKEND == "torch":
    import torch
    from core.neurons import DEVICE


# ============================================================
# BRAIN STATE
# ============================================================

@dataclass
class BrainState:
    """Stato completo del cervello."""
    time: int = 0
    arousal: float = 0.5
    valence: float = 0.0
    attention_focus: int = 0
    is_conscious: bool = False
    current_action: int = -1
    surprise: float = 0.0


# ============================================================
# NEOCORTEX-Omega REALISTICO
# ============================================================

class RealisticBrain:
    """
    Cervello biologicamente realistico.
    
    Architettura completa che replica la struttura
    e le connessioni del cervello umano.
    """
    
    def __init__(
        self,
        n_neurons: int = 5000,
        n_columns: int = 4,
        debug: bool = False
    ):
        import sys
        self.debug = debug
        self.state = BrainState()
        
        print(f"[BRAIN __init__] Starting with {n_neurons} neurons, {n_columns} columns")
        sys.stdout.flush()
        
        if debug:
            print("=" * 60)
            print("   NEOCORTEX-Omega REALISTICO")
            print("=" * 60)
            print(f"\n[INIT] Backend: {BACKEND}")
        
        # ========================================
        # CORTECCIA
        # ========================================
        neurons_per_column = n_neurons // n_columns
        
        print(f"[BRAIN __init__] Creating cortex: {neurons_per_column} neurons/column")
        sys.stdout.flush()
        
        if debug:
            print(f"\n[CORTEX] Creazione {n_columns} colonne corticali...")
        
        self.columns: List[CorticalColumn] = []
        for i in range(n_columns):
            print(f"[BRAIN __init__] Creating column {i+1}/{n_columns}...")
            sys.stdout.flush()
            
            col = create_cortical_column(
                n_neurons=neurons_per_column,
                name=f"Column_{i}",
                debug=False
            )
            self.columns.append(col)
            
            print(f"[BRAIN __init__] Column {i+1}/{n_columns} created [OK]")
            sys.stdout.flush()
        
        print(f"[BRAIN __init__] Cortex complete, creating subcortical...")
        sys.stdout.flush()
        
        # ========================================
        # STRUTTURE SUBCORTICALI
        # ========================================
        if debug:
            print("[SUBCORTICAL] Creazione strutture subcorticali...")
        
        # Talamo
        self.thalamus = Thalamus(n_neurons=neurons_per_column // 10)
        
        # Gangli della base
        self.basal_ganglia = BasalGanglia(n_actions=10)
        
        # Ippocampo
        self.hippocampus = Hippocampus(n_neurons=neurons_per_column // 5)
        
        # Amigdala
        self.amygdala = Amygdala(n_neurons=neurons_per_column // 10)
        
        # ========================================
        # COGNIZIONE
        # ========================================
        if debug:
            print("[COGNITION] Inizializzazione processi cognitivi...")
        
        # Predictive coding
        pc_sizes = [100, 50, 25]
        self.predictive_coding = PredictiveCodingHierarchy(pc_sizes)
        
        # Global workspace
        self.global_workspace = GlobalWorkspace(size=100)
        
        # Attenzione
        self.attention = AttentionSystem(size=100)
        
        # ========================================
        # CONTA NEURONI (PRIMA della neuromodulazione!)
        # ========================================
        self.total_neurons = sum(col.total_neurons for col in self.columns)
        self.total_neurons += self.thalamus.n
        self.total_neurons += self.basal_ganglia.n_actions * 3
        self.total_neurons += self.hippocampus.n
        self.total_neurons += self.amygdala.n
        
        # ========================================
        # NEUROMODULAZIONE BIOLOGICA (dopo total_neurons!)
        # ========================================
        if debug:
            print("[NEUROMOD] Inizializzazione sistema neuromodulatorio biologico...")
        
        from emergent_neuromodulation import BiologicalNeuromodulation
        self.neuromodulation = BiologicalNeuromodulation(self, debug=debug)

        # ========================================
        # EMBODIMENT
        # ========================================
        if debug:
            print("[EMBODIMENT] Inizializzazione sistema corporeo...")

        # Extract disease state from neuromodulation efficacy
        # (efficacy 1.0 = healthy, efficacy 0.6 = deficit -0.4)
        disease_state = {
            'serotonin': 1.0 - self.neuromodulation.serotonin_efficacy,
            'dopamine': 1.0 - self.neuromodulation.dopamine_efficacy,
            'noradrenaline': 1.0 - self.neuromodulation.noradrenaline_efficacy,
            'acetylcholine': 1.0 - self.neuromodulation.acetylcholine_efficacy
        }

        if debug:
            print(f"[EMBODIMENT] Disease state extracted:")
            print(f"  5HT deficit: {disease_state['serotonin']:+.2f}")
            print(f"  DA deficit: {disease_state['dopamine']:+.2f}")
            print(f"  NE deficit: {disease_state['noradrenaline']:+.2f}")
            print(f"  ACh deficit: {disease_state['acetylcholine']:+.2f}")

        self.embodiment = Embodiment(disease_state=disease_state)
        
        if debug:
            print(f"\n[OK] Cervello creato!")
            print(f"     Neuroni totali: {self.total_neurons}")
            print(f"     Colonne corticali: {n_columns}")
            print(f"     Tipi di neuroni: Pyramidal, Stellate, PV, SST, VIP")
            print("=" * 60)
    
    def perceive(self, sensory_input: np.ndarray) -> Dict:
        """
        Percepisci input sensoriale.
        
        Flusso:
        1. Input -> Talamo (filtro)
        2. Talamo -> Corteccia L4
        3. Processing corticale
        4. Amigdala valuta emozione
        5. Aggiorna attenzione
        
        Args:
            sensory_input: Input sensoriale
        
        Returns:
            Dict con informazioni sulla percezione
        """
        self.state.time += 1
        
        # Converti input
        if BACKEND == "torch":
            if isinstance(sensory_input, np.ndarray):
                input_tensor = torch.tensor(sensory_input, dtype=torch.float32, device=DEVICE)
            else:
                input_tensor = sensory_input
            sensory_np = sensory_input if isinstance(sensory_input, np.ndarray) else sensory_input.cpu().numpy()
        else:
            input_tensor = np.array(sensory_input, dtype=np.float32)
            sensory_np = input_tensor
        
        # 1. TALAMO
        self.thalamus.receive_sensory(input_tensor)
        self.thalamus.step()
        thalamic_output = self.thalamus.get_output()
        
        # 2. CORTECCIA
        for col in self.columns:
            col.receive_input(thalamic_output)
            col.step()
        
        # 3. AMIGDALA (valutazione emotiva rapida)
        fear, reward = self.amygdala.evaluate(sensory_np[:50] if len(sensory_np) > 50 else sensory_np)
        self.amygdala.step()
        
        # 4. PREDICTIVE CODING
        self.predictive_coding.process(sensory_np[:100] if len(sensory_np) > 100 else sensory_np)
        self.state.surprise = self.predictive_coding.get_total_surprise()
        
        # 5. ATTENZIONE
        self.attention.compute_salience(sensory_np[:100] if len(sensory_np) > 100 else sensory_np)
        self.attention.compute_attention()
        
        # 6. GLOBAL WORKSPACE
        # Sottometti contenuti per competizione
        cortical_output = self.columns[0].get_l23_activity() if self.columns else np.array([])
        self.global_workspace.submit("cortex", cortical_output, np.linalg.norm(cortical_output))
        self.global_workspace.submit("emotion", np.array([fear, reward]), max(fear, reward))
        
        winner = self.global_workspace.compete()
        self.state.is_conscious = self.global_workspace.is_conscious()
        
        # 7. EMBODIMENT
        emotional_input = reward - fear
        threat = fear
        nt_levels = self.neuromodulation.get_levels()
        self.embodiment.update(
            emotional_input=emotional_input,
            threat=threat,
            cognitive_load=self.state.surprise,
            nt_levels=nt_levels
        )
        
        # 8. NEUROMODULAZIONE
        self.neuromodulation.update(
            reward=reward,
            punishment=fear,
            salience=max(fear, reward),
            novelty=min(1.0, self.state.surprise)
        )
        
        # Aggiorna stato
        self.state.arousal = self.embodiment.interoception.get_arousal()
        self.state.valence = self.amygdala.get_valence()
        self.state.attention_focus = self.attention.get_focus()
        
        return {
            'time': self.state.time,
            'surprise': self.state.surprise,
            'arousal': self.state.arousal,
            'valence': self.state.valence,
            'fear': fear,
            'reward': reward,
            'is_conscious': self.state.is_conscious,
            'workspace_winner': winner
        }
    
    def learn(self, reward: float, outcome: Optional[np.ndarray] = None) -> Dict:
        """
        Apprendi da reward.
        
        Args:
            reward: Reward ricevuto (-1 a +1)
            outcome: Pattern associato (opzionale)
        
        Returns:
            Dict con info sull'apprendimento
        """
        # 1. NEUROMODULAZIONE
        if reward > 0:
            self.neuromodulation.update(reward=reward)
        else:
            self.neuromodulation.update(punishment=-reward)
        
        dopamine = self.neuromodulation.get(Neuromodulator.DOPAMINE)
        learning_rate = self.neuromodulation.get_learning_rate_modulation()
        
        # 2. PLASTICITA CORTICALE
        for col in self.columns:
            col.learn(reward)
        
        # 3. PREDICTIVE CODING
        self.predictive_coding.learn(learning_rate * 0.01)
        
        # 4. MEMORIA
        if outcome is not None:
            outcome_np = outcome if isinstance(outcome, np.ndarray) else outcome.cpu().numpy()
            
            # Ippocampo
            context = {
                'reward': reward,
                'arousal': self.state.arousal,
                'valence': self.state.valence,
                'time': self.state.time
            }
            self.hippocampus.encode(outcome_np, context)
            
            # Amigdala
            if reward > 0.3:
                self.amygdala.learn_reward(outcome_np, abs(reward))
            elif reward < -0.3:
                self.amygdala.learn_fear(outcome_np, abs(reward))
            
            # Marcatori somatici
            self.embodiment.create_marker(outcome_np, reward)
        
        # 5. GANGLI DELLA BASE
        if self.state.current_action >= 0:
            self.basal_ganglia.learn(reward, self.state.current_action)
        
        return {
            'dopamine': dopamine,
            'learning_rate': learning_rate,
            'serotonin': self.neuromodulation.get(Neuromodulator.SEROTONIN),
            'memories': len(self.hippocampus.stored_patterns),
            'markers': len(self.embodiment.somatic_markers.markers)
        }
    
    def evaluate(self, pattern: np.ndarray) -> Dict:
        """
        Valuta un pattern.
        
        Args:
            pattern: Pattern da valutare
        
        Returns:
            Dict con valutazione
        """
        pattern_np = pattern if isinstance(pattern, np.ndarray) else pattern.cpu().numpy()
        
        # Amigdala
        fear, reward = self.amygdala.evaluate(pattern_np[:50] if len(pattern_np) > 50 else pattern_np)
        
        # Marcatori somatici
        valence, arousal = self.embodiment.evaluate(pattern_np)
        
        # Memoria
        recalled, context = self.hippocampus.recall(pattern_np)
        
        # Combinazione
        combined_valence = valence * 0.5 + (reward - fear) * 0.5
        
        return {
            'valence': combined_valence,
            'arousal': arousal,
            'fear': fear,
            'reward': reward,
            'recognized': recalled is not None,
            'context': context
        }
    
    def select_action(self, cortical_input: Optional[np.ndarray] = None) -> int:
        """
        Seleziona un'azione usando i gangli della base.
        
        Returns:
            Indice dell'azione selezionata
        """
        if cortical_input is not None:
            self.basal_ganglia.receive_cortical(cortical_input)
        
        # Modula con dopamina
        dopamine = self.neuromodulation.get(Neuromodulator.DOPAMINE)
        self.basal_ganglia.set_dopamine(dopamine)
        
        self.basal_ganglia.step()
        action = self.basal_ganglia.select_action()
        
        self.state.current_action = action
        return action
    
    def step(self, dt: float = 1.0):
        """Simula un timestep senza input."""
        self.state.time += 1
        
        # Decay
        self.global_workspace.decay()
        
        # Step strutture
        self.thalamus.step(dt)
        for col in self.columns:
            col.step(dt)
        self.hippocampus.step(dt)
        self.amygdala.step(dt)
        self.basal_ganglia.step(dt)
        
        # Neuromodulazione decay
        self.neuromodulation.update(dt=dt)
        nt_levels = self.neuromodulation.get_levels()
        self.embodiment.interoception.update(
            dt=dt,
            nt_levels=nt_levels
        )

        if hasattr(self.neuromodulation, 'receptor_effects') and self.neuromodulation.receptor_effects:
            for col in self.columns:
                for layer_name, layer_dict in col.layers.items():
                    for neuron_type, group in layer_dict.items():
                        # Get effects for this neuron type
                        type_key = neuron_type.name if hasattr(neuron_type, 'name') else str(neuron_type)
                        if type_key in self.neuromodulation.receptor_effects:
                            effects = self.neuromodulation.receptor_effects[type_key]

                            # Apply to neural parameters
                            self._apply_modulation_to_group(group, effects)

    def _apply_modulation_to_group(self, group, effects):
        """Apply receptor-mediated modulation to a neuron group."""

        # 1. Excitability (modifies threshold)
        if 'excitability_change' in effects and hasattr(group, 'V_th'):
            # Negative = more excitable (lower threshold)
            # Positive = less excitable (higher threshold)
            modulation_mV = effects['excitability_change'] * 10  # Scale to mV

            if TORCH_AVAILABLE and hasattr(group.V_th, 'add_'):
                group.V_th.add_(modulation_mV)
            else:
                group.V_th += modulation_mV

        # 2. Gain (modifies input responsiveness)
        if 'gain_change' in effects:
            gain_multiplier = 1.0 + effects['gain_change']

            # Apply to synaptic weights or input current
            if hasattr(group, 'I_syn'):
                if TORCH_AVAILABLE and hasattr(group.I_syn, 'mul_'):
                    group.I_syn.mul_(gain_multiplier)
                else:
                    group.I_syn *= gain_multiplier

        # 3. Plasticity (modifies learning rate)
        if 'plasticity_change' in effects:
            # Store for use in synaptic plasticity rules
            if not hasattr(group, 'plasticity_modulation'):
                group.plasticity_modulation = 1.0

            group.plasticity_modulation = 1.0 + effects['plasticity_change']
    
    def get_state(self) -> Dict:
        """Ottieni stato completo."""
        nm = self.neuromodulation
        raw_valence = (
            nm.serotonin * 0.4 +
            nm.dopamine * 0.6 -
            nm.noradrenaline * 0.2
        )
        valence = max(0.0, min(1.0, (raw_valence + 0.2) / 1.2))
        return {
            'time': self.state.time,
            'total_neurons': self.total_neurons,
            'backend': BACKEND,
            
            # Neuromodulazione
            'dopamine': self.neuromodulation.get(Neuromodulator.DOPAMINE),
            'serotonin': self.neuromodulation.get(Neuromodulator.SEROTONIN),
            'noradrenaline': self.neuromodulation.get(Neuromodulator.NORADRENALINE),
            'acetylcholine': self.neuromodulation.get(Neuromodulator.ACETYLCHOLINE),
            'gaba': self.neuromodulation.get(Neuromodulator.GABA),
            'glutamate': self.neuromodulation.get(Neuromodulator.GLUTAMATE),
            
            # Embodiment
            'arousal': self.state.arousal,
            'valence': valence,
            'heart_rate': self.embodiment.interoception.state.heart_rate,
            'respiratory_rate': self.embodiment.interoception.state.respiratory_rate,
            'skin_conductance': self.embodiment.interoception.state.skin_conductance,
            'muscle_tension': self.embodiment.interoception.state.muscle_tension,
            'gut_feeling': self.embodiment.interoception.state.gut_feeling,
            'temperature': self.embodiment.interoception.state.temperature,
            'pain': self.embodiment.interoception.state.pain,
            'fatigue': self.embodiment.interoception.state.fatigue,
            
            # Cognizione
            'surprise': self.state.surprise,
            'is_conscious': self.state.is_conscious,
            'attention_focus': self.state.attention_focus,
            
            # Memoria
            'episodic_memories': len(self.hippocampus.stored_patterns),
            'somatic_markers': len(self.embodiment.somatic_markers.markers),
            'fear_associations': len(self.amygdala.fear_associations),
            'reward_associations': len(self.amygdala.reward_associations),
            
            # Corteccia
            'n_columns': len(self.columns),
        }
    
    def reset(self):
        """Reset stato."""
        self.state = BrainState()
        self.neuromodulation.reset()
        self.hippocampus.clear()
        self.embodiment.somatic_markers.clear()
        for col in self.columns:
            col.reset()


# ============================================================
# FACTORY
# ============================================================

def create_brain(
    scale: float = 1.0,
    debug: bool = True
) -> RealisticBrain:
    """
    Crea un cervello realistico.
    
    Args:
        scale: Fattore di scala (1.0 = ~5000 neuroni)
        debug: Mostra info debug
    
    Returns:
        RealisticBrain
    """
    n_neurons = int(5000 * scale)
    n_columns = max(2, int(4 * scale))
    
    return RealisticBrain(
        n_neurons=n_neurons,
        n_columns=n_columns,
        debug=debug
    )
