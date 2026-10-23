# API documentation

## GET /?city={city}
Returns climate deviation using live OpenWeatherMap temperature and a configured historical CSV.

Example request:
```http
GET /?city=London
Accept: application/json
Authorization: Bearer <OAuth2 access token>
```

Illustrative response only (real values depend on API and dataset):
```json
{
  "city": "London",
  "current_temp_c": 11.82,
  "historical_monthly_avg_c": 9.6,
  "deviation_c": 2.22,
  "status": "Warmer than average",
  "co2": null,
  "data_source": "OpenWeatherMap + configured Kaggle CSV"
}
```

## Status codes
- 200: calculation succeeded
- 400: missing city, missing dataset rows, or invalid dataset configuration
- 401: bearer token missing/invalid when OAuth validation is enabled
- 500: missing API key or internal processing error
- 502: weather upstream failure

## Configuration
Required: OPENWEATHER_API_KEY, CLIMATE_CSV_PATH and actual CSV column mappings. For OIDC validation configure OAUTH_ISSUER, OAUTH_AUDIENCE and OAUTH_JWKS_URL. The identity provider must issue tokens; configuration alone does not provision an identity provider.

## Security
Use HTTPS end-to-end, protect secrets in cloud settings/secret managers, rotate keys, avoid logging tokens, and configure rate limits. With no OAuth settings, AUTH_REQUIRED=true rejects requests; configure a real issuer/audience/JWKS before production use.
