import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from scipy.spatial import cKDTree

# Load the Mars dataset with environmental parameters
df = pd.read_csv("final_dataset.csv")

# Load the Curiosity radiation dataset
df_curiosity = pd.read_csv("radiation_curiosity.csv",
                           encoding="utf-8", encoding_errors="ignore")

# Rename radiation columns to easier names (µ = micro symbol must be preserved)
df_curiosity = df_curiosity.rename(columns={
    "dose_b_µGy/h": "dose_b",
    "dose_e_µGy/h": "dose_e"
})

# Optional: check column names to verify renaming worked
print("Curiosity columns:", df_curiosity.columns.tolist())

# Curiosity rover location
lat0, lon0 = -4.7, 137.4

# Find the nearest row in the Mars dataset to Curiosity location
tree = cKDTree(df[["lat", "lon"]])
dist, idx = tree.query([[lat0, lon0]], k=1)
base_row = df.iloc[idx[0]]

# Define features for training
features = [
    "pressure", "pressure_norm",
    "EPITHERMAL_FLUX1_norm",
    "FAST_FLUX1_norm",
    "stormy_days_normalized",
    "elevation_m"
]

# Create synthetic samples around the base row by adding Gaussian noise
np.random.seed(42)
n = 500  # Number of synthetic training samples

X_syn = pd.DataFrame([
    base_row[features].values +
    np.random.normal(0, [5, 0.01, 0.01, 0.01, 0.01, 10], size=len(features))
    for _ in range(n)
], columns=features)

# Generate target values (radiation) around real Curiosity average values
y_dose_b = np.random.normal(df_curiosity["dose_b"].mean(), 0.1, size=n)
y_dose_e = np.random.normal(df_curiosity["dose_e"].mean(), 0.1, size=n)

# Train regression models for both radiation types
model_b = RandomForestRegressor(n_estimators=100, random_state=42)
model_e = RandomForestRegressor(n_estimators=100, random_state=42)

model_b.fit(X_syn, y_dose_b)
model_e.fit(X_syn, y_dose_e)

# Predict radiation for all locations on Mars
X_all = df[features]
df["predicted_dose_b"] = model_b.predict(X_all)
df["predicted_dose_e"] = model_e.predict(X_all)

# Save the final dataset with predictions
df.to_csv("mars_radiation_prediction.csv", index=False)
print("Final dataset with predicted radiation saved as 'mars_radiation_prediction.csv'")
