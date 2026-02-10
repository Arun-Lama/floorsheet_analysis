import pandas as pd
import os
import glob

# Define base paths
base_path = os.path.expanduser("~/Downloads/Semi_A_FS_Data/")
output_path = os.path.expanduser("~/Downloads/Semi_A_FS_Data/")

# Create output folder if it doesn't exist
os.makedirs(output_path, exist_ok=True)
print("hi")
# Loop through all Excel files in the folder
for file_path in glob.glob(os.path.join(base_path, "*.xlsx")):
    try:
        # Read Excel file
        data = pd.read_excel(file_path)

        # Extract date from Contract No.
        data['Date'] = pd.to_datetime(data['Contract No.'].astype(str).str[:8], format='%Y%m%d')
        date = data['Date'].iloc[0].date()

        # Save as CSV with date in the filename
        output_file = os.path.join(output_path, f"{date} floorsheet.csv")
        data.to_csv(output_file, index=False)
        
        print(f"Processed: {os.path.basename(file_path)} → {os.path.basename(output_file)}")
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
