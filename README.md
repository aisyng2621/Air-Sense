# AirSense

AirSense is an AI - Based System which predicts the next day's AIR QUALITY INDEX and provides user simple, personalized advice for users.  
We convert data into decisions.

---

##  PROBLEM STATEMENT
There is a huge problem that air quality data of Indian cities is scattered and it shows current AQI, i.e., it doesn't forecast the future values.

---

##  OUR SOLUTION
We suggest AirSense, an AI-based system that does AQI forecasting and provides users with easy-to-understand health personal advisories.

---

##  TARGET USERS
Our target audience is:
- Daily commuters  
- Kids  
- Parents  
- Patients suffering from respiratory problems  
- Citizens living in polluted cities (e.g., Gwalior, Delhi, etc.)

---

## SYSTEM WORKFLOW

Collect AQI data from CPCB and Weather data from Visual Crossing  
↓  
Processing the data: filling missing values (mean of previous three values), feature engineering, dropping columns  
↓  
Merge AQI and Weather Data  
↓  
Train XGBoost Model for AQI Prediction  
↓  
Generate `.pkl` file and attach it to main website through Streamlit  

---

##  AI TOOLS AND TECHNOLOGIES

- **Data Preprocessing:** Python, Pandas  
- **Machine Learning:**:XGBOOST ,SKLEARN 
- **Frontend:**  Streamlit
- **Backend:** Python  

---

##  AI TOOL TRANSPARENCY

| Tool      | Purpose |
|-----------|--------|
| CLAUDE    | Used for making UI, deployment part and to integrate and backend support of the website |
| CHATGPT   | For formation of problem, solving minor problems, glitches and doubts |

---

##  ERROR HANDLING STRATEGY

The system incorporates error handling primarily during the data preprocessing stage to ensure data quality. Missing values are handled using appropriate techniques like taking the mean of three previous values of the row in AQI dataset. Feature engineering techniques such as creation of new features are applied. If APIs are used, error handling such as timeouts, rate limits, etc., should be included.

---

##  WHAT WOULD WE BUILD NEXT

If we had more time, we could have done the following:
1. Used APIs with permissions  
2. Better frontend  
3. More robust predictions  
4. Track additional factors like patient health history and environmental conditions  

---

## IMPACT

Our AI-based system helps in the following ways:
1. Individuals make better decisions every day in polluted environments regarding their health  
2. Stay safer during high AQI/pollution conditions  
3. Raise awareness for public health  

---

## CONCLUSION

AirSense takes raw data and converts it into useful information, allowing citizens to make better informed decisions in a polluted environment.

---

## SCOPE

This is a prototype focusing on data preprocessing and AQI prediction.  
Dashboard and real-time deployment are part of future work.

---

## TEAM

**TEAM NEXUS**  
AI SYNERGY HACKATHON
