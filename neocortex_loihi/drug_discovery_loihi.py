"""
DRUG DISCOVERY ENGINE - Genetic Algorithm for Inverse Pharmacology

Finds optimal drug for a given disease by:
1. Generating population of random drug candidates
2. Evaluating fitness with NeoCortex simulation
3. Selecting best performers
4. Crossover + mutation to create new generation
5. Repeat until convergence

FULLY EMERGENT: Drug efficacy emerges from brain simulation, not hardcoded.
"""

import numpy as np
import random
from typing import List, Dict, Tuple
from dataclasses import dataclass
from drug_simulator_loihi import DrugMechanism, Pharmacokinetics, DiseaseProfile, DrugSimulator
import requests
try:
    from docking_utils import run_vina_docking, affinity_to_score
    DOCKING_AVAILABLE = True
    print("[GA] Docking available - will use binding affinity in fitness")
except ImportError:
    DOCKING_AVAILABLE = False
    print("[GA] Docking NOT available - using NT correction only")


CONVERGENCE_FITNESS = 0.95
PROGRESS_REPORT_TIMEOUT_S = 1


@dataclass
class OptimizationConfig:
    """Configuration for genetic algorithm."""
    iterations: int = 100
    population_size: int = 50
    mutation_rate: float = 0.15
    crossover_rate: float = 0.7
    elite_count: int = 5
    selection_method: str = "tournament"
    
    # Fitness weights
    weight_nt_correction: float = 0.6
    weight_side_effects: float = 0.2
    weight_complexity: float = 0.1
    weight_speed: float = 0.1
    weight_docking: float = 0.0

    # Docking params
    use_docking: bool = False
    docking_exhaustiveness: int = 8
    
    # Constraints
    max_targets: int = 5
    min_potency: float = 0.1
    max_potency: float = 1.0
    
    # Simulation params
    trial_duration: int = 168  # 1 week
    sampling_interval: int = 24  # Daily


# All possible molecular targets (matches DrugMechanism parameters)
ALL_TARGETS = [
    # Reuptake inhibitors
    'sert_inhibition',
    'dat_inhibition',
    'net_inhibition',
    'gat_inhibition',
    
    # Enzyme inhibitors
    'mao_a_inhibition',
    'mao_b_inhibition',
    'ache_inhibition',
    'gaba_transaminase_inhibition',
    
    # Precursors
    'da_precursor',
    
    # Receptor agonists
    'd2_agonism',
    'd3_agonism',
    'ht1a_agonism',
    
    # Receptor antagonists
    'd2_antagonism',
    'd3_antagonism',
    'ht2a_antagonism',
    'alpha2_antagonism',
    'h1_antagonism',
    
    # Partial agonists
    'd2_partial_agonism',
    
    # GABA/Glutamate modulators
    'gaba_a_pam',
    'nmda_antagonism',
    'glutamate_release_inhibition',
    'voltage_gated_sodium_blocker',
    'alpha2delta_blocker',
]


class DrugCandidate:
    """Represents a candidate drug in the genetic algorithm."""
    
    def __init__(self, targets: Dict[str, float] = None):
        if targets is None:
            # Random initialization
            num_targets = random.randint(1, 5)
            selected_targets = random.sample(ALL_TARGETS, num_targets)
            self.targets = {
                target: random.uniform(0.3, 1.0)
                for target in selected_targets
            }
        else:
            self.targets = targets
        
        self.fitness = 0.0
        self.trial_results = None
    
    def to_drug_mechanism(self) -> DrugMechanism:
        """Convert to DrugMechanism for simulation."""
        params = {target: 0.0 for target in ALL_TARGETS}
        params.update(self.targets)
        return DrugMechanism(**params)
    
    def get_active_targets(self) -> List[Tuple[str, float]]:
        """Get list of active targets sorted by potency."""
        return sorted(self.targets.items(), key=lambda x: x[1], reverse=True)
    
    def complexity(self) -> float:
        """Drug complexity (number of targets)."""
        return len(self.targets) / 10.0  # Normalize to 0-1
    
    def __repr__(self):
        targets_str = ', '.join([f"{t}:{p:.2f}" for t, p in list(self.targets.items())[:3]])
        return f"DrugCandidate({targets_str}..., fitness={self.fitness:.3f})"


