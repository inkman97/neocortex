"""Translation from HTTP molecular-target names to DrugMechanism keyword arguments."""

DIRECT_TARGET_ALIASES = {
    'sert_inhibition': 'sert_inhibition',
    'dat_inhibition': 'dat_inhibition',
    'net_inhibition': 'net_inhibition',

    'mao_a_inhibition': 'mao_a_inhibition',
    'maoa_inhibition': 'mao_a_inhibition',
    'mao_b_inhibition': 'mao_b_inhibition',
    'maob_inhibition': 'mao_b_inhibition',
    'ache_inhibition': 'ache_inhibition',
    'acetylcholinesterase_inhibition': 'ache_inhibition',

    'da_precursor': 'da_precursor',
    'd2_agonism': 'd2_agonism',
    'd3_agonism': 'd3_agonism',
    'd2_antagonism': 'd2_antagonism',
    'd3_antagonism': 'd3_antagonism',
    'd2_partial_agonism': 'd2_partial_agonism',

    'ht1a_agonism': 'ht1a_agonism',
    '5ht1a_agonism': 'ht1a_agonism',
    'ht2a_antagonism': 'ht2a_antagonism',
    '5ht2a_antagonism': 'ht2a_antagonism',

    'alpha2_antagonism': 'alpha2_antagonism',

    'gaba_a_pam': 'gaba_a_pam',
    'gat_inhibition': 'gat_inhibition',
    'gaba_transaminase_inhibition': 'gaba_transaminase_inhibition',

    'voltage_gated_sodium_blocker': 'voltage_gated_sodium_blocker',
    'glutamate_release_inhibition': 'glutamate_release_inhibition',
    'nmda_antagonism': 'nmda_antagonism',
    'alpha2delta_blocker': 'alpha2delta_blocker',
    'alpha2delta_calcium_channel_blocker': 'alpha2delta_blocker',
}

LEGACY_TARGET_ALIASES = {
    ('SERT', 'inhibition'): 'sert_inhibition',
    ('DAT', 'inhibition'): 'dat_inhibition',
    ('NET', 'inhibition'): 'net_inhibition',
    ('MAO-A', 'inhibition'): 'mao_a_inhibition',
    ('MAOA', 'inhibition'): 'mao_a_inhibition',
    ('MAO-B', 'inhibition'): 'mao_b_inhibition',
    ('MAOB', 'inhibition'): 'mao_b_inhibition',
    ('ACHE', 'inhibition'): 'ache_inhibition',
    ('ACH', 'inhibition'): 'ache_inhibition',
    ('5HT2A', 'antagonism'): 'ht2a_antagonism',
    ('5-HT2A', 'antagonism'): 'ht2a_antagonism',
    ('5HT1A', 'agonism'): 'ht1a_agonism',
    ('5-HT1A', 'agonism'): 'ht1a_agonism',
}

RECEPTOR_TARGET_ALIASES = {
    'D2': {
        'antagonism': 'd2_antagonism',
        'agonism': 'd2_agonism',
        'partial_agonism': 'd2_partial_agonism',
    },
    'D3': {
        'antagonism': 'd3_antagonism',
        'agonism': 'd3_agonism',
    },
}

ACTION_SYNONYMS = {
    'inhibitor': 'inhibition',
    'inhibition': 'inhibition',
    'blocker': 'inhibition',
    'blocking': 'inhibition',
    'antagonist': 'antagonism',
    'antagonism': 'antagonism',
    'block': 'antagonism',
    'agonist': 'agonism',
    'agonism': 'agonism',
    'activate': 'agonism',
    'activation': 'agonism',
    'partial_agonist': 'partial_agonism',
    'partial': 'partial_agonism',
    'mechanism': 'mechanism',
    'modulator': 'mechanism',
    'pam': 'mechanism',
}

UNRESOLVED = object()


def normalize_action(action):
    return ACTION_SYNONYMS.get(action.lower(), action.lower())


def resolve_mechanism_key(target_name, action):
    """Return the DrugMechanism kwarg for a target, None when the receptor is
    known but the action is not, or UNRESOLVED when the target is unknown."""
    lowered = target_name.lower()
    if lowered in DIRECT_TARGET_ALIASES:
        return DIRECT_TARGET_ALIASES[lowered]

    uppercased = lowered.upper()
    if (uppercased, action) in LEGACY_TARGET_ALIASES:
        return LEGACY_TARGET_ALIASES[(uppercased, action)]

    if uppercased in RECEPTOR_TARGET_ALIASES:
        return RECEPTOR_TARGET_ALIASES[uppercased].get(action)

    return UNRESOLVED
