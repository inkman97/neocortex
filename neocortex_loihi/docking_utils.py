"""
AUTODOCK VINA INTEGRATION - Multi-Target Support

AUTO-DETECTS which protein to dock based on disease profile!

Supported diseases:
- Alzheimer's → AChE docking
- Depression → SERT docking
- Parkinson's → DAT docking
- ADHD → DAT docking
- Schizophrenia → D2 docking
- Anxiety → GABA-A docking
- Epilepsy → GABA-A docking
"""

import os
import subprocess
import tempfile
from typing import Optional, Dict, Tuple
from rdkit import Chem
from rdkit.Chem import AllChem

# Path to Vina executable
VINA_PATH = "vina"  # Or: r"C:\AutoDock\vina.exe" on Windows

# Path to protein structures directory
PROTEIN_DIR = os.path.join(os.path.dirname(__file__), "protein_structures")


# ============================================================
# RECEPTOR DATABASE
# ============================================================

RECEPTOR_DATABASE = {
    'ache': {
        'pdb_id': '4EY7',
        'name': 'Acetylcholinesterase',
        'file': os.path.join(PROTEIN_DIR, '4EY7_prepared.pdbqt'),
        'box_center': [2.5, 64.5, 61.0],
        'box_size': [20, 20, 20],
        'mechanisms': ['ache_inhibition'],
        'neurotransmitter': 'acetylcholine'
    },

    'dat': {
        'pdb_id': '4XP4',
        'name': 'Dopamine Transporter',
        'file': os.path.join(PROTEIN_DIR, '4XP4_prepared.pdbqt'),
        'box_center': [0.0, 0.0, 0.0],
        'box_size': [20, 20, 20],
        'mechanisms': ['dat_inhibition'],
        'neurotransmitter': 'dopamine'
    },

    'sert': {
        'pdb_id': '5I6X',
        'name': 'Serotonin Transporter',
        'file': os.path.join(PROTEIN_DIR, '5I6X_prepared.pdbqt'),
        'box_center': [0.0, 0.0, 0.0],
        'box_size': [20, 20, 20],
        'mechanisms': ['sert_inhibition'],
        'neurotransmitter': 'serotonin'
    },

    'mao_a': {
        'pdb_id': '2Z5X',
        'name': 'Monoamine Oxidase A',
        'file': os.path.join(PROTEIN_DIR, '2Z5X_prepared.pdbqt'),
        'box_center': [0.0, 0.0, 0.0],
        'box_size': [20, 20, 20],
        'mechanisms': ['mao_a_inhibition'],
        'neurotransmitter': 'serotonin'
    },

    'd2': {
        'pdb_id': '6CM4',
        'name': 'Dopamine D2 Receptor',
        'file': os.path.join(PROTEIN_DIR, '6CM4_prepared.pdbqt'),
        'box_center': [0.0, 0.0, 0.0],
        'box_size': [20, 20, 20],
        'mechanisms': ['d2_antagonism', 'd3_antagonism'],
        'neurotransmitter': 'dopamine'
    },

    'gaba_a': {
        'pdb_id': '6D6U',
        'name': 'GABA-A Receptor',
        'file': os.path.join(PROTEIN_DIR, '6D6U_prepared.pdbqt'),
        'box_center': [0.0, 0.0, 0.0],
        'box_size': [20, 20, 20],
        'mechanisms': ['gaba_a_pam'],
        'neurotransmitter': 'gaba'
    },
}


