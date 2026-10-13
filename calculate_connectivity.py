"""
calculate_connectivity.py - This script checks data clustering across the culture dataset layers.
It uses the installed 'pykdensity' library to evaluate spatial overlap
and thematic linkages within the excel datasheet.
"""

import os
import pandas as pd
import numpy as np
from pykdensity import calculate_densities

# project setup
data_dir = "data"
output_csv = os.path.join("output", "tables", "culture_connectivity_summary.csv")
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

print("\nStarting data connectivity analysis")
# original study data, converted to xlsx to preserve formatting
data_path = os.path.join(data_dir, "Data_love_bywork_2019.xlsx")

# verify dataset
if not os.path.exists(data_path):
    print(f"Error: Culture data sheet missing at {data_path}")
    exit(1)

print(f"Loading dataset file: {data_path}")
df_culture = pd.read_excel(data_path)
sample_size = len(df_culture)
print(f"Successfully loaded {sample_size} cultural trajectory records.")

# identifier column
id_column = 'Name' if 'Name' in df_culture.columns else df_culture.columns[0]

# thematic attributes present in dataset columns
struct_list = [col for col in ['Century', 'Genre.1'] if col in df_culture.columns]

# run the matrix check
# map parameters to 'spatial_cats' and 'struct_cats'
k_spatial, k_structural = calculate_densities(
    data=df_culture,
    id_col=id_column,
    tree=None,                  # disabled: culture relies on text categories
    tree_type='adaptive',       # uses adaptive categorical checking
    coord_cols=None,            # space is checked via region tags instead of coordinates
    spatial_cats='Zone' if 'Zone' in df_culture.columns else None,
    struct_cats=struct_list if struct_list else None,
    spatial_km=500.0,
    struct_depth=8,
    verbose=True
)

# tag safety topology boundaries
if not pd.isna(k_structural) and k_structural <= 0.10:
    tier_status = "sparse_topology"
elif not pd.isna(k_structural) and k_structural <= 0.25:
    tier_status = "moderate_topology"
else:
    tier_status = "dense_topology"

# compile results into a summary table
compiled_results = [{
    "Dataset": "Data_love_bywork_2019",
    "Sample_Size_N": sample_size,
    "Spatial_Density": k_spatial if not pd.isna(k_spatial) else "N/A",
    "Structural_Density": k_structural if not pd.isna(k_structural) else "N/A",
    "Topology_Tier": tier_status
}]

print("\nConnectivity check complete")
print("-" * 80)

df_out = pd.DataFrame(compiled_results)
df_out.to_csv(output_csv, index=False)
print(f"Summary file saved to: {output_csv}\n")

print(df_out.to_string(index=False))
print("-" * 80 + "\n")
