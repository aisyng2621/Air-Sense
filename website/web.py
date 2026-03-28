import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import pickle
import time

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AQI Predict · BreatheSafe",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: #0a0f1e;
    color: #e8eaf0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d1424 !important;
    border-right: 1px solid rgba(99,179,237,0.15);
}
[data-testid="stSidebar"] * { color: #c5cfe0 !important; }

/* Headings */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2234 100%);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.metric-card:hover { border-color: rgba(99,179,237,0.5); transform: translateY(-2px); }
.metric-title { font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; color: #7a8ba0; margin-bottom: 8px; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 2.8rem; font-weight: 800; line-height: 1; }
.metric-sub { font-size: 0.8rem; color: #7a8ba0; margin-top: 6px; }

/* AQI Level colors */
.aqi-good      { color: #22c55e; }
.aqi-moderate  { color: #eab308; }
.aqi-sensitive { color: #f97316; }
.aqi-unhealthy { color: #ef4444; }
.aqi-very      { color: #a855f7; }
.aqi-hazardous { color: #be123c; }

/* Advisory card */
.advisory-card {
    background: linear-gradient(135deg, #111827, #1e2a3a);
    border-radius: 16px;
    padding: 20px 24px;
    border-left: 4px solid #63b3ed;
    margin: 10px 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.advisory-card h4 { font-family:'Syne',sans-serif; margin:0 0 8px 0; color:#e2e8f0; }
.advisory-card p { margin:0; color:#94a3b8; font-size:0.88rem; line-height:1.6; }

/* Alert banner */
.alert-banner {
    background: linear-gradient(135deg, #7f1d1d, #450a0a);
    border: 1px solid #ef4444;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 16px 0;
    animation: pulse-border 2s ease-in-out infinite;
}
@keyframes pulse-border {
    0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
    50%      { box-shadow: 0 0 0 8px rgba(239,68,68,0); }
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: #111827 !important;
    border: 1px solid rgba(99,179,237,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* Section divider */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #93c5fd;
    letter-spacing: 1px;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(99,179,237,0.15);
    padding-bottom: 8px;
    margin: 20px 0 14px 0;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

AQI_LEVELS = [
    (0,   50,  "Good",                  "#22c55e", "aqi-good"),
    (51,  100, "Moderate",              "#eab308", "aqi-moderate"),
    (101, 150, "Unhealthy for Sensitive","#f97316","aqi-sensitive"),
    (151, 200, "Unhealthy",             "#ef4444", "aqi-unhealthy"),
    (201, 300, "Very Unhealthy",        "#a855f7", "aqi-very"),
    (301, 500, "Hazardous",             "#be123c", "aqi-hazardous"),
]

HEALTH_ADVISORIES = {
    "Good": {
        "general":    "Air quality is satisfactory. Enjoy outdoor activities.",
        "respiratory":"No restrictions. Safe for all respiratory conditions.",
        "exercise":   "Ideal for outdoor exercise and sports.",
        "children":   "Safe for children to play outside all day.",
        "elderly":    "No precautions needed.",
        "icon": "✅"
    },
    "Moderate": {
        "general":    "Air quality is acceptable. Unusually sensitive people may experience discomfort.",
        "respiratory":"Sensitive individuals should limit prolonged outdoor exertion.",
        "exercise":   "Consider reducing intensity of prolonged outdoor activities.",
        "children":   "Children with asthma should watch for symptoms.",
        "elderly":    "Elderly with heart/lung disease should limit outdoor exertion.",
        "icon": "⚠️"
    },
    "Unhealthy for Sensitive": {
        "general":    "Members of sensitive groups may experience health effects.",
        "respiratory":"Asthma/COPD patients: carry inhaler. Limit outdoor time.",
        "exercise":   "Avoid prolonged or heavy outdoor exertion.",
        "children":   "Limit outdoor playtime, especially for children with asthma.",
        "elderly":    "Elderly with breathing issues should stay indoors.",
        "icon": "🟠"
    },
    "Unhealthy": {
        "general":    "Everyone may begin to experience health effects.",
        "respiratory":"Use N95 mask outdoors. Take prescribed medicines as scheduled.",
        "exercise":   "Move workouts indoors. No intense outdoor exercise.",
        "children":   "Keep children indoors. Close school windows.",
        "elderly":    "Remain indoors with air purifier if available.",
        "icon": "🔴"
    },
    "Very Unhealthy": {
        "general":    "Health warnings of emergency conditions. Everyone is affected.",
        "respiratory":"Avoid all outdoor activity. Nebulize if prescribed.",
        "exercise":   "All outdoor exercise must be cancelled.",
        "children":   "Schools should cancel outdoor activities. Keep indoors.",
        "elderly":    "Stay indoors. Seek medical attention if breathing worsens.",
        "icon": "🟣"
    },
    "Hazardous": {
        "general":    "EMERGENCY CONDITIONS. Entire population likely affected.",
        "respiratory":"Seek medical help immediately if experiencing difficulty breathing.",
        "exercise":   "No outdoor activity whatsoever.",
        "children":   "Children must stay indoors. Close all windows/doors.",
        "elderly":    "Call emergency services if experiencing chest pain or shortness of breath.",
        "icon": "☣️"
    },
}

CITIES = [
    "Rajkot", "Ahmedabad", "Surat", "Vadodara", "Mumbai",
    "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad",
    "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur",
    "Custom City"
]

def get_aqi_info(aqi_value):
    for lo, hi, label, color, css in AQI_LEVELS:
        if lo <= aqi_value <= hi:
            return label, color, css
    return "Hazardous", "#be123c", "aqi-hazardous"


def generate_mock_forecast(base_aqi, days=7):
    """Generate mock 7-day AQI forecast (replace with your model output)."""
    np.random.seed(42)
    dates = [datetime.now() + timedelta(days=i) for i in range(days)]
    values = [max(10, int(base_aqi + np.random.randint(-30, 30))) for _ in range(days)]
    return dates, values


def load_model():
    """Load your trained model. Replace path with your actual model file."""
    model_path = "model/aqi_model.pkl"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            return pickle.load(f)
    return None  # Returns None → app uses mock prediction


def predict_aqi(model, features: dict) -> float:
    """Run prediction. If no model loaded, return mock value."""
    if model is None:
        # ── MOCK PREDICTION (remove once real model loaded) ──
        base = features.get("pm25", 80) * 1.2 + features.get("pm10", 100) * 0.5
        return min(500, max(0, int(base + np.random.randint(-10, 10))))
    # ── REAL MODEL ──
    feature_array = np.array([[
        features["pm25"], features["pm10"],
        features["no2"],  features["so2"],
        features["co"],   features["o3"],
    ]])
    return float(model.predict(feature_array)[0])


def send_alert_email(recipient: str, city: str, aqi: float, level: str, advisory: dict):
    """Send AQI alert email via SMTP. Configure credentials in sidebar."""
    sender    = st.session_state.get("email_sender", "")
    password  = st.session_state.get("email_password", "")
    smtp_host = st.session_state.get("smtp_host", "smtp.gmail.com")
    smtp_port = int(st.session_state.get("smtp_port", 587))

    if not sender or not password:
        return False, "Email credentials not configured in Settings."

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;background:#0a0f1e;color:#e2e8f0;padding:24px;">
    <div style="max-width:600px;margin:auto;background:#111827;border-radius:16px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#7f1d1d,#450a0a);padding:24px;text-align:center;">
        <h1 style="color:#fca5a5;margin:0;font-size:28px;">⚠️ AQI ALERT</h1>
        <p style="color:#fecaca;margin:8px 0 0 0;">BreatheSafe · Air Quality Warning</p>
      </div>
      <div style="padding:28px;">
        <h2 style="color:#f87171;">AQI Level: {int(aqi)} — {level}</h2>
        <p style="color:#94a3b8;">City: <strong style="color:#e2e8f0">{city}</strong> &nbsp;|&nbsp; Time: {datetime.now().strftime('%d %b %Y, %H:%M')}</p>
        <hr style="border-color:#1e293b;"/>
        <h3 style="color:#93c5fd;">Health Advisory</h3>
        <table style="width:100%;border-collapse:collapse;">
          <tr><td style="padding:8px;color:#7a8ba0;width:140px;">🏃 Exercise</td><td style="color:#e2e8f0">{advisory['exercise']}</td></tr>
          <tr><td style="padding:8px;color:#7a8ba0;">🫁 Respiratory</td><td style="color:#e2e8f0">{advisory['respiratory']}</td></tr>
          <tr><td style="padding:8px;color:#7a8ba0;">👶 Children</td><td style="color:#e2e8f0">{advisory['children']}</td></tr>
          <tr><td style="padding:8px;color:#7a8ba0;">👴 Elderly</td><td style="color:#e2e8f0">{advisory['elderly']}</td></tr>
        </table>
        <div style="margin-top:20px;padding:16px;background:#1e293b;border-radius:10px;">
          <p style="color:#94a3b8;margin:0;font-size:13px;">
            This is an automated alert from <strong>BreatheSafe AQI Predictor</strong>.<br/>
            Stay safe. Follow advisory guidelines strictly.
          </p>
        </div>
      </div>
    </div>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚨 AQI Alert: {level} ({int(aqi)}) in {city}"
    msg["From"]    = sender
    msg["To"]      = recipient
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        return True, "Alert email sent successfully!"
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════
defaults = {
    "alert_email": "",
    "email_sender": "",
    "email_password": "",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": "587",
    "alert_threshold": 150,
    "last_aqi": None,
    "health_conditions": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px 0;">
      <span style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;
                   background:linear-gradient(135deg,#63b3ed,#a78bfa);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        🌬️ BreatheSafe
      </span>
      <div style="font-size:0.72rem;color:#4a5568;letter-spacing:2px;margin-top:2px;">AQI PREDICTION SYSTEM</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">📍 Location</div>', unsafe_allow_html=True)
    selected_city = st.selectbox("Select City", CITIES, index=0)
    if selected_city == "Custom City":
        selected_city = st.text_input("Enter City Name", placeholder="e.g. Surat")

    st.markdown('<div class="section-title">🏥 Health Profile</div>', unsafe_allow_html=True)
    health_conditions = st.multiselect(
        "Your health conditions",
        ["Asthma", "COPD", "Heart Disease", "Diabetes", "Pregnant", "Allergies", "None"],
        default=st.session_state["health_conditions"]
    )
    st.session_state["health_conditions"] = health_conditions

    age_group = st.selectbox("Age Group", ["Child (< 12)", "Teen (12–18)", "Adult (18–60)", "Elderly (60+)"])

    st.markdown('<div class="section-title">📧 Email Alerts</div>', unsafe_allow_html=True)
    alert_email = st.text_input("Your Email", placeholder="you@email.com",
                                value=st.session_state["alert_email"])
    st.session_state["alert_email"] = alert_email

    alert_threshold = st.slider("Alert when AQI ≥", 50, 400,
                                st.session_state["alert_threshold"], step=10)
    st.session_state["alert_threshold"] = alert_threshold

    with st.expander("⚙️ SMTP Settings"):
        st.session_state["email_sender"]   = st.text_input("Sender Email", value=st.session_state["email_sender"])
        st.session_state["email_password"] = st.text_input("App Password",  type="password", value=st.session_state["email_password"])
        st.session_state["smtp_host"]      = st.text_input("SMTP Host", value=st.session_state["smtp_host"])
        st.session_state["smtp_port"]      = st.text_input("SMTP Port", value=st.session_state["smtp_port"])

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem;color:#374151;text-align:center;line-height:1.6;">
    Built with ❤️ · BreatheSafe v1.0<br/>
    Connect your model via <code>model/aqi_model.pkl</code>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="padding:8px 0 4px 0;">
  <span style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
               background:linear-gradient(135deg,#63b3ed,#a78bfa);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
    AQI Prediction Dashboard
  </span>
  <span style="margin-left:12px;font-size:0.8rem;color:#4a5568;letter-spacing:1.5px;">
    {selected_city.upper()} · {datetime.now().strftime('%d %B %Y')}
  </span>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["🔮 Predict", "📈 Forecast", "🏥 Health Advisory", "📧 Alerts"])


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 · PREDICT
# ────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="section-title">Input Pollutant Values</div>', unsafe_allow_html=True)
    st.caption("Enter sensor readings or measured values for your location.")

    col1, col2, col3 = st.columns(3)
    with col1:
        pm25 = st.number_input("PM2.5 (µg/m³)", 0.0, 999.0, 85.0, step=0.5)
        no2  = st.number_input("NO₂ (µg/m³)",   0.0, 999.0, 40.0, step=0.5)
    with col2:
        pm10 = st.number_input("PM10 (µg/m³)",  0.0, 999.0, 120.0, step=0.5)
        so2  = st.number_input("SO₂ (µg/m³)",   0.0, 999.0, 20.0, step=0.5)
    with col3:
        co   = st.number_input("CO (mg/m³)",     0.0,  99.0,  1.2, step=0.1)
        o3   = st.number_input("O₃ (µg/m³)",     0.0, 999.0, 60.0, step=0.5)

    predict_btn = st.button("🔮 Predict AQI", use_container_width=True)

    if predict_btn:
        with st.spinner("Running prediction model…"):
            time.sleep(0.6)
            model = load_model()
            features = {"pm25": pm25, "pm10": pm10, "no2": no2,
                        "so2": so2,   "co": co,     "o3": o3}
            aqi_value = predict_aqi(model, features)
            st.session_state["last_aqi"] = aqi_value

        level, color, css = get_aqi_info(aqi_value)
        advisory = HEALTH_ADVISORIES[level]

        # ── AQI gauge ──
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aqi_value,
            title={"text": f"<b>{level}</b>", "font": {"size": 18, "color": color}},
            number={"font": {"size": 52, "color": color}},
            gauge={
                "axis": {"range": [0, 500], "tickcolor": "#4a5568", "tickwidth": 1},
                "bar":  {"color": color, "thickness": 0.25},
                "bgcolor": "#111827",
                "bordercolor": "#1e293b",
                "steps": [
                    {"range": [0,   50],  "color": "#052e16"},
                    {"range": [51,  100], "color": "#1a2e05"},
                    {"range": [101, 150], "color": "#2d1f00"},
                    {"range": [151, 200], "color": "#2d0000"},
                    {"range": [201, 300], "color": "#1a0029"},
                    {"range": [301, 500], "color": "#200010"},
                ],
                "threshold": {"line": {"color": color, "width": 4}, "thickness": 0.8, "value": aqi_value},
            }
        ))
        fig.update_layout(
            paper_bgcolor="#0a0f1e", font_color="#e2e8f0",
            height=300, margin=dict(t=30, b=10, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Metric row ──
        mc1, mc2, mc3, mc4 = st.columns(4)
        metrics = [
            ("AQI Index", f"{int(aqi_value)}", level, css),
            ("PM2.5",     f"{pm25}",           "µg/m³", ""),
            ("PM10",      f"{pm10}",           "µg/m³", ""),
            ("Air Status",advisory["icon"],    level,   css),
        ]
        for col, (title, val, sub, c) in zip([mc1, mc2, mc3, mc4], metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="metric-title">{title}</div>
                  <div class="metric-value {c}">{val}</div>
                  <div class="metric-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        # ── Severe alert banner ──
        if aqi_value >= st.session_state["alert_threshold"]:
            st.markdown(f"""
            <div class="alert-banner">
              <b style="color:#fca5a5;font-size:1.05rem;">🚨 SEVERE AQI ALERT — {level.upper()}</b><br/>
              <span style="color:#fecaca;font-size:0.88rem;">
                Current AQI of <b>{int(aqi_value)}</b> has exceeded your alert threshold of
                <b>{st.session_state['alert_threshold']}</b>.
                {advisory['general']}
              </span>
            </div>""", unsafe_allow_html=True)

            # auto-send email if configured
            if st.session_state["alert_email"] and st.session_state["email_sender"]:
                ok, msg = send_alert_email(
                    st.session_state["alert_email"],
                    selected_city, aqi_value, level, advisory
                )
                if ok:
                    st.success(f"✅ Alert email sent to {st.session_state['alert_email']}")
                else:
                    st.warning(f"Email not sent: {msg}")

        # ── Pollutant breakdown bar ──
        st.markdown('<div class="section-title">Pollutant Breakdown</div>', unsafe_allow_html=True)
        poll_df = pd.DataFrame({
            "Pollutant": ["PM2.5", "PM10", "NO₂", "SO₂", "CO×10", "O₃"],
            "Value":     [pm25, pm10, no2, so2, co * 10, o3],
            "Safe Limit":[60,   100,  80,  80,  10,      100],
        })
        fig2 = go.Figure()
        fig2.add_bar(name="Your Value",  x=poll_df["Pollutant"], y=poll_df["Value"],
                     marker_color=color, opacity=0.85)
        fig2.add_bar(name="Safe Limit",  x=poll_df["Pollutant"], y=poll_df["Safe Limit"],
                     marker_color="#374151", opacity=0.6)
        fig2.update_layout(
            barmode="group", paper_bgcolor="#0a0f1e", plot_bgcolor="#0a0f1e",
            font_color="#e2e8f0", legend=dict(bgcolor="#111827"),
            height=280, margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig2, use_container_width=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 · FORECAST
# ────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="section-title">7-Day AQI Forecast</div>', unsafe_allow_html=True)
    st.caption("Replace `generate_mock_forecast()` with your model's multi-step prediction output.")

    base = st.session_state["last_aqi"] if st.session_state["last_aqi"] else 120.0
    dates, forecast_vals = generate_mock_forecast(base)

    fig3 = go.Figure()

    # Colour zones
    for lo, hi, label, col, _ in AQI_LEVELS:
        fig3.add_hrect(y0=lo, y1=min(hi, 500), fillcolor=col,
                       opacity=0.06, line_width=0,
                       annotation_text=label, annotation_position="right",
                       annotation=dict(font_size=10, font_color=col))

    fig3.add_trace(go.Scatter(
        x=dates, y=forecast_vals, mode="lines+markers",
        line=dict(color="#63b3ed", width=3),
        marker=dict(size=8, color=[get_aqi_info(v)[1] for v in forecast_vals]),
        fill="tozeroy", fillcolor="rgba(99,179,237,0.06)",
        name="Predicted AQI"
    ))

    fig3.update_layout(
        xaxis=dict(tickformat="%a %d", gridcolor="#1e293b"),
        yaxis=dict(range=[0, 500], gridcolor="#1e293b", title="AQI"),
        paper_bgcolor="#0a0f1e", plot_bgcolor="#0a0f1e",
        font_color="#e2e8f0", height=380,
        margin=dict(t=20, b=20, l=10, r=80),
        hovermode="x unified"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Forecast table
    forecast_df = pd.DataFrame({
        "Date":   [d.strftime("%A, %d %b") for d in dates],
        "AQI":    forecast_vals,
        "Level":  [get_aqi_info(v)[0] for v in forecast_vals],
    })
    st.dataframe(
        forecast_df.style.applymap(
            lambda v: f"color: {get_aqi_info(v)[1]}" if isinstance(v, int) else "",
            subset=["AQI"]
        ),
        use_container_width=True, hide_index=True
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 · HEALTH ADVISORY
# ────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown('<div class="section-title">Personalised Health Advisory</div>', unsafe_allow_html=True)

    if st.session_state["last_aqi"] is None:
        st.info("💡 Run a prediction first (Predict tab) to get personalised advisory.")
        current_level = "Moderate"
    else:
        current_level, color, _ = get_aqi_info(st.session_state["last_aqi"])

    advisory = HEALTH_ADVISORIES[current_level]

    # Questionnaire for personalisation
    with st.expander("📋 Answer health questions for tailored advice", expanded=True):
        q1 = st.radio("Do you have any respiratory conditions?",
                      ["No", "Mild Asthma", "Severe Asthma / COPD"])
        q2 = st.radio("Do you exercise outdoors?",
                      ["Rarely", "Sometimes (2–3×/week)", "Daily"])
        q3 = st.radio("Do you commute on roads for long hours?",
                      ["No", "Yes (1–2 hr)", "Yes (3+ hr)"])
        q4 = st.radio("Do you have children or elderly at home?",
                      ["No", "Children", "Elderly", "Both"])

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#111827,#1a2234);
                border-radius:16px;padding:20px 24px;border:1px solid rgba(99,179,237,0.2);
                margin-bottom:16px;">
      <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;">
        {advisory['icon']} Current Status: <span style="color:{color if st.session_state['last_aqi'] else '#eab308'};">{current_level}</span>
      </div>
      <div style="color:#94a3b8;margin-top:6px;font-size:0.9rem;">{advisory['general']}</div>
    </div>
    """, unsafe_allow_html=True)

    cards = [
        ("🫁 Respiratory Advisory", advisory["respiratory"]),
        ("🏃 Exercise & Activity",  advisory["exercise"]),
        ("👶 Children",             advisory["children"]),
        ("👴 Elderly Care",         advisory["elderly"]),
    ]

    # Personalise based on questionnaire
    if q1 in ("Mild Asthma", "Severe Asthma / COPD"):
        cards.append(("⚠️ Your Condition — Asthma/COPD",
                       "Keep your rescue inhaler at all times. Monitor SpO2. Reduce outdoor exposure significantly. Use air purifier at home."))
    if q2 == "Daily":
        cards.append(("🏋️ Your Routine — Daily Outdoor Exercise",
                       "Shift all workouts indoors when AQI > 100. Use N95 when going out. Rinse eyes and nasal passages after returning home."))
    if q3 != "No":
        cards.append(("🚗 Long Road Commute",
                       "Keep car windows closed. Use cabin air filter. Wear N95 if travelling by two-wheeler. Avoid peak traffic hours."))
    if q4 != "No":
        cards.append(("🏠 Protecting Vulnerable Members at Home",
                       "Seal gaps in windows. Use HEPA air purifier. Check AQI before outdoor trips. Stock up on required medicines."))

    for title, body in cards:
        st.markdown(f"""
        <div class="advisory-card">
          <h4>{title}</h4>
          <p>{body}</p>
        </div>""", unsafe_allow_html=True)

    # AQI reference table
    st.markdown('<div class="section-title">AQI Reference Scale</div>', unsafe_allow_html=True)
    ref_df = pd.DataFrame(AQI_LEVELS, columns=["Min", "Max", "Category", "Color", "CSS"])
    ref_df = ref_df[["Min", "Max", "Category"]]
    st.dataframe(ref_df, use_container_width=True, hide_index=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 · ALERTS
# ────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown('<div class="section-title">Email Alert Configuration</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        manual_email = st.text_input("Send alert to", value=st.session_state["alert_email"],
                                     placeholder="recipient@email.com")
        manual_aqi   = st.number_input("AQI value to simulate", 0, 500,
                                       int(st.session_state["last_aqi"]) if st.session_state["last_aqi"] else 180)
        manual_city  = st.text_input("City", value=selected_city)

    with col_b:
        st.markdown("""
        <div class="advisory-card">
          <h4>📧 How to Configure</h4>
          <p>
          1. Open <b>⚙️ SMTP Settings</b> in the sidebar.<br/>
          2. Enter your Gmail address as <b>Sender Email</b>.<br/>
          3. Generate a Gmail <b>App Password</b> (not your main password) at
             <a href="https://myaccount.google.com/apppasswords" target="_blank" style="color:#63b3ed;">myaccount.google.com/apppasswords</a>.<br/>
          4. Set threshold in sidebar — alerts auto-fire when AQI exceeds it.<br/>
          5. Use the button below to test manually.
          </p>
        </div>""", unsafe_allow_html=True)

    if st.button("📤 Send Test Alert Email", use_container_width=True):
        if not manual_email:
            st.error("Please enter a recipient email address.")
        else:
            with st.spinner("Sending email…"):
                level_m, _, _ = get_aqi_info(manual_aqi)
                adv_m = HEALTH_ADVISORIES[level_m]
                ok, msg = send_alert_email(manual_email, manual_city, manual_aqi, level_m, adv_m)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

    st.markdown('<div class="section-title">Alert Log</div>', unsafe_allow_html=True)
    # In production: load from a DB / CSV
    st.info("Alert history will appear here. Connect a database (SQLite/PostgreSQL) to persist logs.")

    log_df = pd.DataFrame({
        "Time":   [datetime.now().strftime("%d %b %Y %H:%M")],
        "City":   [selected_city],
        "AQI":    [st.session_state["last_aqi"] or "—"],
        "Level":  [get_aqi_info(st.session_state["last_aqi"])[0] if st.session_state["last_aqi"] else "—"],
        "Sent To":[st.session_state["alert_email"] or "—"],
    })
    st.dataframe(log_df, use_container_width=True, hide_index=True)