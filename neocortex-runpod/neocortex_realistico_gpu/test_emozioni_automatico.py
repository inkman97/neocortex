"""
TEST DETTAGLIATO EMOZIONI E STATI CORPOREI
Versione automatica (senza pause)
"""

import numpy as np
import time
import sys

sys.path.insert(0, '.')
from brain import create_brain
from core import Neuromodulator

# ============================================================
# CONFIGURAZIONE
# ============================================================

SCALA = 1.0
PASSI_PER_FASE = 10

# ============================================================
# FUNZIONI HELPER
# ============================================================

def stampa_stato(brain, titolo=""):
    """Stampa tutti i valori del cervello."""
    state = brain.get_state()
    emb = brain.embodiment.interoception.state
    
    print(f"\n{'─' * 60}")
    if titolo:
        print(f"  {titolo}")
        print(f"{'─' * 60}")
    
    print(f"""
  NEUROMODULATORI:
    Dopamina:       {state['dopamine']:.3f}  {'[ALTO]' if state['dopamine'] > 0.6 else '[basso]' if state['dopamine'] < 0.4 else ''}
    Serotonina:     {state['serotonin']:.3f}  {'[ALTO]' if state['serotonin'] > 0.6 else '[basso]' if state['serotonin'] < 0.4 else ''}
    Noradrenalina:  {state['noradrenaline']:.3f}  {'[ALTO]' if state['noradrenaline'] > 0.6 else '[basso]' if state['noradrenaline'] < 0.4 else ''}
    Acetilcolina:   {state['acetylcholine']:.3f}  {'[ALTO]' if state['acetylcholine'] > 0.6 else '[basso]' if state['acetylcholine'] < 0.4 else ''}
  
  CORPO:
    Battito cardiaco:   {emb.heart_rate:.3f}  {'[TACHICARDIA]' if emb.heart_rate > 0.7 else '[bradicardia]' if emb.heart_rate < 0.3 else '[normale]'}
    Respirazione:       {emb.respiratory_rate:.3f}  {'[VELOCE]' if emb.respiratory_rate > 0.7 else '[lenta]' if emb.respiratory_rate < 0.3 else '[normale]'}
    Sudorazione:        {emb.skin_conductance:.3f}  {'[SUDATO]' if emb.skin_conductance > 0.6 else '[secco]' if emb.skin_conductance < 0.2 else ''}
    Tensione muscolare: {emb.muscle_tension:.3f}  {'[TESO]' if emb.muscle_tension > 0.6 else '[rilassato]' if emb.muscle_tension < 0.2 else ''}
    Sensazione pancia:  {emb.gut_feeling:.3f}  {'[bene]' if emb.gut_feeling > 0.6 else '[MALE]' if emb.gut_feeling < 0.4 else ''}
    Fatica:             {emb.fatigue:.3f}  {'[STANCO]' if emb.fatigue > 0.6 else '[energico]' if emb.fatigue < 0.3 else ''}
  
  STATO MENTALE:
    Arousal:        {state['arousal']:.3f}  {'[ALLERTA]' if state['arousal'] > 0.6 else '[calmo]' if state['arousal'] < 0.3 else ''}
    Valenza:        {state['valence']:+.3f}  {'[POSITIVO]' if state['valence'] > 0.2 else '[NEGATIVO]' if state['valence'] < -0.2 else '[neutro]'}
    Sorpresa:       {state['surprise']:.3f}
  
  MEMORIA:
    Episodica:      {state['episodic_memories']} ricordi
    Marcatori:      {state['somatic_markers']} marcatori
    Paure:          {state['fear_associations']} associazioni
    Piaceri:        {state['reward_associations']} associazioni
""")


def stampa_riga(passo, totale, label, brain):
    """Stampa una riga di valori."""
    emb = brain.embodiment.interoception.state
    nm = brain.neuromodulation
    print(f"  [{passo:2d}/{totale}] {label:12s} | "
          f"Battito:{emb.heart_rate:.2f} | "
          f"Tensione:{emb.muscle_tension:.2f} | "
          f"Sudore:{emb.skin_conductance:.2f} | "
          f"DA:{nm.get(Neuromodulator.DOPAMINE):.2f} | "
          f"NE:{nm.get(Neuromodulator.NORADRENALINE):.2f} | "
          f"5HT:{nm.get(Neuromodulator.SEROTONIN):.2f}")


