# preprocess.py (refactored for dynamic locations)
import pandas as pd
import os

input_path = "data/weather_data.csv"
output_path = "data/processed_data.csv"

if not os.path.exists(input_path):
    raise FileNotFoundError("Run fetch_weather_free.py first to get weather_data.csv")

df = pd.read_csv(input_path)

# Ensure Lat/Lon columns exist for dynamic locations
if not {'Lat', 'Lon'}.issubset(df.columns):
    raise ValueError("weather_data.csv must contain 'Lat' and 'Lon' columns")

# Use rolling average with min_periods=1 so small datasets still work
df["Temp_Avg"] = df.groupby(["Location"])["Temp"].rolling(2, min_periods=1).mean().reset_index(0, drop=True)
df["Humidity_Avg"] = df.groupby(["Location"])["Humidity"].rolling(2, min_periods=1).mean().reset_index(0, drop=True)

# Calculate decay risk based on humidity
df["Decay_Risk"] = df["Humidity_Avg"].apply(
    lambda h: "High" if h > 85 else ("Medium" if h > 65 else "Low")
)

# Save processed data
df.to_csv(output_path, index=False)
print(f"Data preprocessed and saved to {output_path}")