def auto_select_receptor_from_disease(disease_profile: Dict[str, float]) -> Tuple[Optional[str], str]:
    """
    Automatically select receptor based on disease NT profile.

    Looks at the LARGEST deficit/excess and picks the corresponding target.

    Args:
        disease_profile: Dict like {'serotonin_deficit': 0.4, 'dopamine_deficit': 0.0, ...}

    Returns:
        (receptor_key, reason) tuple
        e.g., ('ache', 'acetylcholine deficit 0.60')
    """
    # Map NT deficits to receptors
    nt_to_receptor = {
        'acetylcholine': 'ache',
        'serotonin': 'sert',
        'dopamine': 'dat',
        'noradrenaline': 'sert',  # NET uses SERT as proxy
        'gaba': 'gaba_a',
    }

    # Find largest deficit (positive value)
    max_deficit = 0.0
    max_nt = None

    for nt, receptor in nt_to_receptor.items():
        deficit_key = f"{nt}_deficit"
        if deficit_key in disease_profile:
            deficit = disease_profile[deficit_key]

            # Only consider positive deficits (not excess)
            if deficit > max_deficit:
                max_deficit = deficit
                max_nt = nt

    if max_nt and max_deficit > 0.1:  # Threshold: 10% deficit
        receptor = nt_to_receptor[max_nt]
        reason = f"{max_nt} deficit {max_deficit:.2f}"

        # Check if receptor file exists
        if receptor in RECEPTOR_DATABASE:
            receptor_path = RECEPTOR_DATABASE[receptor]['file']
            if os.path.exists(receptor_path):
                print(f"[DOCKING] Auto-selected {RECEPTOR_DATABASE[receptor]['name']} "
                      f"({reason})")
                return receptor, reason
            else:
                print(f"[DOCKING] WARNING: {receptor} selected but file not found!")
                print(f"[DOCKING] Expected: {receptor_path}")

    # Fallback to AChE if available
    if 'ache' in RECEPTOR_DATABASE and os.path.exists(RECEPTOR_DATABASE['ache']['file']):
        print(f"[DOCKING] No clear target, using AChE as default")
        return 'ache', 'default fallback'

    print(f"[DOCKING] ERROR: No receptor files available!")
    return None, 'no receptors available'


def auto_select_receptor_from_targets(target_profile: Dict[str, float]) -> Tuple[Optional[str], str]:
    """
    Select receptor based on drug target profile.

    Looks at which mechanism has highest potency.

    Args:
        target_profile: Dict like {'ache_inhibition': 0.85, 'sert_inhibition': 0.3, ...}

    Returns:
        (receptor_key, reason) tuple
    """
    # Find receptor matching highest potency mechanism
    for mechanism, potency in sorted(target_profile.items(),
                                    key=lambda x: x[1],
                                    reverse=True):
        # Search all receptors for matching mechanism
        for receptor_key, receptor_info in RECEPTOR_DATABASE.items():
            if mechanism in receptor_info['mechanisms']:
                receptor_path = receptor_info['file']
                if os.path.exists(receptor_path):
                    reason = f"{mechanism} potency {potency:.2f}"
                    print(f"[DOCKING] Auto-selected {receptor_info['name']} ({reason})")
                    return receptor_key, reason
                else:
                    print(f"[DOCKING] WARNING: {receptor_key} matched but file not found!")

    # Fallback
    if 'ache' in RECEPTOR_DATABASE and os.path.exists(RECEPTOR_DATABASE['ache']['file']):
        return 'ache', 'default fallback'

    return None, 'no receptors available'


