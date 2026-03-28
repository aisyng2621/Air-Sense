# DECISIONS.md


##  Purpose

This document records how AI suggestions were used and how final decisions were taken by our team during the project.

It shows that we did not blindly follow AI and made our own decisions based on the problem.

---

##  Decision 1: Model Selection

* **AI Suggestion (ChatGPT):** Use LSTM for AQI forecasting
* **Team Decision:** Use XGBoost with lag and weather features
* **Reason:** AQI prediction is based on structured data (AQI + weather). XGBoost is faster, easier to train, and suitable for hackathon constraints compared to deep learning models.

---

##  Decision 2: Feature Engineering

* **AI Suggestion (ChatGPT):** Use only historical AQI values
* **Team Decision:** Use AQI lag features along with weather data (temperature, humidity, wind speed)
* **Reason:** AQI depends on environmental factors. Adding weather improves prediction accuracy and reflects real-world conditions.

---

##  Decision 3: Data Source Selection

* **AI Suggestion (ChatGPT):** Use multiple global datasets
* **Team Decision:** Use CPCB/OpenAQ for AQI and Open-Meteo for weather
* **Reason:** Keeps the project aligned with Indian conditions and standard AQI guidelines.

---

##  Decision 4: Advisory System Design

* **AI Suggestion (ChatGPT):** Generate advisories using AI text
* **Team Decision:** Use rule-based advisory based on CPCB AQI categories
* **Reason:** Health advice should be consistent and reliable. Rule-based system is safer and easier to explain.

---

##  Decision 5: System Scope

* **AI Suggestion (ChatGPT):** Build a complex system with many features
* **Team Decision:** Focus on core system (prediction + advisory + dashboard + alerts)
* **Reason:** Time is limited in hackathon, so we focused on important features only.

---

##  Decision 6: Failure Handling

* **AI Suggestion (ChatGPT):** Focus mainly on improving accuracy
* **Team Decision:** Add fallback mechanisms (use last AQI, alerts for low confidence)
* **Reason:** System should not give wrong information if prediction fails.

---

## 🔹 Decision 7: Data Window

* **AI Suggestion (ChatGPT):** Use large multi-year dataset
* **Team Decision:** Use recent data (30 days to 1 year)
* **Reason:** Recent data reflects current pollution trends better.

---

##  Decision 8: Deployment Approach

* **AI Suggestion (Claude):** Build full production system
* **Team Decision:** Use Streamlit prototype
* **Reason:** Easy to build, easy to demo, and suitable for hackathon time.

---

##  Decision 9: Health Advisory Importance

* **AI Suggestion (ChatGPT):** Focus mainly on AQI prediction output

* **Team Decision:** Provide simple health advisories along with AQI

* **Reason:**
  Most people do not understand AQI values or what actions to take.
  By giving clear advisories (what to do / what not to do), users can take better precautions and protect their health.

---

## 🎯 Conclusion

In this project, AI was used as a helper, but final decisions were taken by the team.

We focused on building a practical and understandable solution instead of blindly following AI suggestions.

---
