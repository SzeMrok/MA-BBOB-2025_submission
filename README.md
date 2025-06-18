# MERADS_QFUR_V21a for MA-BBOB Competition 2025

## Overview

This repository contains the code and performance data for the **MERADS_QFUR_V21a** algorithm, submitted to the MA-BBOB 2025 competition.

- **Algorithm code:** [`MERADS_QFUR_V21a.py`](MERADS_QFUR_V21a.py)
- **Performance data:** [`results.zip`](results.zip) (unpacked in [`results/`](results/))
- **Dependencies:** [`requirements.txt`](requirements.txt)

## Reproducibility Instructions

### 1. Install Dependencies

Install the required Python packages:

```sh
pip install -r requirements.txt
```

### 2. Prepare Instance Data

Download the instance specification files (`weights.csv`, `iids.csv`, `opt_locs.csv`) from the [competition website](https://iohprofiler.github.io/competitions/mabbob25) and place them in the root of this repository.

### 3. Running the Algorithm

The algorithm is implemented as a class in [`MERADS_QFUR_V21a.py`](MERADS_QFUR_V21a.py). To run it on the MA-BBOB problems and collect results, use a script similar to the following:

```python
import ioh
import numpy as np
import pandas as pd
from MERADS_QFUR_V21a import MERADS_QFUR_V21a

# Load instance specifications
weights = pd.read_csv("weights.csv", index_col=0)
iids = pd.read_csv("iids.csv", index_col=0)
opt_locs = pd.read_csv("opt_locs.csv", index_col=0)

# Set up logger for IOHexperimenter
logger = ioh.logger.Analyzer(
    root="results",
    folder_name="MERADS_QFUR_V21a",
    algorithm_name="MERADS_QFUR_V21a"
)

for dim in [2, 5]:
    for idx in range(100):
        problem = ioh.problem.ManyAffine(
            xopt=np.array(opt_locs.iloc[idx])[:dim],
            weights=np.array(weights.iloc[idx]),
            instances=np.array(iids.iloc[idx], dtype=int),
            n_variables=dim
        )
        problem.set_id(100)
        problem.set_instance(idx)
        problem.attach_logger(logger)
        algo = MERADS_QFUR_V21a(budget_factor=2000)
        algo(problem)
        problem.reset()
logger.close()
```

This will generate results in the `results/` directory, matching the structure required for the competition.

### 4. Analyzing Results

You can analyze the results using [IOHinspector](https://pypi.org/project/iohinspector/) or the [IOHanalyzer web tool](https://iohanalyzer.liacs.nl/):

```python
import iohinspector
manager = iohinspector.DataManager()
manager.add_folder("results/2D/MERADS_QFUR_V21a")
manager.add_folder("results/5D/MERADS_QFUR_V21a")
df = manager.load(True, True)
```

## Notes

- The provided `results.zip` contains the data generated for the official submission.
- For full reproducibility, use the same instance files and Python environment.
- For more details, see the [MA-BBOB 2025 competition page](https://iohprofiler.github.io/competitions/mabbob25).

## Contact

For questions or reproducibility issues, please contact the authors via the