# Cultural Evolution Framework Replication

This repository contains a replication of the historical framework established by Baumard et al. (2022).

Instead of splitting history into fixed, separate time blocks, this workflow models time as a continuous line across 17 historical regions using a Gaussian Process. This method smooths out gaps where data is scarce and allows for tracking of long-term cultural trends without artificial timeline cuts.

## Background & data sources

The original study applies the **Evoked and Transmitted Culture (ETC)** framework to examine how environmental changes and human psychological traits interact to shape historical records over centuries.

* **Original Paper:** Baumard, N., Huillery, E., Hyafil, A. & Safra, L. 2022. The cultural evolution of love in literary history. *Nature Human Behavior* 6, 506–522. https://doi.org/10.1038/s41562-022-01292-z.
* **Data Source:** The original study dataset can be downloaded from https://osf.io/ud35x.
* **Original Code Base:** The original MATLAB scripts used by the authors are available at https://github.com/ahyafil/Evoked_Transmitted_Culture.

### Key differences in this version
This project updates the underlying statistics to make the models more stable and easier to compare:

| Component | Original Study Engine (MATLAB) | Replicated Engine (Python/PyMC) |
| :--- | :--- | :--- |
| **Handling Time** | Tracks changes step-by-step in fixed historical eras. | Tracks trends continuously over time. |
| **Data Gaps** | Creates blocks that leave sharp gaps between eras. | Uses a Gaussian Process to smooth out periods with missing data. |
| **Model Fitting** | Uses estimation loops to find single best-fit values. | Uses Bayesian MCMC sampling to map out full probability spreads. |
| **Error Tracking** | Estimates errors using simulated reshuffling tests. | Measures uncertainty using Highest Density Intervals directly from the data. |

## Results of replication

### Summary statistics
* Main Predictor Effect (`Beta_Mean`): `0.3006`
* 95% Uncertainty Range (HDI): `[0.1958, 0.4103]`

### Final verdict: Robust support
The replication **strongly supports** the core findings of the original paper.

In the original study, the authors argued that specific socioeconomic changes driven by environmental and psychological dynamics were tied to a higher likelihood of romantic themes appearing in historical literature.

Because the entire 95% Bayesian uncertainty interval (`HDI_2.5` to `HDI_97.5`) sits entirely above zero, the updated model confirms that this relationship remains highly significant. The finding is highly resilient: even when we strip away the original paper's arbitrary historical time blocks and account for smooth spatial and temporal variations across 17 distinct regions, the underlying historical trend holds true.

## Repository structure

```text
constraints-endure-culture/
├── data/
│   └── Data_love_bywork_2019.xlsx                # Source data
├── output/
│   ├── figures/
│   │   ├── eurasian_love_trajectories.png        # Summary trends by era
│   │   ├── model_comparison_chart.png            # Comparison between frameworks
│   │   └── replicated_trajectories.png           # Bayesian model trajectories
│   └── tables/
│       ├── bayesian_posterior_summary.csv        # Variance and model details
│       ├── era_binned_comparison.csv             # Results grouped into era blocks for comparison
│       ├── etc_bayesian_latent_trajectories.csv  # Continuous regional trend lines
│       ├── etc_bayesian_metrics.csv              # Main effect sizes and uncertainty ranges
│       └── model_confirmation_table.md           # Summary table for reports
├── utils/
│   ├── __init__.py                               # Handles shortcut imports
│   ├── compare_models.py                         # Groups trends and calculates comparisons
│   └── generate_plots.py                         # Plot generator
├── README.md                                     # Project documentation
└── run_model.py                                  # Runs the main Bayesian model
```

## Data cleaning & transformations

The main script `run_model.py` automatically cleans the spreadsheet data before fitting the model:
* **Combining Regions:** Small, granular region codes (like `AND`, `IRA`, `SYR`) are grouped into broad historical zones (like `ARA` for the Arab World) to match the paper's framework.
* **Time Alignment:** The entire dataset is sorted chronologically by year so the continuous trend models line up perfectly across regions.
* **Trimming Lifespans:** Data entries that fall completely outside a culture's actual historical existence (such as Arab World data from before 500 AD or late modern Egyptian entries) are filtered out to keep early history clean.

## How to Run the Replication

### 1. Fit the Bayesian model
Run the core statistical pipeline. This step cleans the data, runs the model sampler, and saves the trend data:
```bash
python run_model.py
```

### 2. Compare the frameworks
Run this script to aggregate the continuous model trends into the original study's fixed blocks for a direct comparison:
```bash
python utils/compare_models.py
```

### 3. Generate charts
Generate the final figures, comparison plots, and summary charts:
```bash
python utils/generate_plots.py
```
