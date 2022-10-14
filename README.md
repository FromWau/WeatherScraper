# WeatherScraper
Scraps the weather.com site and returns an up to 48h weather forecast in json format.

## But why
Primarly made to be piped into `jq` and used for polybar.

## Usage

Example, Get the next weather forecast for Vienna:
```shell
python weather_scraper.py -m 1 https://weather.com/en-GB/weather/hourbyhour/l/b1c12cb5f559c61ffb70bb86034f904e94f0bf0817f3adc85177b27014c8fbe0 
```

Returns:
```json
{
  "timestamp": "2022-10-14 05:23:09",
  "url": "https://weather.com/en-GB/weather/hourbyhour/l/b1c12cb5f559c61ffb70bb86034f904e94f0bf0817f3adc85177b27014c8fbe0",
  "location": {
    "city": "Vienna",
    "state": "Vienna",
    "country": "Austria"
  },
  "dates": {
    "2022-10-14": {
      "6:00": {
        "weather": {
          "Temperature": "10°",
          "Wind": "W 2 mph",
          "Humidity": "94%",
          "UV Index": "0 of 10",
          "Cloud Cover": "80%",
          "Rain Amount": "0 cm"
        }
      }
    }
  }
}
```

## How to change location/ units/ language
Just go to https://weather.com/weather/hourbyhour, change the settings (top-right corner) or  
search for a location and run the script with the new url.


## Setup
Run to install dependencies: 
```bash
pip install -r requirements.txt
```

