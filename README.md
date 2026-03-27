# Air- Sense
# 🌫️ AirSense: AI-Based AQI Forecast & Smart Health Advisory System
# AirSense: AI-Based AQI Forecast & Health Advisory System

## 🚀 What the Project Does
This project predicts the next 24-hour Air Quality Index (AQI) for Indian cities and converts it into simple, actionable health advisories.

Instead of showing raw AQI numbers, the system helps users understand:
- When it is safe to go outside
- When to avoid exposure
- What precautions to take

---

## 👥 Who It Serves
- General public in urban areas  
- Children (sensitive to pollution)  
- People with respiratory conditions  

Focus cities: Gwalior + polluted Tier-2 cities in Madhya Pradesh  

---

## ⚙️ How It Works
1. Fetch AQI data (CPCB)
2. Process last 30  1-year historical data  
3. Use XGBoost model with lag + weather features  
4. Predict next 24-hour AQI with confidence level  
5. Classify AQI using CPCB standards  
6. Generate personalized health advisories  
7. Display via dashboard and alerts  

---

## 🧠 AI Tools Used (Transparency)

- **ChatGPT** → Problem understanding, advisory logic design  
- **Claude** → Code generation and API integration  
- **XGBoost** → AQI prediction model  

👉 Most used tool: ChatGPT  

---

## 🤖 AI vs Human Responsibility

**AI Role:**
- AQI forecasting  
- Advisory generation  

**Human Role:**
- Define health rules  
- Validate outputs  
- Handle edge cases  

---

## 🇮🇳 India-Specific Design

- Uses CPCB AQI categories (Good → Severe)  
- Handles Indian pollution patterns (Diwali, dust, seasonal smog)  
- Focus on Tier-2 cities with limited awareness tools  
- Simple language advisories for accessibility  

---

## 🛠️ Tech Stack

- Python (Data processing & modeling)  
- XGBoost (Prediction model)  
- Streamlit (Dashboard)  
