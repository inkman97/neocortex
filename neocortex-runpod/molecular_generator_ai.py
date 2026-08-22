"""
MOLECULAR STRUCTURE GENERATOR - AI-Enhanced Version

Generates chemical structures (SMILES) from molecular target profiles.

Three Generation Modes:
1. AI-based: Uses pre-trained ChemGPT/MolGPT (best quality, slower)
2. Fragment-based: Rule-based assembly (fast, reliable)
3. Hybrid: AI + Fragment validation (recommended)

Author: NeoCortex Drug Discovery
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski
    from rdkit.Chem import AllChem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("[WARNING] RDKit not available. Install with: pip install rdkit")

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("[INFO] Transformers not available. Install with: pip install transformers torch")


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

    # Generation metadata
    generation_method: str = "unknown"  # "ai", "fragment", or "hybrid"

    def is_drug_like(self) -> bool:
        """Check if molecule passes Lipinski's Rule of 5 + BBB rules."""
        return self.lipinski_violations <= 1

    def is_cns_penetrant(self) -> bool:
        """
        Check if molecule can penetrate Blood-Brain Barrier.

        Based on:
        - Clark's BBB Rule: TPSA < 90 Å²
        - Lipinski: LogP 1-5, MW < 500
        - Veber: Rotatable bonds ≤ 10
        """
        return (
            self.tpsa <= 90 and
            self.molecular_weight <= 500 and
            1.0 <= self.logp <= 5.0 and
            self.rotatable_bonds <= 10
        )

    def is_synthesizable(self) -> bool:
        """Check if molecule is reasonably synthesizable."""
        return self.sa_score < 6.0  # SA score < 6 is reasonable

    def quality_score(self) -> float:
        """Overall quality score (0-1)."""
        drug_like_score = 1.0 if self.is_drug_like() else 0.5
        cns_score = 1.0 if self.is_cns_penetrant() else 0.6  # Penalize non-CNS
        synth_score = max(0, 1.0 - (self.sa_score / 10.0))
        return (
            self.qed_score * 0.4 +
            drug_like_score * 0.25 +
            cns_score * 0.2 +  # BBB penetration weight
            synth_score * 0.15
        )

    def get_bbb_assessment(self) -> Dict:
        """
        Detailed BBB penetration assessment.

        Returns dict with each criterion and overall prediction.
        """
        assessment = {
            'tpsa': {
                'value': self.tpsa,
                'limit': 90,
                'passes': self.tpsa <= 90,
                'note': 'Clark BBB Rule: TPSA < 90 Å² for CNS penetration'
            },
            'logp': {
                'value': self.logp,
                'optimal_range': [1.0, 5.0],
                'passes': 1.0 <= self.logp <= 5.0,
                'note': 'Optimal lipophilicity for BBB: LogP 1-5'
            },
            'mw': {
                'value': self.molecular_weight,
                'limit': 500,
                'passes': self.molecular_weight <= 500,
                'note': 'MW < 500 Da for passive diffusion'
            },
            'hbd': {
                'value': self.hbd,
                'limit': 5,
                'passes': self.hbd <= 5,
                'note': 'H-bond donors ≤ 5 (Lipinski)'
            },
            'rotatable_bonds': {
                'value': self.rotatable_bonds,
                'limit': 10,
                'passes': self.rotatable_bonds <= 10,
                'note': 'Veber Rule: Rotatable bonds ≤ 10'
            },
            'overall_cns_penetrant': self.is_cns_penetrant(),
            'confidence': 'high' if self.is_cns_penetrant() else 'low'
        }
        return assessment


