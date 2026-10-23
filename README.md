# GreenTech Analytics — Multi-cloud climate deviation prototype

A small Python HTTP service combining live OpenWeatherMap temperature with a historical monthly average from a Kaggle climate CSV and returning JSON climate-deviation results.

## Status and scope
- **AWS Lambda:** existing deployment is reported in the project report; validate the endpoint before submission.
- **Azure Functions:** source scaffold is included, but a successful Azure deployment must still be completed and evidenced. This repository update does not deploy cloud resources.
- **OAuth 2.0/OIDC:** bearer JWT validation is included when issuer, audience, and JWKS settings are configured. Configure a real identity provider and test it before claiming authentication is live.
- **CO₂:** optional CSV field support is included. A CO₂ value is returned only when the selected dataset contains a usable field and the column mapping is correct. Verify against the actual dataset before claiming integration.

## Files
- `app.py` — shared processing handler and optional OIDC JWT validation
- `function_app.py` — Azure Functions HTTP trigger
- `requirements.txt` — Python dependencies
- `load_test.py` — concurrent HTTP test harness
- `.env.example` — configuration template (no secrets)
- `docs/API.md` — API documentation

## Prerequisites
Python 3.11/3.12, an OpenWeatherMap API key, the Kaggle climate CSV, and an AWS/Azure account. For authentication, configure an OAuth 2.0/OIDC provider that issues JWT access tokens.

## Local setup
1. Create a virtual environment: `python -m venv .venv`
2. Activate it (Windows: `.venv\\Scripts\\activate`; macOS/Linux: `source .venv/bin/activate`)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and set values in your shell or local environment. The app does not automatically load `.env`.
5. Set `CLIMATE_CSV_PATH` and map the actual CSV headers using the variables in `.env.example`.
6. Never commit `.env`, API keys, tokens, or other secrets.

## Data mapping
Kaggle dataset schemas differ. Configure `CSV_CITY_COLUMN`, `CSV_DATE_COLUMN`, `CSV_TEMP_COLUMN`, and optional `CSV_CO2_COLUMN` to actual headers. The implementation performs an exact city-name match and calculates an average for the current calendar month when available, otherwise it uses all matching rows. If the dataset does not contain city-level observations, do not describe a global average as a city-specific historical average.

## Deployment
### AWS Lambda
Package the shared files and dependencies or attach a compatible layer. Configure environment variables in Lambda. Use HTTPS through a Function URL or API Gateway. For production, configure an API Gateway JWT authorizer or verified Lambda authorizer; do not expose a public unauthenticated endpoint if authentication is required.

### Azure Functions
Install Azure Functions Core Tools and a compatible Python runtime. Configure Function App settings, then publish with `func azure functionapp publish <APP_NAME>`. Test the HTTPS endpoint. Configure Microsoft Entra ID/App Service Authentication or API Management JWT validation for OAuth/OIDC; app settings alone do not complete OAuth deployment.

## Concurrent testing
Run `python load_test.py --url 'https://YOUR-ENDPOINT/?city=London' --requests 20 --concurrency 5`. Run the same request count and concurrency against AWS and Azure from the same machine and time window. Record region, plan, cold/warm status, and test conditions. This measures client-observed latency and does not by itself prove provider-side execution time or autoscaling.

## Cost comparison
Use current regional pricing calculators. Record region, plan, memory, execution duration, request count, logging, egress, and free-tier assumptions. Do not infer cost advantage from latency alone.

## Evidence still required before final submission
- Azure deployed endpoint and successful response screenshot
- Actual dataset source/version, column mapping, and evidence for temperature/CO₂ calculations
- Reproducible concurrent AWS and Azure test outputs
- OAuth/OIDC configuration and tests for valid, missing, expired, and wrong-audience tokens
- Architecture diagram and redacted deployment screenshots