class FitnessEvaluator:
    """Evaluates fitness of drug candidates using NeoCortex simulation."""
    
    def __init__(self, brain, disease_profile: DiseaseProfile, config: OptimizationConfig):
        self.brain = brain
        self.disease_profile = disease_profile
        self.config = config

        print(f"[FITNESS EVALUATOR] Applying disease profile to brain...")
        print(f"  5HT:  {disease_profile.serotonin_deficit:+.2f}")
        print(f"  DA:   {disease_profile.dopamine_deficit:+.2f}")
        print(f"  NE:   {disease_profile.noradrenaline_deficit:+.2f}")
        print(f"  ACh:  {disease_profile.acetylcholine_deficit:+.2f}")
        print(f"  GABA: {disease_profile.gaba_deficit:+.2f}")
        print(f"  Glu:  {disease_profile.glutamate_deficit:+.2f}")

        # Apply disease
        self.brain.neuromodulation.set_disease_state(disease_profile)

        # Recreate embodiment
        from embodiment import Embodiment
        disease_state = {
            'serotonin': disease_profile.serotonin_deficit,
            'dopamine': disease_profile.dopamine_deficit,
            'noradrenaline': disease_profile.noradrenaline_deficit,
            'acetylcholine': disease_profile.acetylcholine_deficit,
            'gaba': disease_profile.gaba_deficit,
            'glutamate': disease_profile.glutamate_deficit
        }
        self.brain.embodiment = Embodiment(disease_state=disease_state)

        # Warmup to reach steady-state
        print(f"[FITNESS EVALUATOR] Running warmup to establish diseased baseline...")
        warmup_steps = 2000
        for step in range(warmup_steps):
            if step % 500 == 0:
                nm = self.brain.neuromodulation
                print(f"  Step {step}/{warmup_steps}: "
                      f"5HT={nm.serotonin:.3f}, "
                      f"DA={nm.dopamine:.3f}, "
                      f"NE={nm.noradrenaline:.3f}, "
                      f"ACh={nm.acetylcholine:.3f}, "
                      f"GABA={nm.gaba:.3f}, "
                      f"Glu={nm.glutamate:.3f}")

            pattern = np.random.rand(100) * 0.3
            self.brain.perceive(pattern)
            self.brain.step()

        print(f"[FITNESS EVALUATOR] Warmup complete")

        # Store baseline after warmup
        self.baseline_nt = self._get_nt_levels()

        print(f"[FITNESS EVALUATOR] Baseline NT levels:")
        for nt, value in self.baseline_nt.items():
            print(f"  {nt}: {value:.3f}")

    def _reset_brain_to_baseline(self):
        """
        Reset brain to diseased baseline state before each drug evaluation.

        CRITICAL: Prevents state pollution between candidates.
        Drug trials (run_gpu.py) don't need this because they evaluate one drug at a time.
        """
        nm = self.brain.neuromodulation

        # Reset efficacy (reapply disease)
        nm.serotonin_efficacy = 1.0 - self.disease_profile.serotonin_deficit
        nm.dopamine_efficacy = 1.0 - self.disease_profile.dopamine_deficit
        nm.noradrenaline_efficacy = 1.0 - self.disease_profile.noradrenaline_deficit
        nm.acetylcholine_efficacy = 1.0 - self.disease_profile.acetylcholine_deficit
        nm.gaba_efficacy = 1.0 - self.disease_profile.gaba_deficit
        nm.glutamate_efficacy = 1.0 - self.disease_profile.glutamate_deficit

        # Reset reuptake
        nm.serotonin_reuptake = 1.0
        nm.dopamine_reuptake = 1.0
        nm.noradrenaline_reuptake = 1.0
        nm.gaba_reuptake = 1.0
        nm.glutamate_reuptake = 1.0

        # Reset clearance rates
        nm.baseline_clearance_5ht = nm.baseline_clearance_5ht_initial
        nm.baseline_clearance_da = nm.baseline_clearance_da_initial
        nm.baseline_clearance_ne = nm.baseline_clearance_ne_initial
        nm.baseline_clearance_ach = nm.baseline_clearance_ach_initial
        nm.baseline_clearance_gaba = nm.baseline_clearance_gaba_initial
        nm.baseline_clearance_glu = nm.baseline_clearance_glu_initial

        # Reset release rates
        nm.release_5ht = nm.baseline_release_5ht
        nm.release_da = nm.baseline_release_da
        nm.release_ne = nm.baseline_release_ne
        nm.release_ach = nm.baseline_release_ach
        nm.release_gaba = nm.baseline_release_gaba
        nm.release_glu = nm.baseline_release_glu

        # Recreate embodiment
        from embodiment import Embodiment
        disease_state = {
            'serotonin': self.disease_profile.serotonin_deficit,
            'dopamine': self.disease_profile.dopamine_deficit,
            'noradrenaline': self.disease_profile.noradrenaline_deficit,
            'acetylcholine': self.disease_profile.acetylcholine_deficit,
            'gaba': self.disease_profile.gaba_deficit,
            'glutamate': self.disease_profile.glutamate_deficit
        }
        self.brain.embodiment = Embodiment(disease_state=disease_state)

        # Quick warmup (100 steps to stabilize)
        for _ in range(100):
            pattern = np.random.rand(100) * 0.3
            self.brain.perceive(pattern)
            self.brain.step()

    def _get_nt_levels(self) -> Dict[str, float]:
        """Get current NT levels from brain."""
        nm = self.brain.neuromodulation
        return {
            'serotonin': nm.serotonin,
            'dopamine': nm.dopamine,
            'noradrenaline': nm.noradrenaline,
            'acetylcholine': nm.acetylcholine,
            'gaba': nm.gaba,
            'glutamate': nm.glutamate,
        }
    
    def evaluate(self, candidate: DrugCandidate) -> float:
        """
        Evaluate fitness of a drug candidate.
        
        Fitness components:
        1. NT Correction: How well it normalizes NT deficits
        2. Side Effects: Penalize overshooting or unnecessary changes
        3. Complexity: Prefer simpler drugs (fewer targets)
        4. Speed: Prefer faster-acting drugs
        """
        self._reset_brain_to_baseline()

        # Run simulation
        drug_mechanism = candidate.to_drug_mechanism()
        
        # Use simplified PK for optimization (all drugs assumed similar)
        pk = Pharmacokinetics(
            halfLife_hours=24.0,
            tmax_hours=2.0,
            bioavailability=0.7
        )
        
        simulator = DrugSimulator(
            brain=self.brain,
            drug_mechanism=drug_mechanism,
            disease_profile=self.disease_profile,
            pharmacokinetics=pk  # ← Fixed: use 'pharmacokinetics' not 'pk'
        )
        
        # Run short trial
        results = simulator.run_trial(
            dose_mg=100,  # Standard dose
            typical_dose_mg=100,
            duration_hours=self.config.trial_duration,
            sampling_interval_hours=self.config.sampling_interval
        )
        
        candidate.trial_results = results
        
        # Calculate fitness components
        nt_correction_score = self._calculate_nt_correction(results)
        side_effects_score = self._calculate_side_effects(results)
        complexity_score = 1.0 - candidate.complexity()
        speed_score = self._calculate_speed(results)
        docking_score = 0.0
        if self.config.use_docking and DOCKING_AVAILABLE:
            docking_score = self._calculate_docking_score(candidate)
        
        # Weighted sum
        fitness = (
            self.config.weight_nt_correction * nt_correction_score +
            self.config.weight_side_effects * side_effects_score +
            self.config.weight_complexity * complexity_score +
            self.config.weight_speed * speed_score +
            self.config.weight_docking * docking_score
        )
        
        candidate.fitness = fitness
        return fitness
    
    def _calculate_nt_correction(self, results: List[Dict]) -> float:
        """
        Score how well the drug corrects NT deficits.
        
        For each NT:
        - If deficit: reward increase toward 1.0 (normal)
        - If excess: reward decrease toward 1.0 (normal)
        - Penalize overcorrection
        """
        final_state = results[-1]  # End of trial
        
        score = 0.0
        num_deficits = 0
        
        # Check each NT
        for nt_name in ['serotonin', 'dopamine', 'noradrenaline', 'acetylcholine', 'gaba', 'glutamate']:
            deficit = getattr(self.disease_profile, f"{nt_name}_deficit")
            
            if abs(deficit) < 0.05:
                continue  # No deficit, skip
            
            num_deficits += 1
            
            baseline = self.baseline_nt[nt_name]
            final = final_state[nt_name]
            target = 1.0  # Normal level
            
            # How much did we correct toward target?
            baseline_error = abs(baseline - target)
            final_error = abs(final - target)
            
            improvement = (baseline_error - final_error) / baseline_error if baseline_error > 0 else 0
            
            # Penalize overcorrection (going past target)
            if (baseline < target and final > target) or (baseline > target and final < target):
                overcorrection_penalty = abs(final - target) / abs(baseline - target)
                improvement -= overcorrection_penalty * 0.5
            
            score += max(0, improvement)
        
        return score / max(1, num_deficits)  # Normalize by number of deficits
    
    def _calculate_side_effects(self, results: List[Dict]) -> float:
        """
        Penalize side effects:
        - Changes to NT systems that weren't deficient
        - Overshooting targets
        """
        final_state = results[-1]
        
        penalty = 0.0
        
        for nt_name in ['serotonin', 'dopamine', 'noradrenaline', 'acetylcholine', 'gaba', 'glutamate']:
            deficit = getattr(self.disease_profile, f"{nt_name}_deficit")
            
            if abs(deficit) < 0.05:
                # This NT was normal, any change is a side effect
                baseline = self.baseline_nt[nt_name]
                final = final_state[nt_name]
                change = abs(final - baseline)
                penalty += change * 0.5
        
        return max(0, 1.0 - penalty)
    
    def _calculate_speed(self, results: List[Dict]) -> float:
        """
        Reward faster-acting drugs.
        Measured as: how quickly NT levels normalize.
        """
        # Find when 50% correction is achieved
        for idx, timepoint in enumerate(results):
            if idx == 0:
                continue  # Skip baseline

            # Check if at least one major deficit is 50% corrected
            correction_50 = False

            for nt_name in ['serotonin', 'dopamine', 'noradrenaline', 'acetylcholine', 'gaba', 'glutamate']:
                deficit = getattr(self.disease_profile, f"{nt_name}_deficit")
                if abs(deficit) > 0.1:
                    baseline = self.baseline_nt[nt_name]
                    current = timepoint[nt_name]
                    target = 1.0

                    correction_ratio = (current - baseline) / (target - baseline) if target != baseline else 0
                    if correction_ratio >= 0.5:
                        correction_50 = True
                        break

            if correction_50:
                # Earlier is better
                days = timepoint['days']
                max_days = self.config.trial_duration / 24
                speed_score = 1.0 - (days / max_days)
                return max(0, speed_score)

        return 0.0
    def _calculate_docking_score(self, candidate: DrugCandidate) -> float:
        """
        Calculate docking score using AutoDock Vina.

        AUTO-SELECTS receptor based on disease profile!

        Returns:
            Fitness score 0-1 based on binding affinity
        """
        try:
            # Generate SMILES for candidate
            from molecular_generator_ai import generate_structure_for_drug

            target_profile = dict(candidate.targets)
            structure_result = generate_structure_for_drug(
                target_profile,
                num_candidates=1,
                mode="fragment"  # Fast generation
            )

            if 'error' in structure_result or not structure_result.get('smiles'):
                print(f"[DOCKING] Could not generate SMILES, returning 0")
                return 0.0

            smiles = structure_result['smiles']

            # Run docking with AUTO-SELECTION based on disease!
            affinity = run_vina_docking(
                ligand_smiles=smiles,
                disease_profile=self.disease_profile.__dict__,  # Pass disease for auto-selection
                exhaustiveness=self.config.docking_exhaustiveness
            )

            if affinity is None:
                print(f"[DOCKING] Docking failed, returning 0")
                return 0.0

            # Convert to score
            score = affinity_to_score(affinity)

            print(f"[DOCKING] SMILES: {smiles[:40]}...")
            print(f"[DOCKING] Affinity: {affinity:.1f} kcal/mol, Score: {score:.3f}")

            return score

        except Exception as e:
            print(f"[DOCKING] Error: {e}")
            return 0.0

