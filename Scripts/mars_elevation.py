import numpy as np
import pandas as pd

# Parameters and loading MOLA topography 
img_path = r"E:\DATA VECI\Elevace\megt90n000fb.img"
nrows, ncols = 5760, 11520  # 180°×32 a 360°×32

# Load the entire elevation matrix
arr = np.fromfile(img_path, dtype=">i2").reshape((nrows, ncols))

# Size of a 5°×5° tile in pixels
pixel_per_degree = 32
bh, bw = 5 * pixel_per_degree, 5 * pixel_per_degree  # 160 × 160

# Number of tiles in lat and lon directions
lat_cells = nrows // bh   # 36
lon_cells = ncols // bw   # 72

# Crop the matrix to full blocks
arr_cut = arr[:lat_cells * bh, :lon_cells * bw]

# Reshape to (lat_cells, bh, lon_cells, bw) and compute the mean
coarse_mean = arr_cut.reshape(lat_cells, bh, lon_cells, bw).mean(axis=(1, 3))

# Compute center coordinates of the 5° tiles
lat_centers = 90 - ((np.arange(lat_cells) * bh + bh / 2) / nrows) * 180
lon_centers = ((np.arange(lon_cells) * bw + bw / 2) / ncols) * 360

# Construct the DataFrame
lat_rep = np.repeat(lat_centers, lon_cells)
lon_rep = np.tile(   lon_centers,    lat_cells)
elev_rep = coarse_mean.ravel()

df5mean = pd.DataFrame({
    "latitude":   lat_rep,
    "longitude":  lon_rep,
    "elevation_m": elev_rep
})

# Round elevations to integers
df5mean["elevation_m"] = df5mean["elevation_m"].round().astype(int)
# Round coordinates to one decimal place
df5mean["latitude"]  = df5mean["latitude"].round(1)
df5mean["longitude"] = df5mean["longitude"].round(1)

# Save to CSV
output_csv = r"E:\DATA VECI\Elevace\elevation.csv"
df5mean.to_csv(output_csv, index=False, float_format="%.1f")

print(f"elevation_5deg_mean.csv saved with integer elevations, rows: {len(df5mean)}")



