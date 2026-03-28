"""
Run this file ONCE to train XGBoost and save pkl files.
Place this file inside: nexus/Model_training/
Run: python train_model.py
It will create: nexus/model/model.pkl, features.pkl, last_known.pkl
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

# ── 1. Load dataset ──────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
df = pd.read_excel(os.path.join(BASE, "final_dataset.xlsx"))

# ── 2. Clean ─────────────────────────────────────────────────────────────────
df = df.drop(columns=["Unnamed: 0", "city.1"], errors="ignore")
df = df.dropna(subset=["AQI_t-1", "AQI_t-2", "AQI_t-3"])
df = df.ffill().bfill()

# ── 3. Features & Target ─────────────────────────────────────────────────────
FEATURES = [
    "Month", "Delhi", "Gwalior", "Jabalpur",
    "day", "day_of_week", "city",
    "AQI_t-1", "AQI_t-2", "AQI_t-3",
    "humidity", "precip", "windspeed", "temp©"
]

X = df[FEATURES]
y = df["AQI"]

# ── 4. Train/Test split (time-series style) ───────────────────────────────────
split = int(0.8 * len(df))
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

# ── 5. Train XGBoost ──────────────────────────────────────────────────────────
model = XGBRegressor(
    n_estimators=800,
    learning_rate=0.03,
    max_depth=6,
    subsample=0.85,
    colsample_bytree=0.85,
    gamma=0.5,
    reg_alpha=0.1,
    reg_lambda=1.5,
    random_state=42
)
model.fit(X_train, y_train)

# ── 6. Evaluate ───────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)

print("\n📊 MODEL PERFORMANCE")
print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R2   : {r2:.4f}")

# ── 7. Save last known values per city (for prediction) ───────────────────────
def last_row(city_col):
    return df[df[city_col] == 1].iloc[-1]

last_known = {
    "Delhi": {
        "AQI_t-1": last_row("Delhi")["AQI_t-1"],
        "AQI_t-2": last_row("Delhi")["AQI_t-2"],
        "AQI_t-3": last_row("Delhi")["AQI_t-3"],
        "humidity":  last_row("Delhi")["humidity"],
        "precip":    last_row("Delhi")["precip"],
        "windspeed": last_row("Delhi")["windspeed"],
        "temp©":     last_row("Delhi")["temp©"],
    },
    "Gwalior": {
        "AQI_t-1": last_row("Gwalior")["AQI_t-1"],
        "AQI_t-2": last_row("Gwalior")["AQI_t-2"],
        "AQI_t-3": last_row("Gwalior")["AQI_t-3"],
        "humidity":  last_row("Gwalior")["humidity"],
        "precip":    last_row("Gwalior")["precip"],
        "windspeed": last_row("Gwalior")["windspeed"],
        "temp©":     last_row("Gwalior")["temp©"],
    },
    "Jabalpur": {
        "AQI_t-1": last_row("Jabalpur")["AQI_t-1"],
        "AQI_t-2": last_row("Jabalpur")["AQI_t-2"],
        "AQI_t-3": last_row("Jabalpur")["AQI_t-3"],
        "humidity":  last_row("Jabalpur")["humidity"],
        "precip":    last_row("Jabalpur")["precip"],
        "windspeed": last_row("Jabalpur")["windspeed"],
        "temp©":     last_row("Jabalpur")["temp©"],
    },
}

# Historical last 7 days per city (for chart)
historical = {}
for city, col in [("Delhi", "Delhi"), ("Gwalior", "Gwalior"), ("Jabalpur", "Jabalpur")]:
    sub = df[df[col] == 1].tail(7)
    historical[city] = sub["AQI"].round(1).tolist()

# ── 8. Save pkl files ─────────────────────────────────────────────────────────
model_dir = os.path.join(BASE, "..", "model")
os.makedirs(model_dir, exist_ok=True)

joblib.dump(model,       os.path.join(model_dir, "model.pkl"))
joblib.dump(FEATURES,    os.path.join(model_dir, "features.pkl"))
joblib.dump(last_known,  os.path.join(model_dir, "last_known.pkl"))
joblib.dump(historical,  os.path.join(model_dir, "historical.pkl"))

print("\n✅ model.pkl     saved")
print("✅ features.pkl  saved")
print("✅ last_known.pkl saved")
print("✅ historical.pkl saved")
print(f"\nSaved to: {os.path.abspath(model_dir)}")
