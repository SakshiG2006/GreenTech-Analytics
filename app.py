"""Shared GreenTech Analytics HTTP handler."""
import json
import os
import time

import jwt
import pandas as pd
import requests
from jwt import PyJWKClient


def response(status, body):
    return {"statusCode": status, "headers": {"Content-Type": "application/json", "Cache-Control": "no-store"}, "body": json.dumps(body)}


def authorized(headers):
    issuer = os.getenv("OAUTH_ISSUER", "").strip()
    audience = os.getenv("OAUTH_AUDIENCE", "").strip()
    jwks_url = os.getenv("OAUTH_JWKS_URL", "").strip()
    if not any([issuer, audience, jwks_url]):
        return os.getenv("AUTH_REQUIRED", "false").lower() != "true"
    if not (issuer and audience and jwks_url):
        return False
    auth = next((v for k, v in headers.items() if k.lower() == "authorization"), "")
    if not auth.lower().startswith("bearer "):
        return False
    try:
        token = auth.split(" ", 1)[1].strip()
        key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token).key
        jwt.decode(token, key, algorithms=["RS256", "ES256"], audience=audience, issuer=issuer)
        return True
    except Exception:
        return False


def historical(city):
    path = os.getenv("CLIMATE_CSV_PATH", "")
    if not path or not os.path.isfile(path):
        raise ValueError("Historical CSV not configured or not found")
    df = pd.read_csv(path)
    city_col = os.getenv("CSV_CITY_COLUMN", "Country")
    date_col = os.getenv("CSV_DATE_COLUMN", "Date")
    temp_col = os.getenv("CSV_TEMP_COLUMN", "AverageTemperature")
    co2_col = os.getenv("CSV_CO2_COLUMN", "CO2")
    for col in (city_col, date_col, temp_col):
        if col not in df.columns:
            raise ValueError(f"Required CSV column not found: {col}")
    rows = df[df[city_col].astype(str).str.casefold() == city.casefold()].copy()
    if rows.empty:
        raise ValueError(f"No rows for '{city}' in configured column '{city_col}'")
    rows[date_col] = pd.to_datetime(rows[date_col], errors="coerce")
    rows[temp_col] = pd.to_numeric(rows[temp_col], errors="coerce")
    rows = rows.dropna(subset=[date_col, temp_col])
    if rows.empty:
        raise ValueError("No valid historical temperature rows")
    current_month = time.gmtime().tm_mon
    month_rows = rows[rows[date_col].dt.month == current_month]
    chosen = month_rows if not month_rows.empty else rows
    average = float(chosen[temp_col].mean())
    co2 = None
    if co2_col in chosen.columns:
        vals = pd.to_numeric(chosen[co2_col], errors="coerce").dropna()
        if not vals.empty:
            co2 = float(vals.mean())
    return average, co2


def handle(city, headers=None):
    headers = headers or {}
    if not authorized(headers):
        return response(401, {"error": "Missing or invalid OAuth2 bearer access token"})
    city = (city or "").strip()
    if not city:
        return response(400, {"error": "Query parameter 'city' is required"})
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        return response(500, {"error": "OPENWEATHER_API_KEY is not configured"})
    try:
        upstream = requests.get("https://api.openweathermap.org/data/2.5/weather",
                                params={"q": city, "appid": api_key, "units": "metric"}, timeout=10)
        if upstream.status_code != 200:
            return response(502, {"error": "Weather provider request failed", "upstream_status": upstream.status_code})
        current = float(upstream.json()["main"]["temp"])
        average, co2 = historical(city)
        deviation = round(current - average, 2)
        status = "Warmer than average" if deviation > 0 else "Colder than average" if deviation < 0 else "Near average"
        return response(200, {"city": city, "current_temp_c": current,
                              "historical_monthly_avg_c": round(average, 2),
                              "deviation_c": deviation, "status": status, "co2": co2,
                              "data_source": "OpenWeatherMap + configured Kaggle CSV"})
    except ValueError as exc:
        return response(400, {"error": str(exc)})
    except requests.RequestException:
        return response(502, {"error": "Unable to retrieve weather data"})
    except Exception:
        return response(500, {"error": "Internal processing error"})


def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    return handle(params.get("city"), event.get("headers") or {})
