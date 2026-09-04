# AAA-WSN Mathematical Security Analysis — Reproducibility Package

This repository contains the numerical and computational material used to support the paper **“A Mathematical Model for Security Analysis of the AAA-WSN Authentication Scheme.”** The main objective is to allow the reported results to be reproduced from the same mathematical assumptions used in the manuscript.

The paper first derives the synchronization behavior analytically and then uses computation to verify the obtained expressions and study representative operating conditions. Therefore, the code in this repository is not presented as a replacement for the mathematical proofs. It is used to reproduce the numerical results, check the bounded authentication-state behavior, and generate the figures from the same result files.

## Repository structure

```text
AAA-WSN-Mathematical-Analysis/
├── README.md
├── REPRODUCIBILITY.md
├── RESULTS.md
├── CITATION.cff
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── security_models.py
│   ├── run_experiments.py
│   └── generate_figures.py
├── tests/
│   ├── test_security_models.py
│   ├── test_run_experiments.py
│   └── test_generate_figures.py
├── results/
└── figures/
```

`security_models.py` contains the independent-loss state model, synchronization boundary and rejection probabilities, expected boundary and rejection times, Gilbert-Elliott model, bounded active-suppression model, and the mathematical tradeoff associated with the subsequent-authentication parameter `M`.

`run_experiments.py` executes the numerical experiments used in the validation section. The default experiment uses **500,000 Monte Carlo trajectories for each selected configuration** and the fixed random seed **20260904**. It also performs exhaustive authentication-state exploration for `N <= 8` and `K <= 12`.

`generate_figures.py` reads the numerical results and generates the main validation figures. Therefore, the displayed figures and the reported CSV values are obtained from the same experiment outputs.

## Requirements

Python 3.11 or later is recommended. Install the required packages from the repository root:

```bash
python -m pip install -r requirements.txt
```

## Reproduce the reported results

Run the experiments from the repository root:

```bash
python -m src.run_experiments
```

The generated CSV and summary files will be stored in the `results/` directory.

Then generate the figures:

```bash
python -m src.generate_figures
```

The generated figures will be stored in the `figures/` directory.

Finally, the computational checks can be executed using:

```bash
python -m pytest -q
```

The expected result is that all tests pass and the exhaustive bounded-state analysis reports zero mismatches. With the default settings and the package versions listed in `requirements.txt`, the current validation run gives an RMSE of `9.22417029484e-05`, an MAE of `8.20037526817e-05`, and `65,520` exhaustively checked traces with zero mismatches.

## Main outputs

The experiment produces five numerical tables: Monte Carlo validation, reliability-driven selection of `N`, robust selection of `N` under bounded active suppression, Gilbert-Elliott burst-loss results, and the communication-linkability tradeoff for `M`. A validation summary is also generated to report the Monte Carlo sample size, random seed, RMSE, MAE, and the number of exhaustively checked state traces.

## Quick result check

A concise summary of the main reproduced numerical values is provided in `RESULTS.md`. The complete relation between the manuscript sections and the executable files is provided in `REPRODUCIBILITY.md`.

## Reproducibility note

The numerical values depend on the parameters stated in the paper and in the experiment script. The random seed is fixed so that the Monte Carlo results can be reproduced. Small differences may appear if different numerical-library versions are used, especially in floating-point matrix operations. The analytical conclusions are independent of these small numerical differences.

## Original AAA-WSN scheme

The mathematical analysis in this repository is based on the state evolution and authentication parameters defined in the original AAA-WSN scheme:

Shadi Nashwan, “AAA-WSN: Anonymous access authentication scheme for wireless sensor networks in big data environment,” *Egyptian Informatics Journal*, vol. 22, no. 1, pp. 15–26, 2021. DOI: 10.1016/j.eij.2020.02.005.
