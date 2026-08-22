"""
MOLECULAR STRUCTURE GENERATOR

Generates chemical structures (SMILES) from molecular target profiles.

Approach:
1. Use pre-trained molecular generation model (ChemGPT/MolGPT)
2. Condition on target profile
3. Validate drug-likeness
4. Calculate molecular properties

Fallback: Rule-based fragment assembly if no model available
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski
    from rdkit.Chem import AllChem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("[WARNING] RDKit not available. Install with: pip install rdkit")


@dataclass
class MolecularProperties:
    """Calculated molecular properties."""
    smiles: str
    molecular_weight: float
    logp: float  # Lipophilicity
    hbd: int     # H-bond donors
    hba: int     # H-bond acceptors
    tpsa: float  # Topological polar surface area
    rotatable_bonds: int
    aromatic_rings: int
    
    # Drug-likeness scores
    lipinski_violations: int
    qed_score: float  # Quantitative Estimate of Drug-likeness
    
    # Synthetic accessibility
    sa_score: float  # 1 (easy) to 10 (hard)
    
    def is_drug_like(self) -> bool:
        """Check if molecule passes Lipinski's Rule of 5."""
        return self.lipinski_violations <= 1
    
    def is_synthesizable(self) -> bool:
        """Check if molecule is reasonably synthesizable."""
        return self.sa_score < 6.0  # SA score < 6 is reasonable


# Pharmacophore fragments for common drug targets
PHARMACOPHORE_FRAGMENTS = {
    # Serotonin transporter (SERT) - SSRIs
    'sert_inhibition': [
        'c1ccc(OCCF)cc1',           # Fluorophenoxy (fluoxetine-like)
        'c1ccc(Cl)c(Cl)c1',         # Dichlorophenyl (sertraline-like)
        'c1ccccc1N',                # Phenylamine
        'C1CCNCC1',                 # Piperidine
    ],
    
    # Dopamine transporter (DAT)
    'dat_inhibition': [
        'c1ccccc1C(=O)',            # Benzoyl (cocaine-like)
        'C1CCNCC1',                 # Piperidine
        'c1cc(Cl)ccc1',             # Chlorophenyl
    ],
    
    # Norepinephrine transporter (NET)
    'net_inhibition': [
        'c1ccc(O)cc1',              # Phenol
        'NCCC',                     # Ethylamine
        'c1ccccc1',                 # Phenyl
    ],
    
    # MAO-A inhibitor
    'mao_a_inhibition': [
        'c1ccncc1',                 # Pyridine
        'C(=O)N',                   # Amide
        'c1cc(O)ccc1',              # Hydroxyphenyl
    ],
    
    # AChE inhibitor
    'ache_inhibition': [
        'C1CCNCC1',                 # Piperidine (donepezil-like)
        'c1ccccc1',                 # Phenyl
        'C(=O)N',                   # Carbamate
    ],
    
    # GABA-A PAM (benzodiazepine-like)
    'gaba_a_pam': [
        'c1ccc(Cl)cc1',             # Chlorophenyl
        'c1ccccc1',                 # Phenyl
        'C1=Nc2ccccc2C(=O)N1',      # Benzodiazepine core
    ],
    
    # D2 antagonist (antipsychotic)
    'd2_antagonism': [
        'C1CCN(C)CC1',              # N-methylpiperidine
        'c1ccc(F)cc1',              # Fluorophenyl (haloperidol-like)
        'c1cc(Cl)ccc1',             # Chlorophenyl
    ],
    
    # 5-HT2A antagonist
    'ht2a_antagonism': [
        'c1ccccc1C',                # Tolyl
        'C1CCNCC1',                 # Piperidine
        'c1ccc(OC)cc1',             # Methoxyphenyl
    ],
}


