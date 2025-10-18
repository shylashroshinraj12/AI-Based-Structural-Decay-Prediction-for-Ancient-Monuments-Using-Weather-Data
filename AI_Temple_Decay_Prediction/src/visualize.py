# visualize.py (refactored for dynamic locations)
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium

df = pd.read_csv("data/processed_data.csv")

# --- Seaborn scatterplot (Weather vs Decay Risk) ---
plt.figure(figsize=(8,6))
sns.scatterplot(x="Humidity_Avg", y="Temp_Avg", hue="Decay_Risk", data=df, palette="coolwarm", s=100)
plt.title("Decay Risk by Weather")
plt.xlabel("Humidity (%)")
plt.ylabel("Temperature (°C)")
plt.show()

# --- Optional: Interactive map visualization using Folium ---
m = folium.Map(location=[df["Lat"].mean(), df["Lon"].mean()], zoom_start=6)

# Add markers with decay risk color
risk_colors = {"Low": "green", "Medium": "orange", "High": "red"}

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["Lat"], row["Lon"]],
        radius=7,
        color=risk_colors.get(row["Decay_Risk"], "blue"),
        fill=True,
        fill_opacity=0.7,
        popup=f"{row['Location']} - {row['Decay_Risk']}"
    ).add_to(m)

# Save interactive map
m.save("data/decay_risk_map.html")
print("Scatterplot shown and interactive map saved as data/decay_risk_map.html")
