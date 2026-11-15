T.U.L.I.P. — Backend

Backend service for T.U.L.I.P. (Thermal sUrveillance of Landscape Ignition Patterns), a satellite-based platform for exploring wildfire-related thermal anomaly detections and their historical patterns.

The backend exposes a REST API built with FastAPI and uses PostgreSQL + PostGIS for date-based and geographic queries.

What it does

Retrieves satellite thermal-anomaly detections for a selected date and geographic area.

Calculates historical statistics over a selected time interval, including detection counts and Fire Radiative Power (FRP) aggregates.

Produces experimental monthly FRP estimates using a seasonal statistical model.

Performs spatial filtering in PostGIS rather than transferring the full dataset to the application layer.

Architecture

Cesium frontend
        |
        | HTTPS / REST API
        v
FastAPI backend
        |
        | SQL queries
        v
PostgreSQL + PostGIS
        |
        v
Harmonized MODIS / VIIRS detections

The frontend communicates with the backend over HTTPS. Database credentials remain on the server and are not exposed to the frontend.

Data

The platform uses active-fire / thermal-anomaly observations distributed through NASA FIRMS. The project works with observations from:

MODIS — on NASA's Terra and Aqua satellites.

VIIRS — on Suomi-NPP and NOAA-20 / NOAA-21 satellites, depending on the downloaded dataset.

Source: NASA FIRMS

MODIS and VIIRS files have different column sets. The import process harmonizes the fields used by the application and preserves sensor-specific values where available. Missing sensor-specific fields are represented as null values.

Important data interpretation notes

A FIRMS point represents a satellite-detected thermal anomaly, not necessarily one unique wildfire incident. Several detections may correspond to the same incident.

FRP (Fire Radiative Power) is the radiative power associated with a detection at the satellite observation time. A sum of FRP values is an aggregate of detected FRP values; it is not accumulated fire energy, burned area, or fire-spread rate.

Satellite observations can be affected by cloud cover, overpass timing, sensor characteristics, and data availability. A lack of detections does not prove that no fire was present.
Near Real-Time (NRT) data are preliminary and may later be replaced by archive data. Avoid importing overlapping NRT and archive records twice.



Requirements

Python 3.10 or newer is recommended.

PostgreSQL with the PostGIS extension enabled.

Python dependencies listed in the backend's requirements.txt (if it is stored elsewhere in the repository, use that file).

Enable PostGIS in the target database:

CREATE EXTENSION IF NOT EXISTS postgis;

Local setup

Clone the repository and open the backend directory:

git clone <REPOSITORY_URL>
cd <REPOSITORY_DIRECTORY>/backend

Create and activate a virtual environment:

Windows (PowerShell)

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Linux / macOS

python -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configure the database connection using the environment-variable names expected by database_init/db_launcher.py. Do not put database passwords or other secrets in source code or commit them to Git.

Start the API from the backend/ directory:

uvicorn api_requester.main:app --reload --host 0.0.0.0 --port 8000

Open the interactive API documentation:

http://127.0.0.1:8000/docs

If your dependency file is in the repository root rather than backend/, run pip install -r ../requirements.txt instead. The module command above assumes api_requester/ and database_init/ are importable from the backend/ working directory.

API endpoints

The API is organized around the following main operations. The interactive Swagger page at /docs shows the exact query parameters, types, and response schemas exposed by the deployed version.

Endpoint

Purpose

GET /fires

Returns individual thermal-anomaly detections for a selected acquisition date and geographic bounding box.

GET /fire_stats

Returns aggregated statistics for a selected date range, interval, and geographic bounding box.

GET /forecast

Returns experimental monthly FRP estimates based on historical data.

Historical statistics

/fire_stats accepts a date range, an aggregation interval, and bounding-box coordinates. The statistics include values such as:

number of detections;

total detected FRP;

mean FRP.

The database performs the geographic filtering and aggregation. This avoids loading all matching records into Python just to calculate summary values.

Experimental forecasting

The forecasting endpoint estimates expected monthly FRP from historical monthly aggregates. The model combines:

a linear time trend;

Fourier sine and cosine terms to represent recurring seasonality;

a Tweedie Generalized Linear Model (GLM) with a logarithmic link.

The general linear predictor is:

[
\ln(\mu_t)=\beta_0+\beta_1t+
\sum_{k=1}^{K}\left[
a_k\sin\left(\frac{2\pi kt}{P}\right)+
b_k\cos\left(\frac{2\pi kt}{P}\right)
\right]
]

where t is the monthly time index, P is the seasonal period, K is the number of Fourier harmonics, and mu_t is the expected monthly FRP. The current configuration uses a 12-month seasonal period and two harmonics unless configured otherwise.

This is an experimental seasonal estimate, not a prediction of individual fire events, ignition locations, or fire spread. Forecast quality depends on the historical data, geographic region, sensor coverage, and validation period.

Spatial queries

Geographic filtering is handled with PostGIS using longitude / latitude coordinates in the WGS 84 reference system (SRID 4326). The database stores point geometries and queries the selected bounding box using spatial operations.

The bounding-box coordinate order is:

min_lon, min_lat, max_lon, max_lat

Deployment

The backend is designed to be hosted as a web service and connected to a managed PostgreSQL/PostGIS database. For a Render deployment:

Set the service root directory to backend/ if the application is started with api_requester.main:app.

Install dependencies from the backend dependency file, or adjust the build command if it is stored at the repository root.

Use a start command similar to:

uvicorn api_requester.main:app --host 0.0.0.0 --port $PORT

Configure the database connection through Render environment variables, using the names expected by the backend code.

Configure CORS to allow requests from the deployed frontend origin.

Keep the database private; only the backend should connect to it.

Never commit .env files, database URLs containing credentials, API keys, or passwords.

The deployed API's /docs endpoint can be used to inspect the available routes and test requests.

Limitations

Thermal-anomaly detections are satellite observations and should not be interpreted as a one-to-one count of wildfire incidents.

The platform does not simulate or predict the physical spread of an individual fire.

The experimental forecasting model estimates aggregate monthly FRP patterns. It does not provide real-time incident forecasts or guaranteed future outcomes.

Historical comparisons should account for differences in sensor coverage, observation frequency, cloud cover, and data completeness.

Data source and references

NASA FIRMS — Fire Information for Resource Management System

NASA FIRMS Active Fire Data

readme.md modified by ChatGPT LLM 
