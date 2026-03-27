# DECISIONS.md

## Decision 1: Model Selection

- **AI Suggestion:** Use LSTM for AQI forecasting
- **Team Decision:** Use XGBoost with lag features
- **Reason:** XGBoost performs better on structured data like AQI and weather. It is faster, requires less data, and is more suitable for hackathon constraints compared to deep learning models.


## Decision 2: Feature Engineering

- **AI Suggestion:** Use only past AQI values
- **Team Decision:** Use AQI + weather features (temperature, humidity, wind speed)
- **Reason:** AQI is influenced by environmental factors. Including weather improves prediction accuracy and reflects real-world conditions.


## Decision 3: Data Source Selection

- **AI Suggestion:** Use multiple global datasets
- **Team Decision:** Use CPCB/OpenAQ (India-specific data)
- **Reason:** Ensures consistency with Indian AQI standards and keeps the solution context-specific.


## Decision 4: Advisory System Design

- **AI Suggestion:** Generate advisories using AI text generation
- **Team Decision:** Use rule-based advisory mapped to AQI categories
- **Reason:** Health advisories must be reliable and interpretable. Rule-based systems ensure safety and consistency.


## Decision 5: System Scope

- **AI Suggestion:** Build a complex system with many features
- **Team Decision:** Focus on core features (forecast + advisory + dashboard)
- **Reason:** Keeps the solution feasible within hackathon time while delivering maximum impact.


## Decision 6: Failure Handling

- **AI Suggestion:** Focus mainly on prediction accuracy
- **Team Decision:** Include fallback mechanisms (real-time AQI, low-confidence alerts)
- **Reason:** Ensures system reliability and safe user guidance even when predictions are uncertain.
