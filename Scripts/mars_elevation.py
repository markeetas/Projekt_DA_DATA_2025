import numpy as np
import pandas as pd

# 1) Parametry a načtení MOLA topografie (32 px/°)
img_path = r"E:\DATA VECI\Elevace\megt90n000fb.img"
nrows, ncols = 5760, 11520  # 180°×32 a 360°×32

# Načti celou matici elevation
arr = np.fromfile(img_path, dtype=">i2").reshape((nrows, ncols))

# 2) Velikost 5°×5° buňky v pixelech
pixel_per_degree = 32
bh, bw = 5 * pixel_per_degree, 5 * pixel_per_degree  # 160 × 160

# 3) Počet buněk v lat/lon směru
lat_cells = nrows // bh   # 36
lon_cells = ncols // bw   # 72

# 4) Oříznutí matice na celé bloky
arr_cut = arr[:lat_cells * bh, :lon_cells * bw]

# 5) Přetvoření do (lat_cells, bh, lon_cells, bw) a průměr
coarse_mean = arr_cut.reshape(lat_cells, bh, lon_cells, bw).mean(axis=(1, 3))

# 6) Výpočet středových souřadnic 5° buněk
lat_centers = 90 - ((np.arange(lat_cells) * bh + bh / 2) / nrows) * 180
lon_centers = ((np.arange(lon_cells) * bw + bw / 2) / ncols) * 360

# 7) Sestavení DataFrame
lat_rep = np.repeat(lat_centers, lon_cells)
lon_rep = np.tile(   lon_centers,    lat_cells)
elev_rep = coarse_mean.ravel()

df5mean = pd.DataFrame({
    "latitude":   lat_rep,
    "longitude":  lon_rep,
    "elevation_m": elev_rep
})

# 8) Zaokrouhlení elevation na celá čísla
df5mean["elevation_m"] = df5mean["elevation_m"].round().astype(int)

df5mean["latitude"]  = df5mean["latitude"].round(1)
df5mean["longitude"] = df5mean["longitude"].round(1)
# 9) Uložení výsledku do CSV
output_csv = r"E:\DATA VECI\Elevace\elevation.csv"
df5mean.to_csv(output_csv, index=False, float_format="%.1f")

print(f"✅ elevation_5deg_mean.csv uložen s celými elevacemi, řádků: {len(df5mean)}")



