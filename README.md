# Kavak Bot

A simple bot that identifies and searches for the latest cars added on Kavak and notify via email.

<img width="785" alt="Screenshot 2024-02-26 at 18 22 34" src="https://github.com/juanenmellare/kavak-bot/assets/18221356/5801d96d-1667-4986-9fda-2c3f9ab88c7f">

# Requirements

**Python 3.11 or higher** (https://www.python.org/downloads/).

Or

**Docker** (https://docs.docker.com/get-docker/).

# Setup

Create a file `config.json` in the same folder as 'kavak-bot.py', copy/paste and update the following JSON.
```json
{
  "search_rate_per_minutes": 30, // Search and notify interval. When value is 0 it will execute just once.
  "country_acronym": "ar",       // Kavak country code. 
  "filters": {                   // Kavak filters, check them at the URL of the web page when filter are applied (should match and if you want to ignore them add an underscore at the begging of the key). 
    "order": "lower_price",
    "min_price": 0,
    "max_price": 18000000,
    "year": [2021,2022,2023,2024],
    "body_type": ["hatchback"],
    "status": ["disponible"],
    "_min_km": 0,
    "_max_km": 100000,
    "_region": [],
    "_location": [],
    "_transmission": [],
    "_color": [],
    "_fuel_type": [],
    "_maker": [],
    "_model": []
  },
  "smtp": {                      // Your SMTP data to send emails.
    "host": "smtp.x.com",
    "port": 777,
    "user": "x@x.com",
    "password": "x"
  },
  "receiver": "x@x.com"          // The email that will receive the reports.
}
```

**Python:** `pip3 install -r requirements.txt`.

**Docker:**  `make build`.

# Run

**Python:** `python3 kavak-bot.py`.

**Docker:** `make run` (for Unix OS) / `make run-windows` (for Windows OS).