class GeneticAlgorithm:
    """Genetic Algorithm for drug discovery."""
    
    def __init__(
        self,
        brain,
        disease_profile: DiseaseProfile,
        config: OptimizationConfig,
        job_id= None
    ):
        self.brain = brain
        self.disease_profile = disease_profile
        self.config = config
        self.evaluator = FitnessEvaluator(brain, disease_profile, config)
        
        self.population: List[DrugCandidate] = []
        self.best_candidate: DrugCandidate = None
        self.fitness_history: List[Dict] = []
        self.job_id = job_id
        self.java_url = "http://localhost:8080"
    
    def initialize_population(self):
        """Create initial random population."""
        print(f"[GA] Initializing population of {self.config.population_size} candidates...")
        self.population = [DrugCandidate() for _ in range(self.config.population_size)]
    
    def evaluate_population(self):
        """Evaluate fitness of all candidates."""
        print(f"[GA] Evaluating {len(self.population)} candidates...")
        for idx, candidate in enumerate(self.population):
            if candidate.fitness == 0.0:  # Not yet evaluated
                fitness = self.evaluator.evaluate(candidate)
                if idx % 10 == 0:
                    print(f"  Candidate {idx+1}/{len(self.population)}: fitness = {fitness:.3f}")
    
    def select_parents(self, k: int = 5) -> List[DrugCandidate]:
        """Tournament selection."""
        tournament = random.sample(self.population, k)
        tournament.sort(key=lambda x: x.fitness, reverse=True)
        return tournament[:2]
    
    def crossover(self, parent1: DrugCandidate, parent2: DrugCandidate) -> DrugCandidate:
        """Single-point crossover of drug targets."""
        if random.random() > self.config.crossover_rate:
            return DrugCandidate(targets=dict(parent1.targets))
        
        # Combine targets from both parents
        all_targets = set(parent1.targets.keys()) | set(parent2.targets.keys())
        child_targets = {}
        
        for target in all_targets:
            if target in parent1.targets and target in parent2.targets:
                # Both have it, average potencies
                child_targets[target] = (parent1.targets[target] + parent2.targets[target]) / 2
            elif target in parent1.targets:
                # Only parent1 has it, 50% chance to inherit
                if random.random() < 0.5:
                    child_targets[target] = parent1.targets[target]
            else:
                # Only parent2 has it, 50% chance to inherit
                if random.random() < 0.5:
                    child_targets[target] = parent2.targets[target]
        
        # Enforce max_targets constraint
        if len(child_targets) > self.config.max_targets:
            # Keep highest potency targets
            sorted_targets = sorted(child_targets.items(), key=lambda x: x[1], reverse=True)
            child_targets = dict(sorted_targets[:self.config.max_targets])
        
        return DrugCandidate(targets=child_targets)
    
    def mutate(self, candidate: DrugCandidate):
        """Mutate drug candidate."""
        if random.random() > self.config.mutation_rate:
            return
        
        mutation_type = random.choice(['add', 'remove', 'modify'])
        
        if mutation_type == 'add' and len(candidate.targets) < self.config.max_targets:
            # Add new target
            available = set(ALL_TARGETS) - set(candidate.targets.keys())
            if available:
                new_target = random.choice(list(available))
                candidate.targets[new_target] = random.uniform(self.config.min_potency, self.config.max_potency)
        
        elif mutation_type == 'remove' and len(candidate.targets) > 1:
            # Remove random target
            target_to_remove = random.choice(list(candidate.targets.keys()))
            del candidate.targets[target_to_remove]
        
        elif mutation_type == 'modify' and candidate.targets:
            # Modify potency of random target
            target_to_modify = random.choice(list(candidate.targets.keys()))
            delta = random.gauss(0, 0.1)  # Small random change
            new_potency = candidate.targets[target_to_modify] + delta
            new_potency = max(self.config.min_potency, min(self.config.max_potency, new_potency))
            candidate.targets[target_to_modify] = new_potency
    
    def run(self) -> DrugCandidate:
        """Evolve the population and return the fittest candidate found."""
        print(f"[GA] Starting: {self.config.iterations} generations, "
              f"population {self.config.population_size}")

        self.initialize_population()
        self._score_and_rank()

        print(f"[GA] Initial best fitness: {self.best_candidate.fitness:.3f}, "
              f"targets {self.best_candidate.get_active_targets()[:3]}")

        for generation in range(self.config.iterations):
            self.population = self._next_generation()
            self._score_and_rank()

            avg_fitness = sum(c.fitness for c in self.population) / len(self.population)
            self.fitness_history.append({
                'generation': generation + 1,
                'best_fitness': self.best_candidate.fitness,
                'avg_fitness': avg_fitness,
                'diversity': self._calculate_diversity(),
            })

            self._report_progress(generation + 1, avg_fitness)

            print(f"[GA] Generation {generation + 1}/{self.config.iterations}: "
                  f"best={self.best_candidate.fitness:.3f}, avg={avg_fitness:.3f}, "
                  f"targets {self.best_candidate.get_active_targets()[:3]}")

            if self.best_candidate.fitness > CONVERGENCE_FITNESS:
                print(f"[GA] Converged, fitness above {CONVERGENCE_FITNESS}")
                break

        print(f"[GA] Complete. Best fitness {self.best_candidate.fitness:.3f}")
        for target, potency in self.best_candidate.get_active_targets():
            print(f"  {target}: {potency:.3f}")

        return self.best_candidate

    def _next_generation(self) -> List[DrugCandidate]:
        """Carry the elite over untouched, then breed the rest."""
        offspring = self.population[:self.config.elite_count]

        while len(offspring) < self.config.population_size:
            parent1, parent2 = self.select_parents()
            child = self.crossover(parent1, parent2)
            self.mutate(child)
            offspring.append(child)

        return offspring

    def _score_and_rank(self):
        """Evaluate everyone, sort fittest first, and remember the leader."""
        self.evaluate_population()
        self.population.sort(key=lambda candidate: candidate.fitness, reverse=True)
        self.best_candidate = self.population[0]

    def _report_progress(self, generation: int, avg_fitness: float):
        """Push progress to the Java job tracker, if one is attached."""
        if not self.job_id:
            return

        try:
            requests.get(
                f"{self.java_url}/api/discovery/status/{self.job_id}",
                params={
                    "generation": generation,
                    "fitness": self.best_candidate.fitness,
                    "avgFitness": avg_fitness,
                },
                timeout=PROGRESS_REPORT_TIMEOUT_S
            )
        except Exception as report_error:
            print(f"[GA] Progress update failed: {report_error}")
    
    def _calculate_diversity(self) -> float:
        """Calculate population diversity (average pairwise distance)."""
        if len(self.population) < 2:
            return 0.0
        
        distances = []
        for i in range(min(10, len(self.population))):
            for j in range(i+1, min(10, len(self.population))):
                dist = self._drug_distance(self.population[i], self.population[j])
                distances.append(dist)
        
        return np.mean(distances) if distances else 0.0
    
    def _drug_distance(self, drug1: DrugCandidate, drug2: DrugCandidate) -> float:
        """Calculate distance between two drugs."""
        all_targets = set(drug1.targets.keys()) | set(drug2.targets.keys())
        
        distance = 0.0
        for target in all_targets:
            p1 = drug1.targets.get(target, 0.0)
            p2 = drug2.targets.get(target, 0.0)
            distance += abs(p1 - p2)
        
        return distance / len(all_targets) if all_targets else 0.0


