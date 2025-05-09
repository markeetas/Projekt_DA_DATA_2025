import pandas as pd

df = pd.read_csv("cleaned_hend_radiation_only.csv")

# Check if the latitude and longitude are on the grid


def is_on_grid(series):
    return ((series - 2.5) % 5 == 0).all()


print("Latitude OK:", is_on_grid(df["AREOCENTRIC_LATITUDE"]))
print("Longitude OK:", is_on_grid(df["AREOCENTRIC_EAST_LONGITUDE"]))