def stampa_separatore(testo):
    print("\n")
    print("=" * 70)
    print(f"   {testo}")
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("   TEST EMOZIONI E STATI CORPOREI")
print("=" * 70)

# Crea cervello
print(f"\n[*] Creazione cervello (scala={SCALA})...")
brain = create_brain(scale=SCALA, debug=False)
print(f"[OK] Creato con {brain.get_state()['total_neurons']} neuroni")

# Pattern
pattern_neutro = np.ones(100, dtype=np.float32) * 0.5
pattern_minaccia = np.random.rand(100).astype(np.float32)
pattern_piacere = np.random.rand(100).astype(np.float32)

# ============================================================
# FASE 1: STATO INIZIALE
# ============================================================

stampa_separatore("FASE 1: STATO INIZIALE")
stampa_stato(brain, "Cervello a riposo")

# ============================================================
# FASE 2: SPAVENTO GRADUALE
# ============================================================

stampa_separatore("FASE 2: SPAVENTO GRADUALE (minaccia 0.1 -> 1.0)")
print("\n  LEGENDA: DA=Dopamina, NE=Noradrenalina, 5HT=Serotonina\n")

for i in range(PASSI_PER_FASE):
    livello = (i + 1) / PASSI_PER_FASE
    
    brain.perceive(pattern_minaccia * livello)
    brain.embodiment.update(
        emotional_input=-livello,
        threat=livello,
        cognitive_load=livello * 0.5
    )
    brain.neuromodulation.update(
        punishment=livello,
        salience=livello,
        novelty=0.3
    )
    
    stampa_riga(i+1, PASSI_PER_FASE, f"Minaccia:{livello:.1f}", brain)

# Associa paura
brain.amygdala.learn_fear(pattern_minaccia, strength=1.0)
brain.embodiment.create_marker(pattern_minaccia, valence=-0.8)

stampa_stato(brain, "Dopo SPAVENTO MASSIMO")

# ============================================================
# FASE 3: CALMA GRADUALE
# ============================================================

stampa_separatore("FASE 3: RITORNO ALLA CALMA (20 passi di riposo)")

for i in range(PASSI_PER_FASE * 2):  # Doppia durata per vedere il decay
    # NESSUN input - solo riposo totale
    # Non chiamiamo perceive per evitare attivazione
    brain.embodiment.update(
        emotional_input=0.0,    # Neutro
        threat=0.0,             # ZERO minaccia
        cognitive_load=0.0,     # ZERO carico
        activity=0.0            # ZERO attivita
    )
    brain.neuromodulation.update(
        reward=0.0,
        punishment=0.0,
        salience=0.0,
        novelty=0.0,
        effort=0.0
    )
    
    if (i + 1) % 4 == 0:
        stampa_riga(i+1, PASSI_PER_FASE*2, f"Riposo", brain)

stampa_stato(brain, "Dopo fase di CALMA")

# ============================================================
# FASE 4: PIACERE / REWARD
# ============================================================

stampa_separatore("FASE 4: PIACERE E REWARD")

for i in range(PASSI_PER_FASE):
    livello = (i + 1) / PASSI_PER_FASE
    
    brain.perceive(pattern_piacere)
    brain.embodiment.update(
        emotional_input=livello,
        threat=0.0,
        activity=0.2
    )
    brain.neuromodulation.update(
        reward=livello,
        salience=livello * 0.5,
        novelty=0.2
    )
    brain.learn(reward=livello, outcome=pattern_piacere)
    
    stampa_riga(i+1, PASSI_PER_FASE, f"Piacere:{livello:.1f}", brain)

stampa_stato(brain, "Dopo fase di PIACERE")

# ============================================================
# FASE 5: TEST MEMORIA
# ============================================================

stampa_separatore("FASE 5: TEST MEMORIA EMOTIVA")

print("\n  Ripresento i pattern per vedere le reazioni...\n")

