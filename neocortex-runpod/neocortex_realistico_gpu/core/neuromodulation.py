# """
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                                                                              ║
# ║                    SISTEMA NEUROMODULATORIO                                  ║
# ║                                                                              ║
# ║     Neuromodulatori principali:                                              ║
# ║                                                                              ║
# ║     DOPAMINA (DA):                                                           ║
# ║       - Reward prediction error                                              ║
# ║       - Motivazione, piacere                                                 ║
# ║       - Origine: VTA, Substantia Nigra                                       ║
# ║                                                                              ║
# ║     SEROTONINA (5-HT):                                                       ║
# ║       - Pazienza, inibizione                                                 ║
# ║       - Umore, ansia                                                         ║
# ║       - Origine: Nuclei del Rafe                                             ║
# ║                                                                              ║
# ║     NORADRENALINA (NE):                                                      ║
# ║       - Arousal, attenzione                                                  ║
# ║       - Fight-or-flight                                                      ║
# ║       - Origine: Locus Coeruleus                                             ║
# ║                                                                              ║
# ║     ACETILCOLINA (ACh):                                                      ║
# ║       - Apprendimento, memoria                                               ║
# ║       - Attenzione selettiva                                                 ║
# ║       - Origine: Nucleo Basale, Pedunculopontino                             ║
# ║                                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
# """
#
# import numpy as np
# from enum import Enum
# from dataclasses import dataclass
# from typing import Dict, Optional
#
# from .neurons import BACKEND
# if BACKEND == "torch":
#     import torch
#     from .neurons import DEVICE
#
#
# # ============================================================
# # NEUROMODULATORI
# # ============================================================
#
# class Neuromodulator(Enum):
#     """Sistemi neuromodulatori."""
#     DOPAMINE = "dopamine"
#     SEROTONIN = "serotonin"
#     NORADRENALINE = "noradrenaline"
#     ACETYLCHOLINE = "acetylcholine"
#
#
# @dataclass
# class NeuromodulatorParams:
#     """Parametri per ogni neuromodulatore."""
#     tau_rise: float       # Tempo di salita (ms)
#     tau_decay: float      # Tempo di decadimento (ms)
#     baseline: float       # Livello basale
#     max_level: float      # Livello massimo
#     min_level: float      # Livello minimo
#
#
# NEUROMODULATOR_PARAMS = {
#     Neuromodulator.DOPAMINE: NeuromodulatorParams(
#         tau_rise=50.0,
#         tau_decay=200.0,
#         baseline=0.5,
#         max_level=1.0,
#         min_level=0.0
#     ),
#     Neuromodulator.SEROTONIN: NeuromodulatorParams(
#         tau_rise=100.0,
#         tau_decay=500.0,    # Molto lento
#         baseline=0.5,
#         max_level=1.0,
#         min_level=0.0
#     ),
#     Neuromodulator.NORADRENALINE: NeuromodulatorParams(
#         tau_rise=20.0,      # Veloce
#         tau_decay=100.0,
#         baseline=0.3,
#         max_level=1.0,
#         min_level=0.0
#     ),
#     Neuromodulator.ACETYLCHOLINE: NeuromodulatorParams(
#         tau_rise=30.0,
#         tau_decay=150.0,
#         baseline=0.4,
#         max_level=1.0,
#         min_level=0.0
#     ),
# }
#
#
# # ============================================================
# # SISTEMA NEUROMODULATORIO
# # ============================================================
#
# class NeuromodulationSystem:
#     """
#     Sistema neuromodulatorio completo.
#
#     Modella le dinamiche dei principali neuromodulatori
#     e i loro effetti sulla plasticita e sul processing.
#     """
#
#     def __init__(self):
#         # Livelli attuali
#         self.levels: Dict[Neuromodulator, float] = {
#             nm: NEUROMODULATOR_PARAMS[nm].baseline
#             for nm in Neuromodulator
#         }
#
#         # Target levels (verso cui tendono)
#         self.targets: Dict[Neuromodulator, float] = {
#             nm: NEUROMODULATOR_PARAMS[nm].baseline
#             for nm in Neuromodulator
#         }
#
#         # Storico per analisi
#         self.history: Dict[Neuromodulator, list] = {
#             nm: [] for nm in Neuromodulator
#         }
#
#         # Decay rates (for drug mechanisms)
#         self.decay_rates: Dict[Neuromodulator, float] = {
#             Neuromodulator.SEROTONIN: 0.001,
#             Neuromodulator.DOPAMINE: 0.001,
#             Neuromodulator.NORADRENALINE: 0.001,
#             Neuromodulator.ACETYLCHOLINE: 0.001
#         }
#
#     # ═══════════════════════════════════════════════════════════════
#     # COMPATIBILITY PROPERTIES for drug_simulator.py
#     # ═══════════════════════════════════════════════════════════════
#
#     @property
#     def serotonin(self):
#         return self.levels[Neuromodulator.SEROTONIN]
#
#     @serotonin.setter
#     def serotonin(self, value):
#         self.levels[Neuromodulator.SEROTONIN] = float(value)
#
#     @property
#     def dopamine(self):
#         return self.levels[Neuromodulator.DOPAMINE]
#
#     @dopamine.setter
#     def dopamine(self, value):
#         self.levels[Neuromodulator.DOPAMINE] = float(value)
#
#     @property
#     def noradrenaline(self):
#         return self.levels[Neuromodulator.NORADRENALINE]
#
#     @noradrenaline.setter
#     def noradrenaline(self, value):
#         self.levels[Neuromodulator.NORADRENALINE] = float(value)
#
#     @property
#     def acetylcholine(self):
#         return self.levels[Neuromodulator.ACETYLCHOLINE]
#
#     @acetylcholine.setter
#     def acetylcholine(self, value):
#         self.levels[Neuromodulator.ACETYLCHOLINE] = float(value)
#
#     # Decay rate properties
#     @property
#     def serotonin_decay(self):
#         return self.decay_rates[Neuromodulator.SEROTONIN]
#
#     @serotonin_decay.setter
#     def serotonin_decay(self, value):
#         self.decay_rates[Neuromodulator.SEROTONIN] = float(value)
#
#     @property
#     def dopamine_decay(self):
#         return self.decay_rates[Neuromodulator.DOPAMINE]
#
#     @dopamine_decay.setter
#     def dopamine_decay(self, value):
#         self.decay_rates[Neuromodulator.DOPAMINE] = float(value)
#
#     @property
#     def noradrenaline_decay(self):
#         return self.decay_rates[Neuromodulator.NORADRENALINE]
#
#     @noradrenaline_decay.setter
#     def noradrenaline_decay(self, value):
#         self.decay_rates[Neuromodulator.NORADRENALINE] = float(value)
#
#     @property
#     def acetylcholine_decay(self):
#         return self.decay_rates[Neuromodulator.ACETYLCHOLINE]
#
#     @acetylcholine_decay.setter
#     def acetylcholine_decay(self, value):
#         self.decay_rates[Neuromodulator.ACETYLCHOLINE] = float(value)
#
#     def update(
#         self,
#         reward: float = 0.0,
#         punishment: float = 0.0,
#         salience: float = 0.0,
#         novelty: float = 0.0,
#         effort: float = 0.0,
#         dt: float = 1.0
#     ):
#         """
#         Aggiorna livelli neuromodulatori in base agli eventi.
#
#         Args:
#             reward: Reward ricevuto (0-1)
#             punishment: Punizione ricevuta (0-1)
#             salience: Salienza dello stimolo (0-1)
#             novelty: Novita dello stimolo (0-1)
#             effort: Sforzo richiesto (0-1)
#             dt: Timestep in ms
#         """
#         # Prima, tutti i target decadono verso baseline (decay piu forte)
#         for nm in Neuromodulator:
#             baseline = NEUROMODULATOR_PARAMS[nm].baseline
#             # REDUCED decay to allow drug-induced target changes to persist
#             # Changed from 0.15 to 0.01 to let drugs work
#             self.targets[nm] += (baseline - self.targets[nm]) * 0.01
#
#         # DOPAMINA: Reward Prediction Error
#         if reward > 0 or punishment > 0:
#             reward_prediction = self.levels[Neuromodulator.DOPAMINE]
#             rpe = reward - reward_prediction
#             self.targets[Neuromodulator.DOPAMINE] += rpe * 0.3
#             self.targets[Neuromodulator.DOPAMINE] -= punishment * 0.2
#         self.targets[Neuromodulator.DOPAMINE] = np.clip(self.targets[Neuromodulator.DOPAMINE], 0, 1)
#
#         # SEROTONINA: Pazienza e inibizione
#         if effort > 0:
#             self.targets[Neuromodulator.SEROTONIN] += effort * 0.15
#         if reward > 0:
#             self.targets[Neuromodulator.SEROTONIN] -= reward * 0.1
#         self.targets[Neuromodulator.SEROTONIN] = np.clip(self.targets[Neuromodulator.SEROTONIN], 0, 1)
#
#         # NORADRENALINA: Arousal
#         if salience > 0 or novelty > 0 or punishment > 0:
#             self.targets[Neuromodulator.NORADRENALINE] += salience * 0.2
#             self.targets[Neuromodulator.NORADRENALINE] += novelty * 0.15
#             self.targets[Neuromodulator.NORADRENALINE] += punishment * 0.15
#         self.targets[Neuromodulator.NORADRENALINE] = np.clip(self.targets[Neuromodulator.NORADRENALINE], 0, 1)
#
#         # ACETILCOLINA: Apprendimento
#         if novelty > 0 or salience > 0:
#             self.targets[Neuromodulator.ACETYLCHOLINE] += novelty * 0.2
#             self.targets[Neuromodulator.ACETYLCHOLINE] += salience * 0.1
#         self.targets[Neuromodulator.ACETYLCHOLINE] = np.clip(self.targets[Neuromodulator.ACETYLCHOLINE], 0, 1)
#
#         # Dinamica: i livelli tendono verso i target
#         for nm in Neuromodulator:
#             params = NEUROMODULATOR_PARAMS[nm]
#             target = self.targets[nm]
#             current = self.levels[nm]
#
#             if target > current:
#                 tau = params.tau_rise
#             else:
#                 tau = params.tau_decay
#
#             # Equazione differenziale: dx/dt = (target - x) / tau
#             delta = (target - current) * (1 - np.exp(-dt / tau))
#             self.levels[nm] = current + delta
#
#             # Apply drug-induced decay modulation
#             decay_rate = self.decay_rates.get(nm, 0.001)
#             self.levels[nm] *= (1.0 - decay_rate)
#
#             # Clamp
#             self.levels[nm] = np.clip(
#                 self.levels[nm],
#                 params.min_level,
#                 params.max_level
#             )
#
#         # Salva storico
#         for nm in Neuromodulator:
#             self.history[nm].append(self.levels[nm])
#             if len(self.history[nm]) > 1000:
#                 self.history[nm].pop(0)
#
#     def get(self, nm: Neuromodulator) -> float:
#         """Ottieni livello di un neuromodulatore."""
#         return self.levels[nm]
#
#     def get_all(self) -> Dict[str, float]:
#         """Ottieni tutti i livelli."""
#         return {nm.value: level for nm, level in self.levels.items()}
#
#     def get_learning_rate_modulation(self) -> float:
#         """
#         Modulazione del learning rate basata su neuromodulatori.
#
#         DA * ACh aumentano apprendimento
#         """
#         da = self.levels[Neuromodulator.DOPAMINE]
#         ach = self.levels[Neuromodulator.ACETYLCHOLINE]
#         return da * ach * 2  # 0-2 range
#
#     def get_gain_modulation(self) -> float:
#         """
#         Modulazione del gain neuronale.
#
#         NE aumenta gain (piu reattivi)
#         """
#         ne = self.levels[Neuromodulator.NORADRENALINE]
#         return 0.5 + ne  # 0.5-1.5 range
#
#     def get_inhibition_modulation(self) -> float:
#         """
#         Modulazione dell'inibizione.
#
#         5-HT aumenta inibizione (piu controllo)
#         """
#         ser = self.levels[Neuromodulator.SEROTONIN]
#         return 0.5 + ser  # 0.5-1.5 range
#
#     def reset(self):
#         """Reset a baseline."""
#         for nm in Neuromodulator:
#             self.levels[nm] = NEUROMODULATOR_PARAMS[nm].baseline
#             self.targets[nm] = NEUROMODULATOR_PARAMS[nm].baseline
#         self.history = {nm: [] for nm in Neuromodulator}
#
#     def get_state(self) -> dict:
#         """Stato del sistema."""
#         return {
#             "levels": {nm.value: self.levels[nm] for nm in Neuromodulator},
#             "targets": {nm.value: self.targets[nm] for nm in Neuromodulator},
#             "learning_rate": self.get_learning_rate_modulation(),
#             "gain": self.get_gain_modulation(),
#             "inhibition": self.get_inhibition_modulation()
#         }
