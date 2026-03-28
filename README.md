9# 🌫️ AirSense: AI-Based AQI Forecast & Smart Health Advisory System

AirSense is an AI - Based System which predicts the next day's AIR QUALITY INDEX and provides user simple ,personalized advice for users. We convert data into decisions.

*PROBLEM STATEMENT*
There is a huge problem that air quality data of Indian cities is scattered and it is shows current AQI ,i.e. it doesn't forecast the future values. 

*OUR SOLUTION*
We Suggest you AirSense, an AI-based system that do AQI forecasting  and provides user with easy to understand health personal advisories.

*TARGET USERS*
Our target audience is daily commuters,kids,parents,patients suffering from respiratory problems and citizens living in polluted cities,e.g., Gwalior,Delhi, etc.

*SYSTEM WORKFLOW*
Collect AQI data from CPCB and Weather data from visual crossing
                                             |
Processing the data: filling missing values (the mean of the previous three values), feature engineering, dropping columns
                                             |
    Merge AQI and Weather Data
                                             |
Train XGBoost Model for AQI Prediction
                                             |
generated .pkl file try to attach to main website through streamlit

*AI TOOLS AND TECHNOLOGIES*
* Data Preprocessing:Python  , Pandas
* Machine Learning: 
* Frontend: 
* Backend:Python

*AI TOOL TRANSPARENCY*
|       Tool               |                            Purpose                                             |
| 1.)CLAUDE          |    Used for making UI ,deployment part and to     |
|                              |  integrate and backend support of the website    |
|2.) CHATGPT        | For formation of problem, to solve minor             | 
|                              | problem, glitches and solving doubts                     |
 
*ERROR HANDLING STRATEGY*
The system incorporates error handling primarily during the data preprocessing stage to ensure data quality. Missing values are handled using appropriate technique like taking mean of three previous values of the row in AQI dataset. Feature engineering techniques such as creation of new features. If we have used the API we must have included error handling such as timeouts, rate limits etc.

*WHAT WOULD WE BUILD NEXT*
If we had more time , we could have done the following things:
1.)Used API with permisions
2.)Better frontend
3.) More Robust predictions
4.)We would have tried to track few more things like patient health history and taken in consideration more factor affecting the user in a polluting enviornment.

*IMPACT*
Our AI Based System helps in the following ways:
1.)Indivdual make better decisions everyday in polluted enviornment regarding their health
2.)Stay safer during high AQI/Pollution conditions
3.)Raise awareness for Public Health

*CONCLUSION*
AirSense takes raw data and converted it into useful information, allowing citizens to make better informed decisions in a polluted environment.

*SCOPE*
This is a prototype focusing on data preprocessing and AQI prediction.
Dashboard and real-time deployment are part of future work.

 TEAM NEXUS
AI SYNERGRY HACKATHON 
