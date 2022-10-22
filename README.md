# WeatherScraper
Scraps the weather.com site and returns an up to 48h weather forecast in json format.

## But why
Primarly made to be piped into `jq` and used for a bar.  
See `use_case_example.sh` for a script that can be used with polybar modules.

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

Returns (pipe into jq for human readable output):
```json
{
  "request": {
    "timestamp": "2022-10-22 06:55:23",
    "urls": [
      "https://weather.com/en-GB/weather/hourbyhour/l/96f2f84af9a5f5d452eb0574d4e4d8a840c71b05e22264ebdc0056433a642c84?unit=m",
      "https://weather.com/en-GB/weather/tenday/l/96f2f84af9a5f5d452eb0574d4e4d8a840c71b05e22264ebdc0056433a642c84?unit=m"
    ],
    "last_updated": "2022-10-22 06:55:00"
  },
  "location": {
    "city": "New York City",
    "state": "NY",
    "country": "United States",
    "locale_timestamp": "2022-10-22 00:55:00",
    "forecasts": [
      {
        "date": "2022-10-22",
        "lowest temperature": "11°",
        "highest temperature": "19°",
        "weather": [
          {
            "time": "1:00",
            "temperature": "12°",
            "feels like": "11°",
            "info": "Clear Night",
            "rain chance": "2%",
            "rain amount": "0 cm",
            "humidity": "58%",
            "wind": "WSW 8 km/h",
            "cloud cover": "0%",
            "uv index": "0 of 10"
          },
          {
            "time": "2:00",
            "temperature": "11°",
            "feels like": "11°",
            "info": "Clear Night",
            "rain chance": "2%",
            "rain amount": "0 cm",
            "humidity": "59%",
            "wind": "WSW 6 km/h",
            "cloud cover": "0%",
            "uv index": "0 of 10"
          }
        ],
        "yesterday_night": {
          "date": "2022-10-21",
          "lowest temperature": "8°",
          "highest temperature": "8°",
          "night": {
            "avg. weather": {
              "temperature": "8°",
              "info": "Clear Night",
              "rain chance": "2%",
              "humidity": "65%",
              "wind": "SW 7 km/h",
              "uv index": "0 of 10"
            },
            "moonrise": "2:55",
            "moonset": "16:40",
            "moonphase": "Waning Crescent"
          }
        },
        "day": {
          "avg. weather": {
            "temperature": "19°",
            "info": "Sunny",
            "rain chance": "5%",
            "humidity": "54%",
            "wind": "SSW 7 km/h",
            "uv index": "4 of 10"
          },
          "sunrise": "7:15",
          "sunset": "18:05"
        },
        "night": {
          "avg. weather": {
            "temperature": "11°",
            "info": "Mostly Cloudy Night",
            "rain chance": "5%",
            "humidity": "72%",
            "wind": "SSW 7 km/h",
            "uv index": "0 of 10"
          },
          "moonrise": "3:59",
          "moonset": "17:02",
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

