"""
Averages continuous model trajectories into matching era blocks to compute trend correlations.
Exports an automated Markdown comparison table for project documentation.
"""
import os
import numpy as np
import pandas as pd

def execute_model_comparison(bayes_path='output/tables/etc_bayesian_latent_trajectories.csv', output_dir='output/tables'):
    if not os.path.exists(bayes_path):
        raise FileNotFoundError(f"Missing latent trajectory file at: {bayes_path}")

    df_bayes = pd.read_csv(bayes_path)
    code_cleaner = {'JIA': 'CHI', 'SHA': 'JAP', 'WEL': 'WEL', 'IRE': 'IRE'}
    df_bayes['Regional_Zone'] = df_bayes['Regional_Zone'].replace(code_cleaner)

    # Historical time frames from the original publication
    era_definitions = [
        {"name": "Antiquity / Axial Age",     "start": -500, "end": 200,  "orig_est": -0.65, "orig_se": 0.15},
        {"name": "Late Antiquity / Early MD",   "start": 200,  "end": 800,  "orig_est": -0.20, "orig_se": 0.12},
        {"name": "High & Late Middle Ages",    "start": 800,  "end": 1400, "orig_est":  0.35, "orig_se": 0.14},
        {"name": "Early Modern Era",           "start": 1400, "end": 1800, "orig_est":  0.95, "orig_se": 0.09}
    ]

    comparison_records = []

    for era in era_definitions:
        mask = (df_bayes['Historical_Year'] >= era['start']) & (df_bayes['Historical_Year'] < era['end'])
        era_data = df_bayes[mask]

        if not era_data.empty:
            your_mean = era_data['Latent_Value_Mean'].mean()
            your_sd = era_data['Latent_Value_Mean'].std()
        else:
            your_mean, your_sd = np.nan, np.nan

        comparison_records.append({
            "Era Window": f"{era['start']} to {era['end']} CE",
            "Era Designation": era['name'],
            "Original GLM Estimate": era['orig_est'],
            "Original SE": era['orig_se'],
            "Your Bayesian Mean": your_mean,
            "Your Cross-Regional SD": your_sd
        })

    df_comp = pd.DataFrame(comparison_records)
    correlation = np.corrcoef(df_comp["Original GLM Estimate"], df_comp["Your Bayesian Mean"])[0, 1]

    # Export clean Markdown syntax summary report file
    md_path = os.path.join(output_dir, "model_confirmation_table.md")
    os.makedirs(output_dir, exist_ok=True)

    with open(md_path, 'w') as f:
        f.write("### Cross-Framework Paradigm Confirmation Matrix\n\n")
        f.write("| Historical Era Window | Cultural Era Designation | Original GLM Estimate (±SE) | Replicated Bayes Mean (±SD) | Confirmation Verdict |\n")
        f.write("| :--- | :--- | :---: | :---: | :--- |\n")

        for _, row in df_comp.iterrows():
            orig_str = f"{row['Original GLM Estimate']:.2f} (±{row['Original SE']:.2f})"
            bayes_str = f"{row['Your Bayesian Mean']:.2f} (±{row['Your Cross-Regional SD']:.2f})"

            orig_direction = np.sign(row['Original GLM Estimate'])
            bayes_direction = np.sign(row['Your Bayesian Mean'])
            verdict = "**Confirmed** (Directional Match)" if orig_direction == bayes_direction else "Divergent Trend"

            f.write(f"| {row['Era Window']} | {row['Era Designation']} | {orig_str} | {bayes_str} | {verdict} |\n")

        f.write(f"\n*Statistical Alignment Diagnostic: Trend Correlation coefficient (r) = **{correlation:+.4f}***\n")

    # Save matching CSV spreadsheet file
    df_comp.to_csv(os.path.join(output_dir, "era_binned_comparison.csv"), index=False)
    print(f"Generated comparison spreadsheets and Markdown logs at: {output_dir}")

if __name__ == "__main__":
    execute_model_comparison()
