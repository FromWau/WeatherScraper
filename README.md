# WeatherScraper
Scraps the weather.com site and returns an up to 48h weather forecast in json format.

## But why
Primarly made to be piped into `jq` and used for polybar.

## Usage
```bash
usage: weather_scraper.py [-h] [-n N] [-u UNIT] [-l LANG] [-d DIR] location_code

scraps weather.com for weather data

positional arguments:
  location_code         specifies the location for where to check the weather

options:
  -h, --help            show this help message and exit
  -n N, --n N           specify how many forecasts should be scraped (default: 2)
  -u UNIT, --unit UNIT  sets the unit, valid units: C, F, H (default: C)
  -l LANG, --lang LANG  sets the language, format: <language code>-<country code> (default: en-GB)
  -d DIR, --dir DIR     specify the directory for the output.json file (default: None)
```


### How to change the location/ from where to get the location_code?
Just go to https://weather.com/ and search for the desired city in the search.  
For example searching for New York City will redirect you to:  
https://weather.com/weather/today/l/96f2f84af9a5f5d452eb0574d4e4d8a840c71b05e22264ebdc0056433a642c84.

The location_code is the last part of the url, so in this case:  
96f2f84af9a5f5d452eb0574d4e4d8a840c71b05e22264ebdc0056433a642c84


## Example
Get the next two weather forecasts for New York City:
```shell
python weather_scraper.py 96f2f84af9a5f5d452eb0574d4e4d8a840c71b05e22264ebdc0056433a642c84
```

Returns (pipe into jq for pretty output):
```json
{
  "request": {
    "timestamp": "2022-10-20 11:31:17",
    "urls": [
      "https://weather.com/en-GB/weather/hourbyhour/l/96f2f84af9a5f5d452eb0574d4e4d8a840c71b05e22264ebdc0056433a642c84?unit=m",
      "https://weather.com/en-GB/weather/tenday/l/96f2f84af9a5f5d452eb0574d4e4d8a840c71b05e22264ebdc0056433a642c84?unit=m"
    ],
    "last_updated": "2022-10-20 11:28:00"
  },
  "location": {
    "city": "New York City",
    "state": "NY",
    "country": "United States",
    "locale_timestamp": "2022-10-20 05:28:00",
    "forecasts": [
      {
        "date": "2022-10-20",
        "weather": [
          {
            "time": "6:00",
            "temperature": "5°",
            "wind": "SW 12 km/h",
            "humidity": "66%",
            "uv index": "0 of 10",
            "cloud cover": "3%",
            "rain amount": "0 cm",
            "type": "Clear Night"
          },
          {
            "time": "7:00",
            "temperature": "4°",
            "wind": "SW 12 km/h",
            "humidity": "70%",
            "uv index": "0 of 10",
            "cloud cover": "0%",
            "rain amount": "0 cm",
            "type": "Clear Night"
          }
        ],
        "day": {
          "avg. weather": {
            "rain chance": "2%",
            "wind": "SW 20 km/h"
          },
          "sunrise": "7:12",
          "sunset": "18:08"
        },
        "night": {
          "avg. weather": {
            "rain chance": "5%",
            "wind": "WSW 12 km/h"
          },
          "moonrise": "1:51",
          "moonset": "16:16",
          "moonphase": "Waning Crescent"
        }
      }
    ]
  }
}
```


## Setup
Run to install dependencies: 
```bash
pip install -r requirements.txt
```

