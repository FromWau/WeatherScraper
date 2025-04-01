# WeatherScraper
Scraps the weather.com site and returns a up to 48h weather forecast in json format.

## But why
Primarily made to be piped into `jq` and used for a bar.  
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
For example, searching for London will redirect you to:  
https://weather.com/weather/today/l/5d3ac36b50e4aa01e9916508005d45eab1dffb15cb59d5b38cce3ca54d24c65d

The location_code is the last part of the url, so in this case:  
5d3ac36b50e4aa01e9916508005d45eab1dffb15cb59d5b38cce3ca54d24c65d



## Examples 

### polybar Module
```ini
[module/weather-scraper]
type              = custom/script
exec              = cd ~/.config/polybar/scripts && ./use_case_example.sh
internal          = 600

label-font        = 1
label             = %output%
format-foreground = ${colors.primary}
format-background = ${colors.background}
```

Displays on the bar:

![alt text](https://raw.githubusercontent.com/FromWau/WeatherScraper/main/polybar-weather-module.png)



### Bash
Get the next two weather forecasts for London:
```shell
python weather_scraper.py 5d3ac36b50e4aa01e9916508005d45eab1dffb15cb59d5b38cce3ca54d24c65d
```

Returns (pipe into jq for human readable output):
```json
{
  "request": {
    "timestamp": "2022-10-22 07:54:07",
    "urls": [
      "https://weather.com/en-GB/weather/hourbyhour/l/5d3ac36b50e4aa01e9916508005d45eab1dffb15cb59d5b38cce3ca54d24c65d?unit=m",
      "https://weather.com/en-GB/weather/tenday/l/5d3ac36b50e4aa01e9916508005d45eab1dffb15cb59d5b38cce3ca54d24c65d?unit=m"
    ],
    "last_updated": "2022-10-22 07:51:00"
  },
  "location": {
    "city": "London",
    "state": "London",
    "country": "England",
    "locale_timestamp": "2022-10-22 06:51:00",
    "forecasts": [
      {
        "date": "2022-10-22",
        "lowest temperature": "14°",
        "highest temperature": "18°",
        "weather": [
          {
            "time": "7:00",
            "temperature": "13°",
            "feels like": "12°",
            "info": "Partly Cloudy Night",
            "rain chance": "2%",
            "rain amount": "0 cm",
            "humidity": "90%",
            "wind": "SW 11 km/h",
            "cloud cover": "33%",
            "uv index": "0 of 10"
          },
          {
            "time": "8:00",
            "temperature": "12°",
            "feels like": "11°",
            "info": "Partly Cloudy",
            "rain chance": "2%",
            "rain amount": "0 cm",
            "humidity": "90%",
            "wind": "SW 10 km/h",
            "cloud cover": "47%",
            "uv index": "0 of 10"
          }
        ],
        "day": {
          "avg. weather": {
            "temperature": "18°",
            "info": "Mostly Cloudy",
            "rain chance": "15%",
            "humidity": "81%",
            "wind": "SSW 17 km/h",
            "uv index": "1 of 10"
          },
          "sunrise": "7:36",
          "sunset": "17:52"
        },
        "night": {
          "avg. weather": {
            "temperature": "14°",
            "info": "Scattered Showers",
            "rain chance": "15%",
            "humidity": "88%",
            "wind": "SSW 17 km/h",
            "uv index": "0 of 10"
          },
          "moonrise": "3:36",
          "moonset": "17:11",
          "moonphase": "Waning Crescent"
        }
      }
    ]
  }
}
```


## Setup
Install uv: 
```bash
pacman -S uv
```

Build and run:
```bash 
uv build
uv run weather_scraper.py -h
```

Install jq (only needed for polybar or for selecting specific data):
```bash
pacman -S jq
```

