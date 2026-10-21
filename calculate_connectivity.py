"""
calculate_connectivity.py - This script checks data clustering across the culture dataset layers.
It uses the installed 'pytstability' library to evaluate spatial overlap
and thematic linkages within the excel datasheet.
"""

import os
import pandas as pd
import numpy as np
from pytstability import calculate_densities

# Set up project directories and output path
data_dir = "data"
output_csv = os.path.join("output", "tables", "culture_connectivity_summary.csv")
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

print("\nStarting data connectivity analysis")
data_path = os.path.join(data_dir, "Data_love_bywork_2019.xlsx")

if not os.path.exists(data_path):
    print(f"Error: Culture data sheet missing at {data_path}")
    exit(1)

print(f"Loading dataset file: {data_path}")
df_culture = pd.read_excel(data_path)
sample_size = len(df_culture)
print(f"Successfully loaded {sample_size} cultural trajectory records.")

# Clean up column names and find the identifier column
df_culture.columns = df_culture.columns.str.strip()
id_column = 'Name' if 'Name' in df_culture.columns else df_culture.columns[0]

# Identify thematic attributes present in dataset columns
struct_list = [col for col in ['Century', 'Genre.1'] if col in df_culture.columns]

try:
    # The package will automatically select the Fixed Absolute Depth optimization track
    spatial_metrics, struct_metrics, tsi_current, gamma_current = calculate_densities(
        data=df_culture,
        id_col=id_column,
        spatial_cats='Zone' if 'Zone' in df_culture.columns else None,
        struct_cats=struct_list if struct_list else None,
        struct_depth='auto',  # Engages internal Route 1 optimization
        verbose=False
    )

    k_spatial = float(spatial_metrics["kappa"]) if not pd.isna(spatial_metrics["kappa"]) else np.nan
    k_structural = float(struct_metrics["kappa"]) if not pd.isna(struct_metrics["kappa"]) else np.nan

except Exception as e:
    print(f"Warning: Density calculation failed: {e}")
    k_spatial = np.nan
    k_structural = np.nan
    tsi_current = np.nan
    gamma_current = np.nan

# Categorize the network stability using the threshold boundary guidelines
if not pd.isna(tsi_current) and tsi_current <= 0.0018:
    tier_status = "critical funnel zone"
elif not pd.isna(tsi_current) and tsi_current <= 0.0500:
    tier_status = "moderate geometric shear"
else:
    tier_status = "stable pooling backbone"

compiled_results = [{
    "Dataset": "Data_love_bywork_2019",
    "Sample_Size_N": sample_size,
    "Spatial_Density": k_spatial if not pd.isna(k_spatial) else np.nan,
    "Structural_Density": k_structural if not pd.isna(k_structural) else np.nan,
    "Topology_Stability_Index": tsi_current if not pd.isna(tsi_current) else np.nan,
    "Critical_Horizon": gamma_current if not pd.isna(gamma_current) else np.nan,
    "Operational_Status": tier_status
}]

print("\nConnectivity check complete")
print("-" * 80)

df_out = pd.DataFrame(compiled_results)
df_out.to_csv(output_csv, index=False)
print(f"Summary file saved to: {output_csv}\n")

print(df_out.to_string(index=False, formatters={
    "Spatial_Density": lambda x: f"{x:.4f}" if not pd.isna(x) else "N/A",
    "Structural_Density": lambda x: f"{x:.4f}" if not pd.isna(x) else "N/A",
    "Topology_Stability_Index": lambda x: f"{x:.5f}" if not pd.isna(x) else "N/A"
}))
print("-" * 80 + "\n")
