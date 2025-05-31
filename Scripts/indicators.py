import pandas as pd
import os
from functools import reduce
from numpy import nan

# Function to load and standardize a dataset
def load_param(path, colname, newname=None):
    df = pd.read_csv(path)
    
    # Detect valid lat/lon column names
    lat_opts = ['lat', 'Lat', 'LATITUDE', 'Latitude', 'latitude']
    lon_opts = ['lon', 'Lon', 'LONGITUDE', 'Longitude', 'longitude']
    lat = next((c for c in lat_opts if c in df.columns), None)
    lon = next((c for c in lon_opts if c in df.columns), None)
    
    if lat is None or lon is None:
        raise ValueError(f"File {path} does not contain proper coordinates.")
    
    # Rename columns to standard format
    df = df.rename(columns={lat: "lat", lon: "lon"})
    df = df[["lat", "lon", colname]].rename(columns={colname: newname or colname})
    
    return df

# Parameters and their weights for composite indicators
params = {
    "Water": ("water_concentration_normalized.csv", "CONCENTRATION_NORM", 8),
    "Silicon": ("silicon_concentration_normalized.csv", "CONCENTRATION_NORM", 8),
    "Iron": ("iron_concentration_normalized.csv", "CONCENTRATION_NORM", 1),
    "Thorium": ("thorium_concentration_normalized.csv", "CONCENTRATION_NORM", 2),
    "Potassium": ("potassium_concentration_normalized.csv", "CONCENTRATION_NORM", 1),
    "Chlorine": ("chlorine_concentration_normalized.csv", "CONCENTRATION_NORM", 1),
    "Temp_Cold": ("mars_typical_temperatures_5x5_2.5start_normalized.csv", "cold_night_C_NORM", 3),
    "Dust_storms": ("storm_summary_5x5_days_normalized.csv", "stormy_days_normalized", 4),
    "Radiation": ("mars_grid_radiation2.csv", "dose_e_norm", 4),
    "Temp_Sd": ("mars_temperature_average_2.5start_normalized.csv", "annual_range_C_NORM", 3),
    "Temp_Avg": ("mars_temperature_average_2.5start_normalized.csv", "annual_avg_C_NORM", 1),
}

# Load all datasets as a list
frames = []
for name, (path, col, _) in params.items():
    df = load_param(os.path.join("C:/Users/marke", path), col, name)
    frames.append(df)

# Merge all DataFrames on lat/lon using outer join
full = reduce(lambda left, right: pd.merge(left, right, on=["lat", "lon"], how="outer"), frames)

# Invert selected values
full["Radiation_INV"] = 1 - full["Radiation"]   
full["Thorium_INV"] = 1 - full["Thorium"]             

# Define sets of keys (parameters) 
industry_keys = ["Water", "Silicon", "Iron", "Thorium", "Potassium", "Chlorine", "Temp_Cold", "Dust_storms", "Radiation"]
habit_keys = ["Water", "Radiation", "Thorium_INV", "Dust_storms", "Temp_Cold", "Temp_Sd", "Temp_Avg"]

# Extract weights 
industry_params = {k: params[k.replace("_INV", "")] for k in industry_keys}
habit_params = {k: params[k.replace("_INV", "")] for k in habit_keys}

# Compute weighted composite score and count of valid parameters used
def weighted_score_and_count(row, param_weights):
    values = []
    weights = []
    count = 0
    for param, (_, _, w) in param_weights.items():
        val = row.get(param)
        if pd.notna(val):
            values.append(val * w)
            weights.append(w)
            count += 1
    score = sum(values) / sum(weights) if weights else nan
    return round(score, 2), count

# Compute industry and habitability composite scores
full[["Industry_0_8", "Count_Industry"]] = full.apply(
    lambda row: pd.Series(weighted_score_and_count(row, industry_params)), axis=1
)
full[["Habitability_0_8", "Count_Habitability"]] = full.apply(
    lambda row: pd.Series(weighted_score_and_count(row, habit_params)), axis=1
)

# Round all values to two decimal places
full = full.round(2)

# Save the dataset 
output = "C:/Users/marke/composite_indicators.csv"
full.to_csv(output, index=False)