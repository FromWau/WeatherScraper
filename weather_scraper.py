#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import re
import json
from datetime import datetime, timedelta
import argparse
import os

import sys



def main():
    
    # define argparse
    parser = argparse.ArgumentParser(
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        description     = "scraps weather.com for weather data"
    )
    
    parser.add_argument("location_code", type=str,                         help="specifies the location for where to check the weather")
    parser.add_argument("-n", "--n",     type=valid_n,    default=2,       help="specify how many forecasts should be scraped") 
    parser.add_argument("-u", "--unit",  type=valid_unit, default='C',     help="sets the unit, valid units: C, F, H")
    parser.add_argument("-l", "--lang",  type=valid_lang, default='en-GB', help="sets the language, format: <languadge code>-<country code>")
    parser.add_argument("-d", "--dir",   type=valid_dir,                   help="specify the directory for the output.json file")

    args = parser.parse_args()

    # Check if everything is valid
    if args.location_code and args.n and args.unit and args.lang: 

        json = scrap_it(args.location_code, args.n, args.unit, args.lang)
        
        # Export via file or stdout
        if args.dir:
            with open(args.dir+'/output.json', "w") as f:
                   f.write(json + '\n')
        else:
            print(json)
    
        
  
# check if url is valid via regex
def valid_url(value):
    if not re.search('^https://weather.com/\S+/weather/hourbyhour/l/\S+$', value):
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid url")
    return value


# Check if max is a signed int
def valid_n(value):
    try:
        n = int(value)
        if n < 1: 
            raise argparse.ArgumentTypeError(f"'{value}' is not greater 0")
        return n
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not an int")


# Check if unit is valid
def valid_unit(value):
    match value:
        case 'C' | 'Celsius':
            return 'm'
    
        case 'F' | 'Fahrenheit':
            return 'e'
        
        case 'H' | 'Hybrid':
            return 'h'

        case _:
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid unit. Valid units: C, F, H")


# Check if lang is valid
def valid_lang(value):
    if not re.match('^([a-z]{2})-([A-z]{2})$', value):
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid language setting, format: <languadge code>-<country code>")
    return value


# Check if dir exists
def valid_dir(value):
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid dir")
    return value
    


