import os
import json
import sqlite3
import smtplib
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
DB = "airsense.db"

# ── City mapping ──────────────────────────────────────────────────────────────
CITY_NUM = {"Delhi": 1, "Gwalior": 2, "Jabalpur": 3}
CITY_COL = {"Delhi": "Delhi", "Gwalior": "Gwalior", "Jabalpur": "Jabalpur"}

# ── Load model & data ─────────────────────────────────────────────────────────
MODEL      = None
FEATURES   = None
LAST_KNOWN = None
HISTORICAL = None

def load_model():
    global MODEL, FEATURES, LAST_KNOWN, HISTORICAL
    try:
        MODEL      = joblib.load("model/model.pkl")
        FEATURES   = joblib.load("model/features.pkl")
        LAST_KNOWN = joblib.load("model/last_known.pkl")
        HISTORICAL = joblib.load("model/historical.pkl")
        print("✅ Model loaded successfully.")
    except Exception as e:
        print(f"❌ Model not found: {e}")
        print("   Run Model_training/train_model.py first.")

# ── Database ──────────────────────────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            city TEXT,
            age_group TEXT,
            gender TEXT,
            lung_issue TEXT,
            threshold INTEGER DEFAULT 150,
            created_at TEXT
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS advisories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT UNIQUE,
            message TEXT,
            updated_at TEXT
        )
    """)
    con.commit()
    con.close()

# ── AQI category (CPCB standard) ──────────────────────────────────────────────
def aqi_category(aqi):
    if aqi is None:
        return "Unknown", "#7a8099"
    aqi = int(aqi)
    if aqi <= 50:   return "Good",        "#4ade80"
    if aqi <= 100:  return "Satisfactory","#a3e635"
    if aqi <= 200:  return "Moderate",    "#facc15"
    if aqi <= 300:  return "Poor",        "#f97316"
    if aqi <= 400:  return "Very Poor",   "#ef4444"
    return "Severe", "#9333ea"

# ── Prediction using XGBoost ──────────────────────────────────────────────────
def predict_tomorrow(city):
    if MODEL is None or LAST_KNOWN is None:
        return None, None

    lk = LAST_KNOWN.get(city, {})
    today_aqi = lk.get("AQI_t-1", 150)  # last known AQI = today

    tomorrow = datetime.now() + timedelta(days=1)

    row = {
        "Month":       float(tomorrow.month),
        "Delhi":       1.0 if city == "Delhi"    else 0.0,
        "Gwalior":     1.0 if city == "Gwalior"  else 0.0,
        "Jabalpur":    1.0 if city == "Jabalpur" else 0.0,
        "day":         float(tomorrow.day),
        "day_of_week": float(tomorrow.weekday()),
        "city":        float(CITY_NUM.get(city, 1)),
        "AQI_t-1":     lk.get("AQI_t-1", today_aqi),
        "AQI_t-2":     lk.get("AQI_t-2", today_aqi),
        "AQI_t-3":     lk.get("AQI_t-3", today_aqi),
        "humidity":    lk.get("humidity",  65.0),
        "precip":      lk.get("precip",    0.0),
        "windspeed":   lk.get("windspeed", 10.0),
        "temp©":       lk.get("temp©",     22.0),
    }

    X = pd.DataFrame([row])[FEATURES]
    pred = float(MODEL.predict(X)[0])
    pred = max(0, round(pred))

    # Confidence: based on AQI stability in last 3 days
    variance = abs(lk.get("AQI_t-1", today_aqi) - lk.get("AQI_t-2", today_aqi))
    confidence = max(60, min(95, int(90 - variance * 0.4)))

    return pred, confidence

# ── Today's AQI from last known data ─────────────────────────────────────────
def get_today_aqi(city):
    if LAST_KNOWN is None:
        return 150
    lk = LAST_KNOWN.get(city, {})
    return int(round(lk.get("AQI_t-1", 150)))

# ── Historical 7-day + predicted 3-day chart data ────────────────────────────
def get_chart_data(city, today_aqi, tomorrow_aqi):
    # Past 7 days from dataset
    if HISTORICAL and city in HISTORICAL:
        past_values = HISTORICAL[city]  # list of 7 AQI values
    else:
        past_values = [today_aqi] * 7

    # Past 7 day labels (Dec 25 – Dec 31 from dataset)
    past_labels = [
        (datetime(2025, 12, 25) + timedelta(days=i)).strftime("%d %b")
        for i in range(7)
    ]

    # Future 3 days from today
    future_labels = [
        (datetime.now() + timedelta(days=i)).strftime("%d %b")
        for i in range(1, 4)
    ]

    # Future predictions: tomorrow from model, day+2 and day+3 estimated
    t2 = max(0, round(tomorrow_aqi * 0.97)) if tomorrow_aqi else today_aqi
    t3 = max(0, round(tomorrow_aqi * 0.94)) if tomorrow_aqi else today_aqi
    future_values = [tomorrow_aqi or today_aqi, t2, t3]

    # Chart datasets: past has None at end, future has None at start
    past_chart   = past_values + [None, None, None]
    future_chart = [None] * 7 + future_values

    return {
        "labels":  past_labels + future_labels,
        "past":    past_chart,
        "future":  future_chart,
    }

# ── Health advice (rule-based, CPCB guidelines) ───────────────────────────────
def health_advice(aqi, age_group, gender, lung_issue):
    tips = []

    if aqi <= 50:
        tips.append("Air quality is Good. Enjoy outdoor activities freely.")
    elif aqi <= 100:
        tips.append("Air quality is Satisfactory. Outdoor activities are safe for most people.")
    elif aqi <= 200:
        tips.append("Moderate AQI. Sensitive individuals should reduce prolonged outdoor exertion.")
        tips.append("Keep windows slightly open for ventilation.")
    elif aqi <= 300:
        tips.append("Poor AQI. Avoid outdoor activities during peak hours (10am–4pm).")
        tips.append("Keep windows closed. Use air purifier if available.")
    elif aqi <= 400:
        tips.append("Very Poor AQI. Avoid all outdoor activities.")
        tips.append("Stay indoors. Keep doors and windows shut.")
        tips.append("Wear N95 mask if going outside is unavoidable.")
    else:
        tips.append("Severe AQI — Emergency level. Do NOT go outside.")
        tips.append("Seal gaps in doors and windows.")
        tips.append("Seek medical attention if you feel breathlessness.")

    # Lung / breathing issue
    if lung_issue == "yes":
        tips.append("Carry your inhaler or prescribed medication at all times.")
        if aqi > 100:
            tips.append("Wear N95 mask even for short outdoor trips.")
        if aqi > 200:
            tips.append("Contact your doctor if symptoms worsen.")

    # Age group
    if age_group == "child":
        if aqi > 100:
            tips.append("Keep children indoors. Avoid outdoor play.")
        if aqi > 200:
            tips.append("School outdoor activities should be cancelled.")
    elif age_group == "elderly":
        if aqi > 100:
            tips.append("Elderly persons should avoid going outside.")
        if aqi > 200:
            tips.append("Monitor blood pressure and breathing closely.")

    # Gender specific (pregnancy risk)
    if gender == "female" and aqi > 150:
        tips.append("Pregnant women should stay indoors and consult a doctor if needed.")

    return tips

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/aqi")
def api_aqi():
    city = request.args.get("city", "Gwalior")

    today_aqi              = get_today_aqi(city)
    tomorrow_aqi, conf     = predict_tomorrow(city)
    today_cat, today_color = aqi_category(today_aqi)
    tmr_cat, tmr_color     = aqi_category(tomorrow_aqi)
    chart                  = get_chart_data(city, today_aqi, tomorrow_aqi)

    # Government advisory from DB
    con = sqlite3.connect(DB)
    row = con.execute("SELECT message FROM advisories WHERE city=?", (city,)).fetchone()
    con.close()
    advisory = row[0] if row else None

    return jsonify({
        "city": city,
        "today": {
            "aqi":      today_aqi,
            "category": today_cat,
            "color":    today_color,
        },
        "tomorrow": {
            "aqi":        tomorrow_aqi,
            "category":   tmr_cat,
            "color":      tmr_color,
            "confidence": conf,
        },
        "chart":    chart,
        "advisory": advisory,
    })

@app.route("/api/health_advice")
def api_health():
    aqi    = int(request.args.get("aqi", 150))
    age    = request.args.get("age_group", "adult")
    gender = request.args.get("gender", "other")
    lung   = request.args.get("lung_issue", "no")

    tips       = health_advice(aqi, age, gender, lung)
    cat, color = aqi_category(aqi)

    return jsonify({"tips": tips, "category": cat, "color": color})

@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    d = request.json
    if not d.get("name") or not d.get("email"):
        return jsonify({"ok": False, "msg": "Name and email are required."}), 400
    try:
        con = sqlite3.connect(DB)
        con.execute("""
            INSERT OR REPLACE INTO subscribers
            (name, email, city, age_group, gender, lung_issue, threshold, created_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            d["name"], d["email"], d.get("city", "Gwalior"),
            d.get("age_group", "adult"), d.get("gender", "other"),
            d.get("lung_issue", "no"), int(d.get("threshold", 150)),
            datetime.now().isoformat()
        ))
        con.commit()
        con.close()
        return jsonify({"ok": True, "msg": "Subscribed successfully! 🎉"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 400

@app.route("/api/advisory", methods=["POST"])
def post_advisory():
    secret = request.json.get("secret", "")
    if secret != os.environ.get("ADMIN_SECRET", "admin123"):
        return jsonify({"ok": False, "msg": "Unauthorized"}), 403
    city = request.json.get("city")
    msg  = request.json.get("message")
    if not city or not msg:
        return jsonify({"ok": False, "msg": "city and message required"}), 400
    con = sqlite3.connect(DB)
    con.execute(
        "INSERT OR REPLACE INTO advisories (city, message, updated_at) VALUES (?,?,?)",
        (city, msg, datetime.now().isoformat())
    )
    con.commit()
    con.close()
    return jsonify({"ok": True, "msg": f"Advisory set for {city}"})

# ── Email alerts ──────────────────────────────────────────────────────────────
def send_alerts():
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASS = os.environ.get("SMTP_PASS", "")

    if not SMTP_USER:
        return

    con  = sqlite3.connect(DB)
    subs = con.execute("SELECT * FROM subscribers").fetchall()
    con.close()

    for sub in subs:
        _, name, email, city, age_group, gender, lung_issue, threshold, _ = sub
        today_aqi = get_today_aqi(city)
        if today_aqi < threshold:
            continue

        tips    = health_advice(today_aqi, age_group, gender, lung_issue)
        cat, _  = aqi_category(today_aqi)
        tip_str = "\n".join(f"  • {t}" for t in tips)

        body = f"""Hello {name},

⚠️ AQI Alert for {city}: {today_aqi} ({cat})

Your personalised health tips:
{tip_str}

Stay safe,
AirSense Team
"""
        try:
            msg             = MIMEText(body)
            msg["Subject"]  = f"⚠️ AQI Alert: {city} — {today_aqi} ({cat})"
            msg["From"]     = SMTP_USER
            msg["To"]       = email
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
            print(f"Alert sent to {email}")
        except Exception as e:
            print(f"Email failed for {email}: {e}")

# ── Start ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    load_model()
    app.run(debug=True)