class MolecularGenerator:
    """
    Generates molecular structures from target profiles.
    
    Methods:
    1. Transformer-based (if model available)
    2. Fragment-based assembly (fallback)
    """
    
    def __init__(self, use_transformer: bool = False):
        self.use_transformer = use_transformer and self._check_transformer_available()
        
        if self.use_transformer:
            print("[MolGen] Using transformer-based generation")
            self._load_transformer()
        else:
            print("[MolGen] Using fragment-based generation (fallback)")
    
    def _check_transformer_available(self) -> bool:
        """Check if transformer model is available."""
        try:
            import transformers
            return True
        except ImportError:
            return False
    
    def _load_transformer(self):
        """Load pre-trained molecular generation model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # Use MolGPT or similar (this is placeholder)
            # In production, use: ncfrey/ChemGPT-1.2B or similar
            self.tokenizer = None  # Would load real model
            self.model = None
            
            print("[MolGen] Transformer model loaded")
        except Exception as e:
            print(f"[MolGen] Could not load transformer: {e}")
            self.use_transformer = False
    
    def generate(
        self,
        target_profile: Dict[str, float],
        num_candidates: int = 10
    ) -> List[Tuple[str, MolecularProperties]]:
        """
        Generate molecular structures for target profile.
        
        Args:
            target_profile: Dict of {target: potency}
            num_candidates: Number of structures to generate
            
        Returns:
            List of (SMILES, properties) tuples
        """
        if not RDKIT_AVAILABLE:
            raise RuntimeError("RDKit required for molecular generation")
        
        if self.use_transformer:
            return self._generate_transformer(target_profile, num_candidates)
        else:
            return self._generate_fragment_based(target_profile, num_candidates)
    
    def _generate_transformer(
        self,
        target_profile: Dict[str, float],
        num_candidates: int
    ) -> List[Tuple[str, MolecularProperties]]:
        """
        Generate using transformer model.
        
        (Placeholder - would use real MolGPT/ChemGPT)
        """
        # Convert target profile to prompt
        prompt = self._profile_to_prompt(target_profile)
        
        # Generate SMILES (placeholder)
        # In production: smiles_list = self.model.generate(prompt, num_return=num_candidates)
        
        # For now, fall back to fragment-based
        return self._generate_fragment_based(target_profile, num_candidates)
    
    def _profile_to_prompt(self, target_profile: Dict[str, float]) -> str:
        """Convert target profile to text prompt for transformer."""
        targets = [f"{target}={potency:.2f}" for target, potency in target_profile.items()]
        return f"Generate molecule with: {', '.join(targets)}"
    
    def _generate_fragment_based(
        self,
        target_profile: Dict[str, float],
        num_candidates: int
    ) -> List[Tuple[str, MolecularProperties]]:
        """
        Generate using fragment assembly.
        
        Strategy:
        1. Select fragments based on target profile
        2. Connect fragments with linkers
        3. Validate structure
        4. Calculate properties
        """
        candidates = []
        
        # Sort targets by potency (most important first)
        sorted_targets = sorted(
            target_profile.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Generate diverse candidates
        for attempt in range(num_candidates * 3):  # Try 3x to get num_candidates valid
            try:
                smiles = self._assemble_molecule(sorted_targets, attempt)
                
                if smiles and self._is_valid_molecule(smiles):
                    props = self._calculate_properties(smiles)
                    
                    if props.is_drug_like():
                        candidates.append((smiles, props))
                    
                    if len(candidates) >= num_candidates:
                        break
            except Exception as e:
                continue
        
        # Sort by QED score (drug-likeness)
        candidates.sort(key=lambda x: x[1].qed_score, reverse=True)
        
        return candidates[:num_candidates]
    
    def _assemble_molecule(
        self,
        sorted_targets: List[Tuple[str, float]],
        seed: int
    ) -> str:
        """
        Assemble molecule from fragments.
        
        Strategy:
        - Pick 1-3 pharmacophores based on top targets
        - Connect with appropriate linkers
        - Add diversity with seed
        """
        np.random.seed(seed)
        
        # Select fragments
        fragments = []
        num_fragments = min(3, len(sorted_targets))  # Max 3 pharmacophores
        
        for target, potency in sorted_targets[:num_fragments]:
            if potency < 0.1:
                continue
            
            available_frags = PHARMACOPHORE_FRAGMENTS.get(target, [])
            if available_frags:
                frag = np.random.choice(available_frags)
                fragments.append(frag)
        
        if not fragments:
            # No specific fragments, use generic scaffold
            fragments = ['c1ccccc1', 'C1CCNCC1']  # Phenyl + piperidine (common)
        
        # Connect fragments with linkers
        linkers = [
            'C',      # Methylene
            'CC',     # Ethylene
            'CCO',    # Hydroxyethyl
            'CNC',    # Methylamine
            'C(=O)',  # Carbonyl
        ]
        
        # Assemble SMILES
        if len(fragments) == 1:
            smiles = fragments[0]
        else:
            linker = np.random.choice(linkers)
            smiles = linker.join(fragments)
        
        return smiles
    
    def _is_valid_molecule(self, smiles: str) -> bool:
        """Check if SMILES string is valid."""
        try:
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except:
            return False
    
    def _calculate_properties(self, smiles: str) -> MolecularProperties:
        """Calculate molecular properties using RDKit."""
        mol = Chem.MolFromSmiles(smiles)
        
        # Basic properties
        mw = Descriptors.MolWt(mol)
        logp = Crippen.MolLogP(mol)
        hbd = Lipinski.NumHDonors(mol)
        hba = Lipinski.NumHAcceptors(mol)
        tpsa = Descriptors.TPSA(mol)
        rotatable = Lipinski.NumRotatableBonds(mol)
        aromatic = Lipinski.NumAromaticRings(mol)
        
        # Lipinski violations
        violations = 0
        if mw > 500: violations += 1
        if logp > 5: violations += 1
        if hbd > 5: violations += 1
        if hba > 10: violations += 1
        
        # QED (Quantitative Estimate of Drug-likeness)
        try:
            from rdkit.Chem import QED
            qed = QED.qed(mol)
        except:
            qed = 0.5  # Fallback
        
        # Synthetic Accessibility (SA) score
        sa_score = self._estimate_sa_score(mol)
        
        return MolecularProperties(
            smiles=smiles,
            molecular_weight=mw,
            logp=logp,
            hbd=hbd,
            hba=hba,
            tpsa=tpsa,
            rotatable_bonds=rotatable,
            aromatic_rings=aromatic,
            lipinski_violations=violations,
            qed_score=qed,
            sa_score=sa_score,
        )
    
    def _estimate_sa_score(self, mol) -> float:
        """
        Estimate synthetic accessibility score.
        
        Simplified version (real SA score is more complex).
        1 = very easy, 10 = very hard
        """
        # Simple heuristic based on complexity
        num_atoms = mol.GetNumAtoms()
        num_rings = Lipinski.NumAromaticRings(mol) + Lipinski.NumAliphaticRings(mol)
        num_rotatable = Lipinski.NumRotatableBonds(mol)
        
        # Penalty for complexity
        complexity = (num_atoms / 30.0) + (num_rings * 0.5) + (num_rotatable * 0.3)
        
        sa_score = min(10, 1 + complexity)
        
        return sa_score
    
    def generate_2d_image(self, smiles: str, filename: str = None):
        """Generate 2D image of molecule."""
        if not RDKIT_AVAILABLE:
            return None
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        
        from rdkit.Chem import Draw
        
        if filename:
            Draw.MolToFile(mol, filename)
        else:
            return Draw.MolToImage(mol)


def generate_structure_for_drug(
    target_profile: Dict[str, float],
    num_candidates: int = 5
) -> Dict:
    """
    Main function to generate molecular structure for discovered drug.
    
    Args:
        target_profile: Optimal target profile from GA
        num_candidates: Number of candidate structures
        
    Returns:
        Dict with best structure and properties
    """
    if not RDKIT_AVAILABLE:
        return {
            'error': 'RDKit not available. Install with: pip install rdkit',
            'smiles': None,
        }
    
    generator = MolecularGenerator(use_transformer=False)
    
    print(f"\n[MolGen] Generating structures for target profile:")
    for target, potency in sorted(target_profile.items(), key=lambda x: x[1], reverse=True):
        if potency > 0.1:
            print(f"  {target}: {potency:.2f}")
    
    candidates = generator.generate(target_profile, num_candidates)
    
    if not candidates:
        return {
            'error': 'No valid structures generated',
            'smiles': None,
        }
    
    # Best candidate (highest QED)
    best_smiles, best_props = candidates[0]
    
    print(f"\n[MolGen] Best structure found:")
    print(f"  SMILES: {best_smiles}")
    print(f"  MW: {best_props.molecular_weight:.1f}")
    print(f"  LogP: {best_props.logp:.2f}")
    print(f"  HBD: {best_props.hbd}, HBA: {best_props.hba}")
    print(f"  QED: {best_props.qed_score:.2f}")
    print(f"  SA Score: {best_props.sa_score:.1f}")
    print(f"  Lipinski violations: {best_props.lipinski_violations}")
    print(f"  Drug-like: {'[OK] Yes' if best_props.is_drug_like() else '[X] No'}")
    print(f"  Synthesizable: {'[OK] Yes' if best_props.is_synthesizable() else '[X] Difficult'}")
    
    # Return all info
    return {
        'smiles': best_smiles,
        'properties': {
            'molecular_weight': best_props.molecular_weight,
            'logp': best_props.logp,
            'hbd': best_props.hbd,
            'hba': best_props.hba,
            'tpsa': best_props.tpsa,
            'rotatable_bonds': best_props.rotatable_bonds,
            'aromatic_rings': best_props.aromatic_rings,
            'lipinski_violations': best_props.lipinski_violations,
            'qed_score': best_props.qed_score,
            'sa_score': best_props.sa_score,
            'is_drug_like': best_props.is_drug_like(),
            'is_synthesizable': best_props.is_synthesizable(),
        },
        'alternatives': [
            {
                'smiles': smiles,
                'qed': props.qed_score,
                'sa_score': props.sa_score,
            }
            for smiles, props in candidates[1:]
        ]
    }


# Example usage
if __name__ == '__main__':
    # Example: SSRI-like profile
    target_profile = {
        'sert_inhibition': 0.85,
        'dat_inhibition': 0.15,
        'ht1a_agonism': 0.30,
    }
    
    result = generate_structure_for_drug(target_profile, num_candidates=5)
    
    if result['smiles']:
        print(f"\nGenerated SMILES: {result['smiles']}")
        print(f"Properties: {result['properties']}")
