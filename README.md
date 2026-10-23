# 🌍 GreenTech Analytics: Sustainable Climate Data Processing

## 📌 Project Overview
GreenTech Analytics is a cloud-native prototype designed to analyze climate change by comparing real-time weather data with historical global temperature records. The project demonstrates the application of the **NIST Cloud Computing Model** using a serverless architecture to ensure scalability, elasticity, and cost-efficiency.

## 🏗️ Cloud Architecture
The system is designed as a multi-cloud service to compare deployment and performance across different providers.

- **Primary Deployment:** AWS Lambda (PaaS/FaaS)
- **Secondary Prototypes:** Microsoft Azure Functions & Google Cloud Functions
- **Runtime:** Python 3.12
- **Security:** HTTPS communication, Environment Variables for secret management, and OIDC/OAuth 2.0 scaffold.

## 🛠️ Tech Stack
- **Language:** Python 3.12
- **Cloud Provider:** Amazon Web Services (AWS)
- **API:** OpenWeatherMap REST API (Live environmental data)
- **Dataset:** Kaggle Global Climate Change Dataset (Historical temperature & CO₂ data)
- **Libraries:** Pandas (Data processing), Requests (API communication)

## 📊 How it Works
1. **Request:** The user sends an HTTPS GET request to the cloud endpoint with a city parameter (e.g., `?city=London`).
2. **Live Retrieval:** The function fetches the current temperature via the **OpenWeatherMap API**.
3. **Historical Analysis:** The function processes a **mini-dataset** derived from the Kaggle Global Climate Change dataset to find the historical average for that specific city.
4. **Computation:** The system calculates the **Climate Deviation**:
   `Deviation = Live Temperature - Historical Average`
5. **Response:** The result is returned as a structured JSON object containing the current temp, historical average, deviation, and a status (Warmer/Colder).

## 📈 Performance Metrics (AWS)
A load test of 20 consecutive requests was performed to validate the elasticity of the serverless environment.
- **Success Rate:** 100%
- **Average Latency:** 1888.61 ms
- **Max Latency:** 1954.55 ms
- **Analysis:** The latency is primarily attributed to the "Cold Start" of the Pandas library in a serverless environment.

## 📖 API Documentation
**Endpoint:** `/climate_processor`  
**Method:** `GET`  
**Parameter:** `city` (String)  
**Example Request:** `https://[your-lambda-url]/?city=London`  
**Example Response:**
```json
{
  "city": "London",
  "current_temp": 11.82,
  "historical_avg": 9.6,
  "deviation": 2.22,
  "status": "Warmer than average",
  "details": "overcast clouds"
}