# Pattern minaccia
brain.perceive(pattern_minaccia)
eval_m = brain.evaluate(pattern_minaccia)
fear_m, reward_m = brain.amygdala.evaluate(pattern_minaccia[:50])
val_m, aro_m = brain.embodiment.evaluate(pattern_minaccia)

print(f"""  PATTERN MINACCIA (imparato come PAUROSO):
    Valenza:        {eval_m['valence']:+.3f}
    Arousal:        {eval_m['arousal']:.3f}
    Fear amigdala:  {fear_m:.3f}
    Marcatore:      {val_m:+.3f}
    Riconosciuto:   {'SI' if eval_m['recognized'] else 'NO'}
""")

# Pattern piacere
brain.perceive(pattern_piacere)
eval_p = brain.evaluate(pattern_piacere)
fear_p, reward_p = brain.amygdala.evaluate(pattern_piacere[:50])
val_p, aro_p = brain.embodiment.evaluate(pattern_piacere)

print(f"""  PATTERN PIACERE (imparato come BUONO):
    Valenza:        {eval_p['valence']:+.3f}
    Arousal:        {eval_p['arousal']:.3f}
    Reward amigdala:{reward_p:.3f}
    Marcatore:      {val_p:+.3f}
    Riconosciuto:   {'SI' if eval_p['recognized'] else 'NO'}
""")

# Pattern nuovo
pattern_nuovo = np.random.rand(100).astype(np.float32) * 0.3
eval_n = brain.evaluate(pattern_nuovo)

print(f"""  PATTERN NUOVO (mai visto):
    Valenza:        {eval_n['valence']:+.3f}
    Arousal:        {eval_n['arousal']:.3f}
    Riconosciuto:   {'SI' if eval_n['recognized'] else 'NO'}
""")

# ============================================================
# FASE 6: FATICA
# ============================================================

stampa_separatore("FASE 6: ACCUMULO FATICA (stress prolungato)")

for i in range(PASSI_PER_FASE * 2):
    brain.perceive(pattern_minaccia * 0.4)
    brain.embodiment.update(
        emotional_input=-0.2,
        threat=0.3,
        activity=0.5,
        cognitive_load=0.6
    )
    brain.neuromodulation.update(
        punishment=0.2,
        salience=0.3,
        effort=0.5
    )
    
    if (i + 1) % 4 == 0:
        emb = brain.embodiment.interoception.state
        print(f"  [{i+1:2d}/{PASSI_PER_FASE*2}] "
              f"Fatica:{emb.fatigue:.2f} | "
              f"Battito:{emb.heart_rate:.2f} | "
              f"Tensione:{emb.muscle_tension:.2f} | "
              f"Pancia:{emb.gut_feeling:.2f}")

stampa_stato(brain, "Dopo STRESS PROLUNGATO")

# ============================================================
# RIEPILOGO
# ============================================================

stampa_separatore("RIEPILOGO FINALE")

state = brain.get_state()
print(f"""
  STATISTICHE:
    Neuroni:            {state['total_neurons']}
    Memorie episodiche: {state['episodic_memories']}
    Marcatori somatici: {state['somatic_markers']}
    Associazioni paura: {state['fear_associations']}
    Associazioni reward:{state['reward_associations']}

  APPRENDIMENTO EMOTIVO:
    Pattern MINACCIA: valenza = {eval_m['valence']:+.3f} (atteso: NEGATIVO)
    Pattern PIACERE:  valenza = {eval_p['valence']:+.3f} (atteso: POSITIVO)
    Pattern NUOVO:    valenza = {eval_n['valence']:+.3f} (atteso: ~0)
""")

# Verifica
if eval_m['valence'] < eval_n['valence'] < eval_p['valence']:
    print("  [OK] Apprendimento emotivo CORRETTO!")
    print("       MINACCIA < NEUTRO < PIACERE")
elif eval_m['valence'] < eval_p['valence']:
    print("  [OK] Apprendimento parziale: MINACCIA < PIACERE")
else:
    print("  [!!] Potrebbe servire piu training")

print("\n" + "=" * 70)
print("   TEST COMPLETATO")
print("=" * 70)
