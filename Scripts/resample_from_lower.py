# Resample lower-resolution data to a 5x5° grid and normalize the values

import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('t_sd_global_average.csv')  

# Rename columns for clarity
df = df.rename(columns={
    "Longitude": "lon",
    "Latitude": "lat",
    "Temperature_sd": "temp_sd"
})

# Convert coordinates to a 5x5° grid centered at 2.5°
df["lon_grid"] = (np.floor(df["lon"] / 5) * 5 + 2.5) % 360
df["lat_grid"] = (np.floor(df["lat"] / 5) * 5 + 2.5)

# Group values by each grid cell and compute the mean temperature_sd per cell
grid = df.groupby(["lat_grid", "lon_grid"]).agg({
    "temp_sd": "mean"
}).reset_index()

# Rename for clarity
grid = grid.rename(columns={"lat_grid": "lat", "lon_grid": "lon"})

# Normalize each variable to range [0, 1]
for col in ["temp_sd"]:
    grid[f"{col}_norm"] = (grid[col] - grid[col].min()) / (grid[col].max() - grid[col].min())

# Keep only final columns
final = grid[["lat", "lon", "temp_sd_norm"]]
# Save the final dataset
grid.to_csv("tsd_resampled_5x5_normalized.csv", index=False)

