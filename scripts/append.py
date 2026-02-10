import os
import pandas as pd

# Define paths
base_path = os.path.expanduser("~/Downloads/Semi_A_FS_Data/")
parquet_file = "/Users/arun/Documents/Python Projects/Floorsheet Code/Floorsheet/combined_data.parquet"

# Collect all CSV files
csv_files = [os.path.join(base_path, f) for f in os.listdir(base_path) if f.endswith(".csv")]

# Read and concatenate all CSVs
dataframes = []
for f in csv_files:
    df = pd.read_csv(f, dtype=str)  # Read all columns as strings to avoid type issues
    dataframes.append(df)

combined_csv_data = pd.concat(dataframes, ignore_index=True)

# Optional: replace NaNs with empty string if needed
combined_csv_data = combined_csv_data.fillna("")

# Load existing Parquet data if exists
if os.path.exists(parquet_file):
    existing_data = pd.read_parquet(parquet_file)
    # Ensure matching dtypes
    existing_data = existing_data.astype(str).fillna("")
    final_data = pd.concat([existing_data, combined_csv_data], ignore_index=True)
else:
    final_data = combined_csv_data

# Save to Parquet
final_data.to_parquet(parquet_file, index=False)

print(f"Appended {len(combined_csv_data)} rows to {parquet_file}")
