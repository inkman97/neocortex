"""
LOIHI EMBODIMENT - 8 Physiological Parameters
"""
import numpy as np
from typing import Dict
import sys
sys.path.append("..")
from core.neurons_loihi import SCALE, float_to_fixed, fixed_to_float

class EmbodiedState:
    def __init__(self):
        self.heart_rate = float_to_fixed(0.5)
        self.respiratory_rate = float_to_fixed(0.5)
        self.skin_conductance = float_to_fixed(0.3)
        self.muscle_tension = float_to_fixed(0.4)
        self.gut_feeling = float_to_fixed(0.5)
        self.temperature = float_to_fixed(0.5)
        self.pain = float_to_fixed(0.0)
        self.fatigue = float_to_fixed(0.3)
    
    def update(self, nt_levels, arousal, valence):
        target_hr = 0.4 + 0.3 * nt_levels.get("NE", 0.5) + 0.2 * arousal
        self.heart_rate = self._smooth(self.heart_rate, target_hr, 0.1)
        
        target_rr = 0.4 + 0.25 * nt_levels.get("NE", 0.5) + 0.25 * arousal
        self.respiratory_rate = self._smooth(self.respiratory_rate, target_rr, 0.12)
        
        target_sc = arousal * 0.8 + 0.2 * nt_levels.get("NE", 0.5)
        self.skin_conductance = self._smooth(self.skin_conductance, target_sc, 0.15)
        
        target_mt = 0.3 + 0.4 * arousal - 0.3 * max(0, valence)
        self.muscle_tension = self._smooth(self.muscle_tension, target_mt, 0.08)
        
        target_gf = 0.5 + 0.3 * nt_levels.get("5HT", 0.5) + 0.2 * valence
        self.gut_feeling = self._smooth(self.gut_feeling, target_gf, 0.05)
        
        target_temp = 0.5 + 0.15 * nt_levels.get("NE", 0.5) + 0.1 * arousal
        self.temperature = self._smooth(self.temperature, target_temp, 0.03)
        
        target_pain = 0.2 * (1.0 - nt_levels.get("5HT", 0.5))
        self.pain = self._smooth(self.pain, target_pain, 0.06)
        
        target_fatigue = 0.7 - 0.4 * nt_levels.get("DA", 0.4) - 0.3 * nt_levels.get("ACh", 0.5)
        self.fatigue = self._smooth(self.fatigue, target_fatigue, 0.04)
    
    def _smooth(self, current, target, rate):
        curr_f = fixed_to_float(current)
        new_val = curr_f * (1 - rate) + target * rate
        return float_to_fixed(np.clip(new_val, 0, 1))
    
    def to_dict(self):
        return {
            "heart_rate": fixed_to_float(self.heart_rate),
            "respiratory_rate": fixed_to_float(self.respiratory_rate),
            "skin_conductance": fixed_to_float(self.skin_conductance),
            "muscle_tension": fixed_to_float(self.muscle_tension),
            "gut_feeling": fixed_to_float(self.gut_feeling),
            "temperature": fixed_to_float(self.temperature),
            "pain": fixed_to_float(self.pain),
            "fatigue": fixed_to_float(self.fatigue)
        }
