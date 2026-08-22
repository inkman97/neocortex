"""Download protein structure from PDB."""
import requests
import sys
import os

# Create directory
os.makedirs('protein_structures', exist_ok=True)

pdb_id = sys.argv[1] if len(sys.argv) > 1 else "4EY7"

print(f"[DOWNLOAD] Downloading {pdb_id} from PDB...")

url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
response = requests.get(url)

if response.status_code == 200:
    filepath = f"protein_structures/{pdb_id}.pdb"
    with open(filepath, 'wb') as f:
        f.write(response.content)
    print(f"[OK] Downloaded: {filepath}")
    print(f"  Now run: python prepare_receptor.py {pdb_id}")
else:
    print(f"[X] Error: HTTP {response.status_code}")