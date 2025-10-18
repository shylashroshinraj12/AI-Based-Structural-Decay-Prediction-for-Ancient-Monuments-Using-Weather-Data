# app.py - Temple Decay Risk Prediction (Map-based)
import pandas as pd
import streamlit as st
import joblib
import requests
import os
from datetime import datetime
import folium
from streamlit_folium import st_folium

# ------------------- Config -------------------
API_KEY = "d4fd911924b0caa3e4391946e3d8ff08"  # OpenWeather API key
MODEL_PATH = "model.pkl"
HISTORY_PATH = "data/location_history.csv"
os.makedirs("data", exist_ok=True)

st.set_page_config(page_title="Temple Decay Risk", layout="wide")
st.title("Temple Decay Risk Prediction (Map Input)")

# ------------------- Step 1: Map for Location Selection -------------------
st.subheader("Click on the Map to Select a Location")
m = folium.Map(location=[10.0, 78.0], zoom_start=6)
map_data = st_folium(m, width=700, height=500)

lat, lon = None, None
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"Selected Location: {lat:.4f}, {lon:.4f}")

# ------------------- Step 2: Fetch Weather & Predict -------------------
if lat and lon and st.button("Get Weather & Predict Decay Risk"):
    try:
        # Fetch current weather
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()

        weather_info = {
            "Date": datetime.utcnow(),
            "Lat": lat,
            "Lon": lon,
            "Temp": data["main"]["temp"],
            "Humidity": data["main"]["humidity"],
            "Pressure": data["main"]["pressure"],
            "Rain": data.get("rain", {}).get("1h", 0)
        }
        st.subheader("Current Weather Data")
        st.json(weather_info)

        # Load model
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            input_df = pd.DataFrame([[
                weather_info["Temp"],
                weather_info["Humidity"],
                weather_info["Pressure"],
                weather_info["Rain"]
            ]], columns=["Temp_Avg", "Humidity_Avg", "Pressure", "Rain"])

            # Predict decay risk
            prediction = model.predict(input_df)[0]
            st.success(f"Predicted Decay Risk: **{prediction}** ✅")
            weather_info["Decay_Risk"] = prediction

            # ------------------- Step 3: Save History -------------------
            if os.path.exists(HISTORY_PATH):
                history_df = pd.read_csv(HISTORY_PATH)
            else:
                history_df = pd.DataFrame()
            history_df = pd.concat([history_df, pd.DataFrame([weather_info])], ignore_index=True)
            history_df.to_csv(HISTORY_PATH, index=False)

            # ------------------- Step 4: Plot Decay Risk Over Time -------------------
            st.subheader("Decay Risk Over Time for this Location")
            loc_history = history_df[
                (history_df["Lat"].round(4) == round(lat,4)) &
                (history_df["Lon"].round(4) == round(lon,4))
            ]
            if not loc_history.empty:
                loc_history["Date"] = pd.to_datetime(loc_history["Date"])
                risk_map = {"Low": 1, "Medium": 2, "High": 3}
                loc_history["Risk_Num"] = loc_history["Decay_Risk"].map(risk_map)
                st.line_chart(loc_history.set_index("Date")["Risk_Num"])
                st.write("Risk scale: 1 = Low, 2 = Medium, 3 = High")
            else:
                st.info("No historical data for this location yet.")

        else:
            st.warning("Model not found. Run train_model.py first.")

    except requests.RequestException as e:
        st.error(f"Failed to fetch weather: {e}")
    except Exception as e:
        st.error(f"Error: {e}")