# Pharmacophore fragments for fragment-based generation
PHARMACOPHORE_FRAGMENTS = {
    # Serotonin transporter (SERT) - SSRIs
    'sert_inhibition': [
        'c1ccc(OCCF)cc1',           # Fluorophenoxy (fluoxetine-like)
        'c1ccc(Cl)c(Cl)c1',         # Dichlorophenyl (sertraline-like)
        'c1ccccc1N',                # Phenylamine
        'C1CCNCC1',                 # Piperidine
        'c1ccc(CF3)cc1',            # Trifluoromethylphenyl
    ],

    # Dopamine transporter (DAT)
    'dat_inhibition': [
        'c1ccccc1C(=O)',            # Benzoyl (cocaine-like)
        'C1CCNCC1',                 # Piperidine
        'c1cc(Cl)ccc1',             # Chlorophenyl
        'c1ccc(OC)cc1',             # Methoxyphenyl
    ],

    # Norepinephrine transporter (NET)
    'net_inhibition': [
        'c1ccc(O)cc1',              # Phenol
        'NCCC',                     # Ethylamine
        'c1ccccc1',                 # Phenyl
        'c1ccc(CN)cc1',             # Benzylamine
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

    # GABA-A PAM
    'gaba_a_pam': [
        'c1ccc(Cl)cc1',             # Chlorophenyl
        'c1ccccc1',                 # Phenyl
        'C1=Nc2ccccc2C(=O)N1',      # Benzodiazepine-like
    ],

    # D2/D3 antagonist
    'd2_antagonism': [
        'C1CCN(C)CC1',              # N-methylpiperidine
        'c1ccc(F)cc1',              # Fluorophenyl
        'c1cc(Cl)ccc1',             # Chlorophenyl
    ],
    'd3_antagonism': [
        'C1CCN(C)CC1',
        'c1ccc(F)cc1',
        'c1ncccn1',                 # Pyrimidine
    ],

    # 5-HT receptor modulators
    'ht1a_agonism': [
        'c1ccccc1C',                # Tolyl
        'C1CCNCC1',                 # Piperidine
        'c1ccc(OC)cc1',             # Methoxyphenyl
    ],
    'ht2a_antagonism': [
        'c1ccccc1C',
        'C1CCNCC1',
        'c1ccc(OC)cc1',
    ],
}


class MolecularGenerator:
    """
    Generates molecular structures from target profiles.

    Three Generation Modes:
    1. AI-based: Uses pre-trained language model
    2. Fragment-based: Rule-based assembly
    3. Hybrid: Combines both approaches (recommended)

    BBB Filtering:
    All generated molecules are filtered for CNS penetration using:
    - Lipinski's Rule of 5
    - Clark's BBB Rule (TPSA < 90 Å²)
    - Veber's Rule (Rotatable bonds ≤ 10)
    """

    def __init__(self, use_ai: bool = True, mode: str = "hybrid"):
        """
        Initialize molecular generator.

        Args:
            use_ai: Try to use AI model if available
            mode: "ai", "fragment", or "hybrid" (default: hybrid)
        """
        self.mode = mode
        self.ai_available = False
        self.model = None
        self.tokenizer = None

        if use_ai and mode in ["ai", "hybrid"]:
            self.ai_available = self._check_ai_available()

            if self.ai_available:
                print(f"[MolGen] AI model available - Mode: {mode}")
                try:
                    self._load_ai_model()
                except Exception as e:
                    print(f"[MolGen] Failed to load AI model: {e}")
                    print(f"[MolGen] Falling back to fragment-based")
                    self.ai_available = False
                    self.mode = "fragment"
            else:
                print(f"[MolGen] AI libraries not available - Using fragment-based")
                self.mode = "fragment"
        else:
            print("[MolGen] Using fragment-based generation")
            self.mode = "fragment"

    def _check_ai_available(self) -> bool:
        """Check if AI generation is possible."""
        return AI_AVAILABLE

    def _load_ai_model(self):
        """
        Load pre-trained molecular generation model.

        Models available:
        - "ncfrey/ChemGPT-1.2B" (best, but large ~5GB)
        - "ncfrey/ChemGPT-4.7M" (smaller, faster)
        - "gpt2" (fallback, not specialized)
        """
        try:
            print("[MolGen] Loading AI model (this may take a few minutes)...")

            # Try ChemGPT first (best for molecules)
            model_name = "ncfrey/ChemGPT-4.7M"  # Smaller version

            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
                print(f"[MolGen] Loaded {model_name}")
            except Exception as e:
                print(f"[MolGen] ChemGPT not available: {e}")
                print(f"[MolGen] Trying GPT-2 as fallback...")

                # Fallback to GPT-2 (not specialized but works)
                self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
                self.model = AutoModelForCausalLM.from_pretrained("gpt2")
                print(f"[MolGen] Loaded GPT-2 (fallback)")

            # Move to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                print(f"[MolGen] Model on GPU")
            else:
                print(f"[MolGen] Model on CPU")

        except Exception as e:
            print(f"[MolGen] Failed to load AI model: {e}")
            raise

    def generate(
        self,
        target_profile: Dict[str, float],
        num_candidates: int = 10,
        force_method: Optional[str] = None,
        require_cns: bool = True
    ) -> List[Tuple[str, MolecularProperties]]:
        """
        Generate molecular structures for target profile.

        Args:
            target_profile: Dict of {target: potency}
            num_candidates: Number of structures to generate
            force_method: Override mode ("ai", "fragment", or None)
            require_cns: If True, only return BBB-penetrant molecules (default: True)

        Returns:
            List of (SMILES, properties) tuples sorted by quality
        """
        if not RDKIT_AVAILABLE:
            raise RuntimeError("RDKit required for molecular generation")

        method = force_method or self.mode

        print(f"\n[MolGen] Generating {num_candidates} candidates using '{method}' method")
        print(f"[MolGen] CNS penetration required: {require_cns}")

        if method == "ai" and self.ai_available:
            candidates = self._generate_ai(target_profile, num_candidates, require_cns)
        elif method == "hybrid" and self.ai_available:
            candidates = self._generate_hybrid(target_profile, num_candidates, require_cns)
        else:
            candidates = self._generate_fragment_based(target_profile, num_candidates, require_cns)

        # Final BBB report
        if candidates:
            cns_count = sum(1 for _, props in candidates if props.is_cns_penetrant())
            print(f"[MolGen] BBB Assessment: {cns_count}/{len(candidates)} candidates are CNS-penetrant")

        return candidates

    def _generate_ai(
        self,
        target_profile: Dict[str, float],
        num_candidates: int,
        require_cns: bool = True
    ) -> List[Tuple[str, MolecularProperties]]:
        """
        Generate using AI model (ChemGPT/GPT-2).

        Strategy:
        1. Create prompt describing desired properties
        2. Generate SMILES with language model
        3. Validate and filter
        4. Calculate properties
        5. Filter for BBB penetration if require_cns=True
        """
        print("[MolGen] Using AI generation...")

        # Create prompt
        prompt = self._create_prompt(target_profile)

        print(f"[MolGen] Prompt: {prompt[:100]}...")

        candidates = []
        attempts = 0
        max_attempts = num_candidates * 20  # More attempts to find CNS-penetrant

        while len(candidates) < num_candidates and attempts < max_attempts:
            attempts += 1

            try:
                # Generate SMILES
                smiles = self._generate_smiles_from_prompt(prompt)

                if smiles and self._is_valid_molecule(smiles):
                    # Calculate properties
                    props = self._calculate_properties(smiles)
                    props.generation_method = "ai"

                    # Filter for drug-likeness AND CNS penetration
                    if props.is_drug_like() and props.molecular_weight > 150:
                        if not require_cns or props.is_cns_penetrant():
                            candidates.append((smiles, props))

                            if len(candidates) % 5 == 0:
                                print(f"[MolGen] Generated {len(candidates)}/{num_candidates} valid candidates")
                        else:
                            # Log rejected for BBB
                            if attempts % 20 == 0:
                                print(f"[MolGen] Rejected (BBB): TPSA={props.tpsa:.1f}, LogP={props.logp:.2f}")

            except Exception as e:
                continue

        if not candidates:
            print("[MolGen] AI generation failed, falling back to fragments")
            return self._generate_fragment_based(target_profile, num_candidates, require_cns)

        # Sort by quality
        candidates.sort(key=lambda x: x[1].quality_score(), reverse=True)

        print(f"[MolGen] AI generated {len(candidates)} candidates")
        return candidates[:num_candidates]

    def _create_prompt(self, target_profile: Dict[str, float]) -> str:
        """Create text prompt for AI model."""
        # Sort targets by potency
        sorted_targets = sorted(
            target_profile.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Build prompt
        prompt = "Generate a drug-like molecule SMILES with the following properties:\n"

        for target, potency in sorted_targets[:5]:  # Top 5 targets
            if potency > 0.1:
                # Convert to human-readable
                target_name = target.replace('_', ' ').title()
                prompt += f"- {target_name}: {int(potency*100)}%\n"

        prompt += "\nSMILES: "

        return prompt

    def _generate_smiles_from_prompt(self, prompt: str) -> Optional[str]:
        """Generate single SMILES from prompt using AI model."""
        try:
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=200
            )

            if torch.cuda.is_available() and self.model.device.type == 'cuda':
                inputs = {k: v.cuda() for k, v in inputs.items()}

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=250,
                    do_sample=True,
                    temperature=0.8,
                    top_p=0.9,
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decode
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract SMILES (after "SMILES: ")
            if "SMILES:" in generated_text:
                smiles = generated_text.split("SMILES:")[-1].strip()
                # Clean up (take first line/word)
                smiles = smiles.split()[0].split('\n')[0]
                return smiles
            else:
                # Try to extract SMILES pattern
                words = generated_text.split()
                for word in words:
                    if self._looks_like_smiles(word):
                        return word

            return None

        except Exception as e:
            return None

    def _looks_like_smiles(self, text: str) -> bool:
        """Quick check if text looks like SMILES."""
        if not text or len(text) < 5:
            return False
        # SMILES typically contain c, C, N, O, parentheses, numbers
        smiles_chars = set('cCNOSnPFClBrI()[]=#-+123456789')
        return len(set(text) - smiles_chars) < 3  # Allow few non-SMILES chars

    def _generate_hybrid(
        self,
        target_profile: Dict[str, float],
        num_candidates: int,
        require_cns: bool = True
    ) -> List[Tuple[str, MolecularProperties]]:
        """
        Generate using hybrid approach: AI + Fragment validation.

        Strategy:
        1. Generate 70% with AI
        2. Generate 30% with fragments
        3. Combine and rank
        """
        print("[MolGen] Using hybrid generation (AI + Fragments)...")
        num_ai = int(num_candidates * 0.7)
        num_fragment = num_candidates - num_ai

        candidates = []

        # Generate with AI
        try:
            ai_candidates = self._generate_ai(target_profile, num_ai, require_cns)
            candidates.extend(ai_candidates)
        except Exception as e:
            print(f"[MolGen] AI generation failed: {e}")

        # Generate with fragments
        fragment_candidates = self._generate_fragment_based(target_profile, num_fragment, require_cns)
        candidates.extend(fragment_candidates)

        # Remove duplicates
        seen_smiles = set()
        unique_candidates = []
        for smiles, props in candidates:
            if smiles not in seen_smiles:
                seen_smiles.add(smiles)
                unique_candidates.append((smiles, props))

        # Sort by quality
        unique_candidates.sort(key=lambda x: x[1].quality_score(), reverse=True)

        print(f"[MolGen] Hybrid generated {len(unique_candidates)} unique candidates")
        return unique_candidates[:num_candidates]

    def _generate_fragment_based(
        self,
        target_profile: Dict[str, float],
        num_candidates: int,
        require_cns: bool = True
    ) -> List[Tuple[str, MolecularProperties]]:
        """
        Generate using fragment assembly (original method).

        Strategy:
        1. Select fragments based on target profile
        2. Connect fragments with linkers
        3. Validate structure
        4. Calculate properties
        5. Filter for BBB penetration
        """
        print("[MolGen] Using fragment-based generation...")

        candidates = []

        # Sort targets by potency
        sorted_targets = sorted(
            target_profile.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Generate diverse candidates
        for attempt in range(num_candidates * 10):  # More attempts for BBB filter
            try:
                smiles = self._assemble_molecule(sorted_targets, attempt)

                if smiles and self._is_valid_molecule(smiles):
                    props = self._calculate_properties(smiles)
                    props.generation_method = "fragment"

                    if props.is_drug_like():
                        # Check BBB if required
                        if not require_cns or props.is_cns_penetrant():
                            candidates.append((smiles, props))

                    if len(candidates) >= num_candidates:
                        break
            except Exception as e:
                continue

        # Sort by QED score
        candidates.sort(key=lambda x: x[1].qed_score, reverse=True)

        print(f"[MolGen] Fragment-based generated {len(candidates)} candidates")
        return candidates[:num_candidates]

    def _assemble_molecule(
        self,
        sorted_targets: List[Tuple[str, float]],
        seed: int
    ) -> str:
        """Assemble molecule from fragments."""
        np.random.seed(seed)

        fragments = []
        num_fragments = min(3, len(sorted_targets))

        for target, potency in sorted_targets[:num_fragments]:
            if potency < 0.1:
                continue

            available_frags = PHARMACOPHORE_FRAGMENTS.get(target, [])
            if available_frags:
                frag = np.random.choice(available_frags)
                fragments.append(frag)

        if not fragments:
            fragments = ['c1ccccc1', 'C1CCNCC1']

        # Linkers (shorter to keep MW and rotatable bonds low for BBB)
        linkers = ['C', 'CC', 'CN', 'CO', 'C(=O)']

        # Assemble
        if len(fragments) == 1:
            smiles = fragments[0]
        elif len(fragments) == 2:
            linker = np.random.choice(linkers)
            smiles = fragments[0] + linker + fragments[1]
        else:
            linker1 = np.random.choice(linkers)
            linker2 = np.random.choice(linkers)
            smiles = fragments[0] + linker1 + fragments[1] + linker2 + fragments[2]

        return smiles

    def _is_valid_molecule(self, smiles: str) -> bool:
        """Check if SMILES is valid."""
        try:
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except:
            return False

    def _calculate_properties(self, smiles: str) -> MolecularProperties:
        """
        Calculate molecular properties including BBB-relevant descriptors.

        BBB Criteria Applied:
        - Lipinski's Rule of 5 (MW, LogP, HBD, HBA)
        - Clark's BBB Rule (TPSA < 90 Å²)
        - Veber's Rule (Rotatable bonds ≤ 10)
        """
        mol = Chem.MolFromSmiles(smiles)

        mw = Descriptors.MolWt(mol)
        logp = Crippen.MolLogP(mol)
        hbd = Lipinski.NumHDonors(mol)
        hba = Lipinski.NumHAcceptors(mol)
        tpsa = Descriptors.TPSA(mol)
        rotatable = Lipinski.NumRotatableBonds(mol)
        aromatic = Lipinski.NumAromaticRings(mol)

        # ═══════════════════════════════════════════════════════════════
        # VIOLATIONS COUNT - NOW INCLUDES BBB RULES
        # ═══════════════════════════════════════════════════════════════
        violations = 0

        # Lipinski's Rule of 5
        if mw > 500:
            violations += 1      # MW < 500 Da
        if logp > 5:
            violations += 1      # LogP < 5
        if hbd > 5:
            violations += 1      # H-bond donors ≤ 5
        if hba > 10:
            violations += 1      # H-bond acceptors ≤ 10

        # Clark's BBB Rule
        if tpsa > 90:
            violations += 1      # TPSA < 90 Å² for CNS penetration

        # Veber's Rule (also helps oral bioavailability)
        if rotatable > 10:
            violations += 1      # Rotatable bonds ≤ 10
        # ═══════════════════════════════════════════════════════════════

        try:
            from rdkit.Chem import QED
            qed = QED.qed(mol)
        except:
            qed = 0.5

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
        """Estimate synthetic accessibility."""
        num_atoms = mol.GetNumAtoms()
        num_rings = Lipinski.NumAromaticRings(mol) + Lipinski.NumAliphaticRings(mol)
        num_rotatable = Lipinski.NumRotatableBonds(mol)

        complexity = (num_atoms / 30.0) + (num_rings * 0.5) + (num_rotatable * 0.3)
        sa_score = min(10, 1 + complexity)

        return sa_score


def generate_structure_for_drug(
    target_profile: Dict[str, float],
    num_candidates: int = 5,
    mode: str = "hybrid",
    require_cns: bool = True
) -> Dict:
    """
    Main function to generate molecular structure.

    Args:
        target_profile: Optimal target profile from GA
        num_candidates: Number of candidates to generate
        mode: "ai", "fragment", or "hybrid" (default)
        require_cns: If True, only return BBB-penetrant molecules (default: True)

    Returns:
        Dict with best structure and properties
    """
    if not RDKIT_AVAILABLE:
        return {
            'error': 'RDKit not available. Install with: pip install rdkit',
            'smiles': None,
        }

    # Initialize generator
    generator = MolecularGenerator(use_ai=True, mode=mode)

    print(f"\n[MolGen] Generating structures for target profile:")
    for target, potency in sorted(target_profile.items(), key=lambda x: x[1], reverse=True):
        if potency > 0.1:
            print(f"  {target}: {potency:.2f}")

    print(f"\n[MolGen] BBB/CNS penetration required: {require_cns}")

    # Generate candidates
    candidates = generator.generate(target_profile, num_candidates, require_cns=require_cns)

    if not candidates:
        return {
            'error': 'No valid structures generated (all failed BBB filter)' if require_cns else 'No valid structures generated',
            'smiles': None,
        }

    # Best candidate
    best_smiles, best_props = candidates[0]

    # Get BBB assessment
    bbb_assessment = best_props.get_bbb_assessment()

    print(f"\n[MolGen] Best structure found ({best_props.generation_method}):")
    print(f"  SMILES: {best_smiles}")
    print(f"  MW: {best_props.molecular_weight:.1f} Da")
    print(f"  LogP: {best_props.logp:.2f}")
    print(f"  TPSA: {best_props.tpsa:.1f} Å²")
    print(f"  HBD: {best_props.hbd}, HBA: {best_props.hba}")
    print(f"  Rotatable bonds: {best_props.rotatable_bonds}")
    print(f"  QED: {best_props.qed_score:.2f}")
    print(f"  SA Score: {best_props.sa_score:.1f}")
    print(f"  Quality Score: {best_props.quality_score():.2f}")
    print(f"  Lipinski + BBB violations: {best_props.lipinski_violations}")
    print(f"  Drug-like: {'[OK] Yes' if best_props.is_drug_like() else '[X] No'}")
    print(f"  CNS Penetrant (BBB): {'[OK] Yes' if best_props.is_cns_penetrant() else '[X] No'}")
    print(f"  Synthesizable: {'[OK] Yes' if best_props.is_synthesizable() else '[X] Difficult'}")

    return {
        'smiles': best_smiles,
        'generation_method': best_props.generation_method,
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
            'quality_score': best_props.quality_score(),
            'is_drug_like': best_props.is_drug_like(),
            'is_cns_penetrant': best_props.is_cns_penetrant(),
            'is_synthesizable': best_props.is_synthesizable(),
        },
        'bbb_assessment': bbb_assessment,
        'alternatives': [
            {
                'smiles': smiles,
                'method': props.generation_method,
                'qed': props.qed_score,
                'quality': props.quality_score(),
                'cns_penetrant': props.is_cns_penetrant(),
                'tpsa': props.tpsa,
            }
            for smiles, props in candidates[1:]
        ]
    }


# Example usage
if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         MOLECULAR GENERATOR WITH BBB FILTERING                 ║
    ║                                                                ║
    ║  BBB Rules Applied:                                            ║
    ║    [OK] Lipinski's Rule of 5 (MW, LogP, HBD, HBA)                ║
    ║    [OK] Clark's BBB Rule (TPSA < 90 Å²)                          ║
    ║    [OK] Veber's Rule (Rotatable bonds ≤ 10)                      ║
    ║                                                                ║
    ║  Only CNS-penetrant molecules pass the filter!                 ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # Example: SSRI-like profile for CNS drug
    target_profile = {
        'sert_inhibition': 0.85,
        'net_inhibition': 0.62,
        'dat_inhibition': 0.41,
    }

    # Test with BBB filtering
    print("\n" + "="*60)
    print("Testing with BBB filtering (require_cns=True)")
    print("="*60)

    result = generate_structure_for_drug(
        target_profile,
        num_candidates=5,
        mode="fragment",
        require_cns=True  # Only BBB-penetrant molecules
    )

    if result['smiles']:
        print(f"\n[OK] Generated CNS-penetrant molecule: {result['smiles']}")
        print(f"  BBB Assessment: {result['bbb_assessment']['overall_cns_penetrant']}")
    else:
        print(f"\n[X] Failed: {result.get('error')}")
