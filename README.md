# 🌍 Earthquake AI Detector & Live Weather Dashboard

## Project Description
A web-based application that monitors recent global earthquake events using USGS data and displays live weather information using the Open-Meteo API.

## Features
- Earthquake magnitude and location monitoring
- Latest earthquake event details
- Total earthquake count
- Largest magnitude display
- Weather temperature and humidity
- Wind speed and feels-like temperature
- Automatic data refresh

## Tools & Technologies
- Python
- FastAPI
- Uvicorn
- HTML, CSS and JavaScript
- USGS Earthquake API
- Open-Meteo Weather API
- Visual Studio Code
- GitHub

## Installation

```bash
git clone https://github.com/Raghavdixit123/EARTHQUAKE_AI_DETACTER.git
cd EARTHQUAKE_AI_DETACTER
python -m venv venv
```

Activate environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install requirements:

```bash
python -m pip install -r requirements.txt
```

Run project:

```bash
python -m uvicorn main:app --reload
```

Open in browser:

http://127.0.0.1:8000

## Future Scope
- AI-based earthquake anomaly detection
- Interactive earthquake maps
- Voice notifications
- Custom earthquake alerts
- Historical data analysis

## Disclaimer
This is an educational monitoring project, not an official earthquake prediction or early-warning system.
