# train_model.py (refactored for dynamic locations)
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

csv_path = "data/processed_data.csv"

# --- Step 1: Check if file exists ---
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"{csv_path} not found. Please run preprocess.py first.")

# --- Step 2: Load dataset ---
df = pd.read_csv(csv_path)

if df.empty:
    raise ValueError(f"{csv_path} is empty. Make sure fetch_weather_free.py and preprocess.py ran correctly.")

# --- Step 3: Select features & target ---
# We train only on weather features, ignore Lat/Lon for model
features = ["Temp_Avg", "Humidity_Avg", "Pressure", "Rain"]
X = df[features]
y = df["Decay_Risk"]

# --- Step 4: Handle small datasets ---
if len(df) < 5:
    print("Warning: Not enough real data to train the model.")
    print("Duplicating rows just for testing. Please collect more weather data for real accuracy.\n")
    df = pd.concat([df] * 20, ignore_index=True)
    X = df[features]
    y = df["Decay_Risk"]

# --- Step 5: Train/Test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --- Step 6: Train model ---
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# --- Step 7: Predictions & Report ---
y_pred = model.predict(X_test)
print("Model Training Complete")
print(classification_report(y_test, y_pred))

# --- Step 8: Save model ---
joblib.dump(model, "model.pkl")
print("Model saved as model.pkl and ready for map-based predictions")
