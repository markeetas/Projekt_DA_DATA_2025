import xarray as xr
import numpy as np
import pandas as pd
import glob
import os

# Set the directory containing the MCD scenario NetCDF files
scenario_dir = r"C:\Users\marke\DA_Projekt\MCD_test\MCD_6.1\data\clim_aveEUV"

# Find the first .NC file that contains the "Temperature" variable
nc_files = glob.glob(os.path.join(scenario_dir, "*.nc"))
temp_file = None
for fn in nc_files:
    try:
        ds0 = xr.open_dataset(fn, decode_times=False)
        if "Temperature" in ds0:
            temp_file = fn
            ds0.close()
            break
        ds0.close()
    except Exception:
        continue

#If no valid file was found, stop the script
if temp_file is None:
    raise RuntimeError("No file with 'Temperature'.")

# Open the dataset
ds = xr.open_dataset(temp_file, decode_times=False, chunks={})

# Drop unnecessary "time" variable if it exists
if "time" in ds:
    ds = ds.drop_vars("time")

# Convert longitude coordinates from [-180, 180] to [0, 360] and sort by longitude
ds = ds.assign_coords(
    Longitude=(ds.Longitude + 360) % 360
).sortby("Longitude")

# Select surface level temperature (Altitude = 0)
temp_surf = ds["Temperature"].isel(Altitude=0)  # dimy: Ls, Lt, Lat, Lon

# Average over Solar Longitude (Ls) and Local Time (Lt) to get annual mean surface temperature
temp_avg = temp_surf.mean(dim=["Solar_Longitude", "Local_Time"])

# Create a new regular 5x5°grid for interpolation
new_lon = np.arange(0, 360, 5)
new_lat = np.arange(-90,  95, 5)

# Interpolate the average temperature to the new grid
temp5 = temp_avg.interp(Longitude=new_lon, Latitude=new_lat)

# Convert to DataFrame and add Celsius temperature
df = temp5.to_dataframe(name="T_K").reset_index()
df["T_C"] = df["T_K"] - 273.15

# Save to CSV
out_dir = r"C:\Users\marke\DA_Projekt\Výstupy"
os.makedirs(out_dir, exist_ok=True)
csv_path = os.path.join(out_dir, "MCD_avg_surface_T_5x5.csv")
df.to_csv(csv_path, index=False)

print(f"CSV saved: {csv_path}")
print(df.head())
