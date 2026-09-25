"""
calculate_connectivity.py

this script checks data clustering across the culture dataset layers.
it uses the installed 'pykdensity' library to evaluate spatial overlap
and thematic linkages within the centralized excel datasheet.
"""

import os
import pandas as pd
import numpy as np
from pykdensity import calculate_densities

# 0. project setup
# folders to read/write data based on your directory layout
data_dir = "data"
output_csv = os.path.join("output", "tables", "culture_connectivity_summary.csv")
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

print("\nStarting data connectivity analysis")

data_path = os.path.join(data_dir, "Data_love_bywork_2019.xlsx")

# 1. verify dataset availability
if not os.path.exists(data_path):
    print(f"Error: Culture data sheet missing at {data_path}")
    exit(1)

print(f"Loading dataset file: {data_path}")
df_culture = pd.read_excel(data_path)
sample_size = len(df_culture)
print(f"Successfully loaded {sample_size} cultural trajectory records.")

# 2. run the matrix check using matching categories
# the package prints individual data layer diagnostics automatically
k_spatial, k_structural = calculate_densities(
    data=df_culture,
    id_col='Name' if 'Name' in df_culture.columns else df_culture.columns[0],
    tree=None,                  # disabled: culture relies on text categories
    tree_type='fixed',          # ignored since no tree file is supplied
    coord_cols=['Zone'] if 'Zone' in df_culture.columns else None,              # groups by region names
    theme_cols=['Century', 'Genre.1'] if 'Century' in df_culture.columns else None,  # groups by era and genre
    verbose=True
)

# 3. compile results into a summary table
compiled_results = [{
    "Dataset": "Data_love_bywork_2019",
    "Sample_Size_N": sample_size,
    "Spatial_Density": k_spatial if not pd.isna(k_spatial) else "N/A",
    "Structural_Density": k_structural if not pd.isna(k_structural) else "N/A"
}]

print("\nConnectivity check complete")
print("-" * 80)

df_out = pd.DataFrame(compiled_results)
df_out.to_csv(output_csv, index=False)
print(f"Summary file saved to: {output_csv}\n")

# print the final table summary directly to your console
print(df_out.to_string(index=False))
print("-" * 80 + "\n")