def discover_drug(
    brain,
    disease_profile: DiseaseProfile,
    config: OptimizationConfig,
    generate_structure: bool = True,
    job_id: str = None
) -> Dict:
    """
    Main entry point for drug discovery.
    
    Args:
        brain: NeoCortex brain instance
        disease_profile: Disease to cure
        config: Optimization parameters
        generate_structure: If True, generate molecular structure (SMILES)
    
    Returns:
        Dict with optimal drug definition and optimization history
    """
    ga = GeneticAlgorithm(brain, disease_profile, config, job_id=job_id)
    best_drug = ga.run()
    
    result = {
        'optimal_drug': {
            'name': f"AI-Discovered-{int(best_drug.fitness*1000)}",
            'id': f"discovered_{hash(str(best_drug.targets)) % 10000}",
            'class': 'AI-Optimized Multi-Target',
            'typical_dose_mg': 100,
            'dose_range': [25, 400],
            'molecularTargets': [
                {'target': target, 'action': 'mechanism', 'potency': potency}
                for target, potency in best_drug.get_active_targets()
            ],
            'pharmacokinetics': {
                'halfLife_hours': 24,
                'tmax_hours': 2,
                'bioavailability': 0.7,
            },
            'optimization': {
                'fitness': best_drug.fitness,
                'generations': config.iterations,
                'population_size': config.population_size,
            },
        },
        'fitness_history': ga.fitness_history,
        'final_fitness': best_drug.fitness,
        'generations': len(ga.fitness_history),
    }
    
    # Generate molecular structure
    if generate_structure:
        try:
            from molecular_generator_ai import generate_structure_for_drug
            
            print("\n[DISCOVERY] Generating molecular structure...")
            
            target_profile = dict(best_drug.targets)
            structure_result = generate_structure_for_drug(target_profile, num_candidates=5, mode="hybrid")
            
            if 'error' not in structure_result:
                result['optimal_drug']['molecular_structure'] = structure_result
                print(f"[DISCOVERY] Structure generated: {structure_result['smiles']}")
            else:
                print(f"[DISCOVERY] Could not generate structure: {structure_result['error']}")
                result['optimal_drug']['molecular_structure'] = None
                
        except Exception as e:
            print(f"[DISCOVERY] Molecular generation failed: {e}")
            result['optimal_drug']['molecular_structure'] = None
    
    return result
