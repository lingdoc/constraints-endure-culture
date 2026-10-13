"""
run_model.py - Fits a spatiotemporal model across historical macro-regions.
Uses a categorical random effect for regions and a continuous 1D
Hilbert Space Gaussian Process (HSGP) to capture smooth temporal trends.
Fixes alignment mapping errors and limits cultural timeline bleeding.
"""
import os
import numpy as np
import pandas as pd
import pymc as pm

def run_pipeline(data_path="data/Data_love_bywork_2019.xlsx", output_dir="output"):
    print(f"Loading data from {data_path}...")

    table_dir = os.path.join(output_dir, "tables")
    os.makedirs(table_dir, exist_ok=True)

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing source file: {data_path}")

    # standardize column headers and drop empty target fields
    df = pd.read_excel(data_path, engine='openpyxl')
    df['Zone'] = df['Zone'].astype(str).str.strip().str.upper()
    df = df.rename(columns={
        'Love.story..yes...1.': 'Trait',
        'Strong.Love_url': 'Predictor',
        'DATE': 'Year',
        'Zone': 'Raw_Region'
    })

    # map both full names and short codes
    string_region_mapping = {
        # full text spreadsheet names & exact matching short-codes
        'Ancient Egypt':     'EGY', 'EGY': 'EGY',
        'England':           'ENG', 'ENG': 'ENG',
        'France':            'FRA', 'FRA': 'FRA',
        'German World':      'GER', 'GER': 'GER',
        'Greek World':       'GRE', 'GRE': 'GRE',
        'Indian World':      'IND', 'IND': 'IND',
        'Persian World':     'PER', 'PER': 'PER',
        'East Slavic World': 'RUS', 'RUS': 'RUS',
        'Spain':             'SPA', 'SPA': 'SPA',
        'Italy':             'ITA', 'ITA': 'ITA',
        'Japan':             'JAP', 'JAP': 'JAP',
        'China':             'CHI', 'CHI': 'CHI',

        # Norse World & Iceland (Mapped to ICE to match plotting config)
        'Norse World': 'ICE', 'NOR': 'ICE', 'ICE': 'ICE', 'Iceland': 'ICE',

        # Granular sub-codes and variations
        'JIA': 'CHI', 'SHA': 'JAP',
        'WEL': 'WEL', 'WAL': 'WEL',
        'IRE': 'IRE', 'IRL': 'IRE',
        'DUT': 'LOW', 'LOW': 'LOW',

        # Islamic & Arabic World sub-regions pooled together
        'AND': 'ARA', 'IRA': 'ARA', 'SYR': 'ARA',
        'TUN': 'ARA', 'TUR': 'ARA', 'HEB': 'ARA',
        'CHM': 'ARA', 'ARA': 'ARA'
    }

    # map the raw strings down to unified macro-regions
    df['Region'] = df['Raw_Region'].map(string_region_mapping)

    # drop rows that don't match the core historical framework definitions
    df = df.dropna(subset=['Region'])

    # format numeric fields
    df['Trait'] = pd.to_numeric(df['Trait'], errors='coerce')
    df['Predictor'] = pd.to_numeric(df['Predictor'], errors='coerce')
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df.dropna(subset=['Trait', 'Predictor', 'Year'])

    # chronological sorting preserves row index time mapping
    df = df.sort_values(by='Year').reset_index(drop=True)

    # timeline containment trimming to prevent cross-cultural bleeding
    df = df[~((df['Region'] == 'ARA') & (df['Year'] < 500))]
    df = df[~((df['Region'] == 'EGY') & (df['Year'] > 500))]
    df = df.reset_index(drop=True)

    print("Detected unique regions in data:", df['Region'].unique())

    # convert regions to numeric categories for index-mapping in PyMC
    df['Region'] = pd.Categorical(df['Region'])
    region_names = df['Region'].cat.categories
    num_regions = len(region_names)
    region_idx = df['Region'].cat.codes.to_numpy().astype(int)

    # standardize continuous timeline values for the HSGP kernel
    raw_years = df['Year'].to_numpy().astype(float)
    year_mean, year_std = np.mean(raw_years), np.std(raw_years)
    norm_years = (raw_years - year_mean) / (year_std if year_std > 0 else 1.0)
    norm_years_X = norm_years[:, None]

    y_obs = df['Trait'].to_numpy().astype(int)
    x_pred = df['Predictor'].to_numpy().astype(float)
    if np.std(x_pred) > 0:
        x_pred = (x_pred - np.mean(x_pred)) / np.std(x_pred)

    print(f"Building PyMC model graph for N={len(df)} observations across {num_regions} regions...")

    with pm.Model() as model:
        # fFixed effect slope for the main predictor
        alpha = pm.Normal("Intercept", mu=0.0, sigma=5.0)
        beta = pm.Normal("Beta_Slope", mu=0.0, sigma=2.0)
        linear_predictor = alpha + beta * x_pred

        # non-centered category offsets for the discrete macro-zones
        sigma_space = pm.HalfNormal("Spatial_Variance", sigma=2.0)
        space_raw = pm.Normal("space_offset", mu=0, sigma=1, shape=num_regions)
        spatial_effect = space_raw[region_idx] * sigma_space

        # smooth 1D temporal field via Matern32 HSGP approximation
        sigma_time = pm.HalfNormal("Temporal_Variance", sigma=2.0)
        length_scale = pm.Gamma("Temporal_Range_Scale", alpha=2.0, beta=1.0)
        cov_func = sigma_time**2 * pm.gp.cov.Matern32(input_dim=1, ls=length_scale)

        # 30 basis functions handle the continuous temporal canvas smoothly
        gp_time = pm.gp.HSGP(m=[30], c=1.5, cov_func=cov_func)
        temporal_effect = gp_time.prior("f_temporal", X=norm_years_X)

        # map to probability scale via inverse-logit link
        p = pm.math.invlogit(linear_predictor + spatial_effect + temporal_effect)
        pm.Bernoulli("y_obs", p=p, observed=y_obs)

        print("Sampling posterior distributions via NumPyro...")
        idata = pm.sample(
            draws=1500, tune=1500, chains=4, target_accept=0.96,
            random_seed=42, nuts_sampler="numpyro",
            nuts_sampler_kwargs={"chain_method": "vectorized"}
        )

    # save summary stats
    print("Exporting results spreadsheets...")
    summary = pm.summary(idata, var_names=["Intercept", "Beta_Slope", "Spatial_Variance", "Temporal_Variance", "Temporal_Range_Scale"])
    summary.to_csv(os.path.join(table_dir, "bayesian_posterior_summary.csv"))

    post_slope = idata.posterior["Beta_Slope"].values.flatten()
    metrics_df = pd.DataFrame([{
        "Predictor": "Strong.Love_url",
        "Beta_Mean": np.mean(post_slope),
        "Beta_SD": np.std(post_slope),
        "HDI_2.5": np.percentile(post_slope, 2.5),
        "HDI_97.5": np.percentile(post_slope, 97.5)
    }])
    metrics_df.to_csv(os.path.join(table_dir, "etc_bayesian_metrics.csv"), index=False)

    # Unpack posterior arrays to reconstruct historical trends
    space_samples = idata.posterior["space_offset"].values * idata.posterior["Spatial_Variance"].values[..., None]
    time_samples = idata.posterior["f_temporal"].values

    space_flat = space_samples.reshape(-1, num_regions)
    time_flat = time_samples.reshape(-1, len(df))

    means = np.zeros(len(df))
    sds = np.zeros(len(df))
    for idx in range(len(df)):
        combined_samples = space_flat[:, region_idx[idx]] + time_flat[:, idx]
        means[idx] = np.mean(combined_samples)
        sds[idx] = np.std(combined_samples)

    pd.DataFrame({
        'Regional_Zone': df['Region'],
        'Historical_Year': df['Year'],
        'Latent_Value_Mean': means,
        'Latent_Value_SD': sds
    }).to_csv(os.path.join(table_dir, "etc_bayesian_latent_trajectories.csv"), index=False)

    print("Done.")

if __name__ == "__main__":
    run_pipeline()
