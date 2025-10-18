# fetch_weather_free.py (refactored for dynamic coordinates)
import requests
import pandas as pd
from datetime import datetime
import os

API_KEY = "d4fd911924b0caa3e4391946e3d8ff08"

# Example: dynamic locations list (can be replaced with map click lat/lon)
locations = [
    {"name": "Madurai_Meenakshi", "lat": 9.9195, "lon": 78.1193},
    {"name": "Thanjavur_Big", "lat": 10.7847, "lon": 79.1378},
    # You can dynamically append more {"name": "Custom Location", "lat": xx, "lon": yy}
]

os.makedirs("data", exist_ok=True)
data_list = []

for loc in locations:
    lat, lon = loc['lat'], loc['lon']
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }

    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        data_list.append({
            "Location": loc['name'],
            "Lat": lat,
            "Lon": lon,
            "Date": datetime.utcfromtimestamp(data["dt"]).strftime('%Y-%m-%d %H:%M:%S'),
            "Temp": data["main"]["temp"],
            "Humidity": data["main"]["humidity"],
            "Pressure": data["main"]["pressure"],
            "Rain": data.get("rain", {}).get("1h", 0)
        })
        print(f"Weather fetched for {loc['name']}")
    else:
        print(f"Failed for {loc['name']}: {r.status_code}")

# Save to CSV
df = pd.DataFrame(data_list)
df.to_csv("data/weather_data.csv", index=False)
print("Weather data saved to data/weather_data.csv")