def smiles_to_pdbqt(smiles: str, output_path: str) -> bool:
    """Convert SMILES to PDBQT format for Vina."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return False

        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)

        pdb_path = output_path.replace('.pdbqt', '.pdb')
        Chem.MolToPDBFile(mol, pdb_path)

        cmd = ['obabel', pdb_path, '-O', output_path, '-h']
        subprocess.run(cmd, check=True, capture_output=True)

        os.remove(pdb_path)
        return True

    except Exception as e:
        print(f"[DOCKING] SMILES conversion failed: {e}")
        return False


def run_vina_docking(
    ligand_smiles: str,
    receptor_key: Optional[str] = None,
    disease_profile: Optional[Dict[str, float]] = None,
    target_profile: Optional[Dict[str, float]] = None,
    exhaustiveness: int = 8
) -> Optional[float]:
    """
    Run AutoDock Vina docking simulation.

    AUTO-SELECTS receptor from:
    1. receptor_key (if provided)
    2. disease_profile (uses largest deficit)
    3. target_profile (uses highest potency mechanism)

    Args:
        ligand_smiles: SMILES of ligand
        receptor_key: Explicit receptor ('ache', 'dat', 'sert', etc.)
        disease_profile: Disease NT profile for auto-selection
        target_profile: Drug target profile for auto-selection
        exhaustiveness: Search exhaustiveness (8 = default, 4 = fast)

    Returns:
        Binding affinity in kcal/mol (negative = better)
        None if docking failed
    """
    # Auto-select receptor
    if receptor_key is None:
        if disease_profile is not None:
            receptor_key, reason = auto_select_receptor_from_disease(disease_profile)
        elif target_profile is not None:
            receptor_key, reason = auto_select_receptor_from_targets(target_profile)
        else:
            print(f"[DOCKING] ERROR: Must provide receptor_key, disease_profile, or target_profile")
            return None

    if receptor_key is None:
        print(f"[DOCKING] ERROR: Could not auto-select receptor")
        return None

    # Get receptor info
    if receptor_key not in RECEPTOR_DATABASE:
        print(f"[DOCKING] ERROR: Unknown receptor '{receptor_key}'")
        return None

    receptor_info = RECEPTOR_DATABASE[receptor_key]
    receptor_path = receptor_info['file']

    if not os.path.exists(receptor_path):
        print(f"[DOCKING] ERROR: Receptor file not found: {receptor_path}")
        print(f"[DOCKING] Download with: python download_protein.py {receptor_info['pdb_id']}")
        return None

    try:
        # Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            ligand_pdbqt = os.path.join(tmpdir, "ligand.pdbqt")
            output_pdbqt = os.path.join(tmpdir, "output.pdbqt")
            log_file = os.path.join(tmpdir, "log.txt")

            # Convert SMILES to PDBQT
            if not smiles_to_pdbqt(ligand_smiles, ligand_pdbqt):
                return None

            # Run Vina
            cmd = [
                VINA_PATH,
                '--receptor', receptor_path,
                '--ligand', ligand_pdbqt,
                '--out', output_pdbqt,
                '--log', log_file,
                '--center_x', str(receptor_info['box_center'][0]),
                '--center_y', str(receptor_info['box_center'][1]),
                '--center_z', str(receptor_info['box_center'][2]),
                '--size_x', str(receptor_info['box_size'][0]),
                '--size_y', str(receptor_info['box_size'][1]),
                '--size_z', str(receptor_info['box_size'][2]),
                '--exhaustiveness', str(exhaustiveness),
                '--num_modes', '1'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Parse log for binding affinity
            with open(log_file, 'r') as f:
                log_content = f.read()

            for line in log_content.split('\n'):
                if line.strip().startswith('1'):
                    parts = line.split()
                    if len(parts) >= 2:
                        affinity = float(parts[1])
                        print(f"[DOCKING] {receptor_info['name']}: {affinity:.1f} kcal/mol")
                        return affinity

            return None

    except subprocess.TimeoutExpired:
        print(f"[DOCKING] Timeout")
        return None
    except Exception as e:
        print(f"[DOCKING] Error: {e}")
        return None


def affinity_to_score(affinity: float) -> float:
    """
    Convert binding affinity to fitness score (0-1).

    -5 → 0.0 (weak)
    -9 → 0.67 (good)
    -11 → 1.0 (strong)
    """
    affinity = abs(affinity)

    if affinity <= 5.0:
        return 0.0
    elif affinity >= 11.0:
        return 1.0
    else:
        return (affinity - 5.0) / 6.0


# Test
if __name__ == '__main__':
    print("="*60)
    print("TESTING AUTO-SELECTION")
    print("="*60)

    # Test 1: Alzheimer's (should select AChE)
    print("\n[TEST 1] Alzheimer's Disease")
    disease = {
        'serotonin_deficit': 0.15,
        'dopamine_deficit': 0.0,
        'acetylcholine_deficit': 0.60,  # ← Largest!
    }
    receptor, reason = auto_select_receptor_from_disease(disease)
    print(f"  Selected: {receptor} ({reason})")

    # Test 2: Depression (should select SERT)
    print("\n[TEST 2] Depression")
    disease = {
        'serotonin_deficit': 0.40,  # ← Largest!
        'dopamine_deficit': 0.30,
    }
    receptor, reason = auto_select_receptor_from_disease(disease)
    print(f"  Selected: {receptor} ({reason})")

    # Test 3: Parkinson's (should select DAT)
    print("\n[TEST 3] Parkinson's")
    disease = {
        'dopamine_deficit': 0.70,  # ← Largest!
    }
    receptor, reason = auto_select_receptor_from_disease(disease)
    print(f"  Selected: {receptor} ({reason})")

    print("\n" + "="*60)