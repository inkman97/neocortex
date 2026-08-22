"""Prepare receptor PDBQT for docking."""
import subprocess
import sys
import os

pdb_id = sys.argv[1] if len(sys.argv) > 1 else "4EY7"

pdb_file = f"protein_structures/{pdb_id}.pdb"
pdbqt_file = f"protein_structures/{pdb_id}_prepared.pdbqt"

if not os.path.exists(pdb_file):
    print(f"[X] Error: {pdb_file} not found")
    print(f"  Run first: python download_protein.py {pdb_id}")
    sys.exit(1)

print(f"[PREP] Preparing {pdb_id}...")
print(f"  Input:  {pdb_file}")
print(f"  Output: {pdbqt_file}")

# Convert with OpenBabel
cmd = [
    'obabel',
    pdb_file,
    '-O', pdbqt_file,
    '-r',         # Remove non-polar H
    '-p', '7.4'   # Add H at pH 7.4
]

try:
    subprocess.run(cmd, check=True)
    print(f"[OK] Receptor prepared: {pdbqt_file}")
except FileNotFoundError:
    print(f"[X] Error: OpenBabel not found")
    print(f"  Install with: conda install -c conda-forge openbabel")
except Exception as e:
    print(f"[X] Error: {e}")