# Gets weather.com URL and returns a json object containing the weather data.
def scrap_it(location_code, n, unit, lang):
    
    url_hourly = 'https://weather.com/' + lang + '/weather/hourbyhour/l/' + location_code + '?unit=' + unit 
    url_days   = 'https://weather.com/' + lang + '/weather/tenday/l/'     + location_code + '?unit=' + unit 
    

    # Setting up scraper
    page_hourly = BeautifulSoup(requests.get(url_hourly).text, 'lxml')
    page_days   = BeautifulSoup(requests.get(url_days  ).text, 'lxml')

    # Getting the location
    location = page_hourly.find('span', class_ = 'LocationPageTitle--PresentationName--1QYny').text.strip().split(', ')

    # Init the dict
    data = {}
    data['request'] = {}
    data['request']['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['request']['urls'] = [url_hourly, url_days]
    data['location'] = {}
    data['location']['city'] = location[0]
    
    # if location has only city and country eg.: Vienna
    if len(location) == 2:
        data['location']['state'] = location[0]
    else:
        data['location']['state'] = location[1]
    data['location']['country'] = location[len(location)-1]
    
    data['location']['locale_timestamp'] = {}
    data['location']['forecasts'] = {}
    data['location']['forecasts']['dates'] = {}

    # Iterate over n forecasts
    for index in range(0, n):
        
        # Check if its a new day
        ugly_date = page_hourly.find( 'h2', id = re.compile('currentDateId' + str(index) + '$') )
        if ugly_date != None:
                            
            # Format the date and add it to dict
            ugly_date = str(ugly_date.text) + ' ' + str(datetime.now().year)
            date = datetime.strptime(ugly_date, '%A, %d %B %Y')
            str_date = str(date.strftime("%Y-%m-%d"))

            data['location']['forecasts']['dates'][str_date] = {}
            data['location']['forecasts']['dates'][str_date]['day'] = {}
            data['location']['forecasts']['dates'][str_date]['night'] = {}
            data['location']['forecasts']['dates'][str_date]['weather'] = {}

        
        # Add Day / Night with rise and set info
        # TODO sometimes overwrites the options from other dates
        day_night = page_days.find( id = re.compile('detailIndex' + str(index) + '$') )
        if day_night != None:
            

            # date add day sunrise and sunset
            sunrise_time = day_night.find('span', attrs={ "data-testid" : "SunriseTime" }).text
            sunset_time  = day_night.find('span', attrs={ "data-testid" : "SunsetTime" }) .text
        
            data['location']['forecasts']['dates'][str_date]['day']['sunrise'] = sunrise_time
            data['location']['forecasts']['dates'][str_date]['day']['sunset']  = sunset_time 
            

            # date add night moonrise and moonset
            moonrise_time = day_night.find('span', attrs={ "data-testid" : "MoonriseTime" }).text
            moonset_time  = day_night.find('span', attrs={ "data-testid" : "MoonsetTime" }) .text
            moonphase     = day_night.find('span', attrs={ "data-testid" : "moonPhase" })   .text

            data['location']['forecasts']['dates'][str_date]['night']['moonrise']  = moonrise_time
            data['location']['forecasts']['dates'][str_date]['night']['moonset']   = moonset_time
            data['location']['forecasts']['dates'][str_date]['night']['moonphase'] = moonphase
    
        # TODO
        # current day/night state 
        # if time at location is smaller sunrise => yesterday night 
        # else if time at location is between sunrise and [sunset or moonrise?] => day
        # else its night today





        # Check if its a new weather section
        weather = page_hourly.find( id = re.compile('detailIndex' + str(index) + '$') )
        if weather != None:
            
            # Get the time for this weather section
            time = weather.find( class_ = 'Disclosure--Summary--UuybP DaypartDetails--Summary--3IBUr Disclosure--hideBorderOnSummaryOpen--ZdSDc' )\
                .div.div.h3.text    
            
            # Add the time to the dict
            
            data['location']['forecasts']['dates'][str_date]['weather'][time] = {} 
            
            # Iterate over weather stats
            for li in weather.find( class_ = 'DaypartDetails--Content--hJ52O DaypartDetails--contentGrid--1SWty')\
                .find( class_ = '' ).ul:
                
                # Get label (replace Feels Like with Temperature)
                label = li.div.find_all('span')[0].text
                if label == "Feels Like": label = "Temperature"
                
                # Get the value
                value = li.div.find_all('span')[1].text

                # Add the stats to the dict
                data['location']['forecasts']['dates'][str_date]['weather'][time][label] = value 
        
    
        # Set the locale_timestamp for the location and last_updated
        if index == 0:
            # get the next forecast hour for the country
            next_date = datetime(year=date.year, month=date.month, day=date.day, 
                                 hour=int(time.split(':')[0]), minute=int(time.split(':')[1]))
            
            # build the current datetime for the location
            ugly_current_time = page_hourly.find('div', class_ = 'HourlyForecast--timestamp--MVnBF').text.strip('As of ').split(' ')[0]
            current_time = datetime.strptime(ugly_current_time, '%H:%M')
            current_date = next_date.replace(hour=current_time.hour, minute=current_time.minute)
           
            # check if current datetime needs to be ajusted
            if current_date > next_date:
                current_date = current_date - timedelta(days=1)

            data['location']['locale_timestamp'] = current_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # TODO add last_updated 
            # data['request']['last_updated'] = {}
            # add timzone diff from now() and locale_timestamp to locale_timestamp => last_updated 
    


        
    # Make it json
    json_data = json.dumps(data)
    return json_data

      
if __name__ == "__main__":
    main()

    
