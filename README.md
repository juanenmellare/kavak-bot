# Kavak Bot
A simple bot that identifies and searches for the latest cars added on Kavak and notify via email.

# Setup
Execute `pip3 install -r requirements.txt`
Create `config.json` at root level, copy/paste and update the following json
```json
{
  "search_rate_per_minutes": 30, // Search and notify interval.
  "country_acronym": "ar",       // Kavak country code. 
  "filters": {                   // Kavak filters, check them at the URL of the web page when filter are applied (should match and if you want to ignore them add an underscore at the begging of the key). 
    "order": "higher_price",
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
  "smtp": {                      // SMTP data to send emails.
    "host": "smtp.x.com",
    "port": 777,
    "user": "x@x.com",
    "password": "x"
  },
  "receiver": "x@x.com"          // The email that will receive the reports.
}
```