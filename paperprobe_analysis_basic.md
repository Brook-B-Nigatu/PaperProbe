# RadonPy Repository Summary

## Overview
**Repository Name:** [RadonPy/RadonPy](https://github.com/RadonPy/RadonPy)  
**Description:** RadonPy is a Python library to automate physical property calculations for polymer informatics.  
**Created On:** March 17, 2022  
**Age:** 3.7 years  
**Primary Language:** Python  

## Activity
- **Stars:** 223  
- **Forks:** 41  
- **Watchers:** 223  
- **Total Commits:** 110  
- **Last Commit:** February 3, 2025 (296 days ago)  
- **Activity Status:** Low Activity  
- **Contributors:** 3  
- **Open Issues:** 14  

## License
- **License Type:** BSD 3-Clause "New" or "Revised" License  

## Documentation
- **Wiki:** [RadonPy Documentation](https://github.com/RadonPy/RadonPy/wiki)  
- **Default Branch:** develop  

## Contributors
1. **yhayashi1986:** 106 contributions  
2. **KouheiOda:** 2 contributions  
3. **Nodanoda-kun:** 2 contributions  

## Required Packages
```plaintext
matplotlib==3.10.7
mdtraj==1.11.0
mpi4py==4.1.1
numpy==2.3.5
pandas==2.3.3
psutil==7.1.3
qcengine==0.33.0
rdkit==2025.9.1
resp==0.1.2
scipy==1.16.3
setuptools==80.9.0
tqdm==4.67.1
```

## Example Script of Usage
The following script demonstrates how to set up a polymer simulation using the RadonPy library:

```python
import os
import uuid
from radonpy.core import utils, calc, poly
from radonpy.sim import helper
from radonpy.ff.gaff2 import GAFF2_mod

if __name__ == '__main__':
    # Example data setup
    data = {
        'UUID': str(uuid.uuid4()),
        'DBID': 'example_db',
        'monomer_ID': 'example_monomer',
        'copoly_ratio_list': '1',
        'input_natom': 1000,
        'input_nchain': 10,
        'ini_density': 0.05,
        'temp': 300.0,
        'press': 1.0,
        'input_tacticity': 'atactic',
        'forcefield': 'GAFF2_mod',
    }

    # Create directories for output
    work_dir = f'./{data["DBID"]}'
    os.makedirs(work_dir, exist_ok=True)
    save_dir = os.path.join(work_dir, 'analyze')
    os.makedirs(save_dir, exist_ok=True)

    # Initialize force field
    ff = GAFF2_mod()

    # Simulate polymerization
    mols = []  # Placeholder for monomer objects
    n = poly.calc_n_from_num_atoms(mols, data['input_natom'], ratio=[1], terminal1=None, terminal2=None)
    homopoly = poly.polymerize_rw(mols[0], n, tacticity=data['input_tacticity'])
    result = ff.ff_assign(homopoly)

    # Save results
    utils.MolToJSON(homopoly, os.path.join(save_dir, 'polymer.json'))
    print('Polymer simulation completed and saved to', save_dir)
```

This script sets up a polymer simulation, initializes the necessary directories, and saves the results in JSON format.