import pandas as pd

# Load Excel file
file_path = "Dataset/AQI_hourly_city_level_gwalior_2025_January_gwalior_January_2025.xlsx"
df = pd.read_excel(file_path)

# Convert all columns except first (date/day) to numeric
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Function to fill nulls using previous 3 values mean
def fill_with_prev_mean(series):
    for i in range(len(series)):
        if pd.isna(series[i]):
            prev_vals = series[max(0, i-3):i]  # previous 3 values
            mean_val = prev_vals.mean()
            series[i] = mean_val
    return series

# Apply to each column except first column
for col in df.columns[1:]:
    df[col] = fill_with_prev_mean(df[col])

# Save cleaned file
output_path = "Dataset/cleaned_aqi_data.xlsx"
df.to_excel(output_path, index=False)

print("✅ Preprocessing done! File saved:", output_path)

import os
import pandas as pd

file_path = os.path.join(os.path.dirname(__file__),
                        "AQI_hourly_city_level_gwalior_2025_January_gwalior_January_2025.xlsx")

df = pd.read_excel(file_path)

# Convert all columns except first (date/day) to numeric
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Function to fill nulls using previous 3 values mean
def fill_with_prev_mean(series):
    for i in range(len(series)):
        if pd.isna(series[i]):
            prev_vals = series[max(0, i-3):i]  # previous 3 values
            mean_val = prev_vals.mean()
            series[i] = mean_val
    return series

# Apply to each column except first column
for col in df.columns[1:]:
    df[col] = fill_with_prev_mean(df[col])

# Save cleaned file
output_path = "Dataset/cleaned_aqi_data.xlsx"
df.to_excel(output_path, index=False)

print("✅ Preprocessing done! File saved:", output_path)
import pandas as pd
import os

# Dataset folder path
folder_path = os.path.dirname(__file__)

# Only original files (cleaned_ avoid cheyyadaniki)
files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx") and not f.startswith("cleaned_")]

print("Files found:", files)

# Function: fill null with previous 3 values mean
def fill_with_prev_mean(series):
    for i in range(len(series)):
        if pd.isna(series[i]):
            prev_vals = series[max(0, i-3):i]
            series[i] = prev_vals.mean()
    return series

# Loop through all files
for file in files:
    print(f"\nProcessing: {file}")

    file_path = os.path.join(folder_path, file)
    df = pd.read_excel(file_path)

    # Convert numeric columns
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Apply preprocessing
    for col in df.columns[1:]:
        df[col] = fill_with_prev_mean(df[col])

    # Save cleaned file
    output_file = os.path.join(folder_path, "cleaned_" + file)
    df.to_excel(output_file, index=False)

    print(f"Saved: cleaned_{file}")

print("\n✅ All months processed successfully!")
import pandas as pd
import os

# Dataset folder
folder_path = os.path.dirname(__file__)

# Only cleaned files
files = [f for f in os.listdir(folder_path) if f.startswith("cleaned_")]

print("Processing files:", files)

for file in files:
    print(f"\nProcessing: {file}")

    file_path = os.path.join(folder_path, file)
    df = pd.read_excel(file_path)

    # All hourly columns (skip first column which is date/day)
    hourly_cols = df.columns[1:]

    # Calculate daily average AQI
    df["daily_avg_aqi"] = df[hourly_cols].mean(axis=1)

    # Save file
    output_file = os.path.join(folder_path, "daily_" + file)
    df.to_excel(output_file, index=False)

    print(f"Saved: daily_{file}")

print("\n✅ Daily AQI calculated for all months!")
import pandas as pd
import os

# Dataset folder
folder_path = os.path.dirname(__file__)

# Only cleaned files
files = [f for f in os.listdir(folder_path) if f.startswith("cleaned_")]

print("Processing files:", files)

for file in files:
    print(f"\nProcessing: {file}")

    file_path = os.path.join(folder_path, file)
    df = pd.read_excel(file_path)

    # First column (date/day)
    date_col = df.columns[0]

    # Hourly columns
    hourly_cols = df.columns[1:]

    # Calculate daily average
    df["daily_avg_aqi"] = df[hourly_cols].mean(axis=1)

    # Keep only date + avg
    df = df[[date_col, "daily_avg_aqi"]]

    # Save back to SAME file (overwrite)
    df.to_excel(file_path, index=False)

    print(f"Updated (overwritten): {file}")

print("\n✅ All files updated (hours removed, only daily avg kept)!")
import os

# Dataset folder path
folder_path = os.path.dirname(__file__)

files = os.listdir(folder_path)

for file in files:
    # Only delete non-cleaned Excel files
    if file.endswith(".xlsx") and not file.startswith("cleaned_"):
        file_path = os.path.join(folder_path, file)
        os.remove(file_path)
        print(f"Deleted: {file}")

print("\n✅ Only cleaned_ files are kept!")
import pandas as pd
import os

# Dataset folder path
folder_path = os.path.dirname(__file__)

# Only cleaned files
files = [f for f in os.listdir(folder_path) if f.startswith("cleaned_")]

for file in files:
    print(f"Processing: {file}")

    file_path = os.path.join(folder_path, file)

    # Read file
    df = pd.read_excel(file_path)

    # Add columns (same for all files)
    df["gwalior"] = 1
    df["jabalpur"] = 0
    df["delhi"] = 0

    # 🔥 IMPORTANT: overwrite SAME file
    df.to_excel(file_path, index=False)

    print(f"Updated (same file): {file}")

print("\n✅ Done! No new files created.")
import pandas as pd
import os

# Dataset folder
folder_path = os.path.dirname(__file__)

# Month mapping
month_map = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12
}

# Only cleaned files
files = [f for f in os.listdir(folder_path) if f.startswith("cleaned_")]

for file in files:
    print(f"Processing: {file}")

    file_path = os.path.join(folder_path, file)
    df = pd.read_excel(file_path)

    # Detect month from file name
    file_lower = file.lower()

    month_value = None
    for month_name, num in month_map.items():
        if month_name in file_lower:
            month_value = num
            break

    # Add month column (same value for all rows)
    df["month"] = month_value

    # Save back to SAME file (overwrite)
    df.to_excel(file_path, index=False)

    print(f"Updated: {file} → month = {month_value}")

print("\n✅ Month column added to all files!")

