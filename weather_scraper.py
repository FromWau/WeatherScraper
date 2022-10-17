#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import re
import json
from datetime import datetime, timedelta
import argparse
import os



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
    location = page_hourly.find('span', class_ = 'LocationPageTitle--PresentationName--1QYny')\
        .text.strip().split(', ')

    # Init the dict
    data = {}
    data['request']  = {}
    data['request']['timestamp']    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['request']['urls']         = [url_hourly, url_days]
    data['request']['last_updated'] = {}
    
    data['location'] = {}
    data['location']['city']        = location[0]
    
    # if location has only city and country eg.: Vienna
    if len(location) == 2:
        data['location']['state']   = location[0]
    else:
        data['location']['state']   = location[1]
    data['location']['country']     = location[len(location)-1]
    

    # Find out the current date 
    ugly_date = page_hourly.find( 'h2', id = re.compile('currentDateId0$') )
    ugly_date = str(ugly_date.text) + ' ' + str(datetime.now().year)
    hourly_date = datetime.strptime(ugly_date, '%A, %d %B %Y')
    
    # Get locale timestamp and add it to dict
    ugly_time = page_hourly.find('div', class_ = 'HourlyForecast--timestamp--MVnBF')\
        .text.strip('As of ').split(' ')[0].split(':')

    locale_date = hourly_date.replace(hour=int(ugly_time[0]), minute=int(ugly_time[1]))
    
    data['location']['locale_timestamp'] = locale_date.strftime("%Y-%m-%d %H:%M:%S")


    # Calc the last_updated time in the users timezone (will be wrong if the last_updated time is bigger 15min.)
    now = datetime.now().replace(second=0, microsecond=0)   

    if now > locale_date:
        diff = now - locale_date
        diff_min = int(diff.total_seconds()/60)
        last_updated = locale_date + timedelta(minutes=( int(diff_min/15) * 15) )

    elif now < locale_date:
        diff = locale_date - now     
        diff_min = int(diff.total_seconds()/60)
        last_updated = locale_date - timedelta(minutes= diff_min + (15-diff_min%15))

    else:
        last_updated = now
    
    data['request']['last_updated'] = last_updated.strftime("%Y-%m-%d %H:%M:%S")

    data['location']['forecasts'] = {}
    data['location']['forecasts']['dates'] = {}
   





    # Check if yeserday night
    day_night = page_days.find( id = re.compile('detailIndex0$') )

    if day_night != None:
            
        # get day and check if we are on the same day
        day_night_ugly_date = day_night.find('span', class_ = 'DailyContent--daypartDate--2A3Wi').text
        day_night_day = int(day_night_ugly_date.split(' ')[1])
        
        # TODO Check if it is yesterday night (eg 02:00) and get the night stats
        
        # idk if works yet
        yesterday = hourly_date - timedelta(days=1)
        if day_night_day == yesterday.day:
            was_yesterday = True

            str_yesterday = str(yesterday.strftime("%Y-%m-%d"))
            
            data['location']['forecasts']['dates'][str_yesterday] = {}
            data['location']['forecasts']['dates'][str_yesterday]['night'] = {}
            
            # date add night moonrise and moonset
            moonrise_time = day_night.find('span', attrs={ "data-testid" : "MoonriseTime" })
            moonset_time  = day_night.find('span', attrs={ "data-testid" : "MoonsetTime" })
            moonphase     = day_night.find('span', attrs={ "data-testid" : "moonPhase" })
            
            if moonrise_time != None:
                data['location']['forecasts']['dates'][str_yesterday]['night']['moonrise']  = moonrise_time.text
            if moonset_time != None:
                data['location']['forecasts']['dates'][str_yesterday]['night']['moonset']   = moonset_time.text
            if moonphase != None:
                data['location']['forecasts']['dates'][str_yesterday]['night']['moonphase'] = moonphase.text
        else:
            was_yesterday = False











    # Iterate over n forecasts and create the weather structure
    for index in range(0, n):
        
        ugly_date = page_hourly.find( 'h2', id = re.compile('currentDateId' + str(index) + '$') )
        if ugly_date != None:
            
            # Format the date and add it to dict
            ugly_date = str(ugly_date.text) + ' ' + str(datetime.now().year)
            hourly_date = datetime.strptime(ugly_date, '%A, %d %B %Y')
            str_date = hourly_date.strftime('%Y-%m-%d')
            
            data['location']['forecasts']['dates'][str_date] = {}
            data['location']['forecasts']['dates'][str_date]['weather'] = {}
   

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
                value = li.div.find_all('span')[1].text
            
                data['location']['forecasts']['dates'][str_date]['weather'][time][label] = value 
            
            # Add icon info as stat -> is cloudy, foggy,mostly sunny, ...    
            type = weather.find(class_ = 'DetailsSummary--condition--24gQw').svg.text   
            data['location']['forecasts']['dates'][str_date]['weather'][time]['Type'] = type
            


    for index in range(0,len(data['location']['forecasts']['dates'])):
        day_night = page_days.find( id = re.compile('detailIndex' + str(index) + '$') )
        if day_night != None:
            

            # Get day_night date
            ugly_date = day_night.find('span', class_ = 'DailyContent--daypartDate--2A3Wi')
            if ugly_date != None:
                
                # Format the date and add it to dict
                ugly_date_day = str(ugly_date.text).split(' ')[1]

                
                # Find the existiing date and add the day_night stats
                for key in data['location']['forecasts']['dates'].keys():

                    if re.search('^.*-' + ugly_date_day + '$', key):
                        str_date = key 
                        
                        # Add avg. rain chance and avg. wind    
                        day_night_avg = day_night.find_all(class_ = 'DailyContent--dataPoints--1Nya6')
                        
                        # only night present
                        if len(day_night_avg) == 1:
                            item = day_night_avg[0].find_all('div')
                            
                            data['location']['forecasts']['dates'][str_date]['night'] = {}
                            data['location']['forecasts']['dates'][str_date]['night']['avg. weather'] = {}
                            data['location']['forecasts']['dates'][str_date]['night']['avg. weather']['Rain Chance'] = item[0].span.text
                            data['location']['forecasts']['dates'][str_date]['night']['avg. weather']['Wind']        = item[2].span.text
                        
                        # day/night stats present
                        elif len(day_night_avg) == 2:
                           
                            for item_count in range(0,2):
                                item = day_night_avg[item_count].find_all('div')
                                
                                if item_count == 0: 
                                    data['location']['forecasts']['dates'][str_date]['day'] = {}
                                    data['location']['forecasts']['dates'][str_date]['day']  ['avg. weather'] = {}
                                    data['location']['forecasts']['dates'][str_date]['day']  ['avg. weather']['Rain Chance'] = item[0].span.text
                                    data['location']['forecasts']['dates'][str_date]['day']  ['avg. weather']['Wind']        = item[2].span.text
                                else:
                                    data['location']['forecasts']['dates'][str_date]['night'] = {}
                                    data['location']['forecasts']['dates'][str_date]['night']['avg. weather'] = {}
                                    data['location']['forecasts']['dates'][str_date]['night']['avg. weather']['Rain Chance'] = item[0].span.text
                                    data['location']['forecasts']['dates'][str_date]['night']['avg. weather']['Wind']        = item[2].span.text


                        # Add day sunrise and sunset
                        sunrise_time = day_night.find('span', attrs={ "data-testid" : "SunriseTime" })
                        sunset_time  = day_night.find('span', attrs={ "data-testid" : "SunsetTime" })

                        if sunrise_time != None:
                            data['location']['forecasts']['dates'][str_date]['day']['sunrise']  = sunrise_time.text
                        if sunset_time != None:
                            data['location']['forecasts']['dates'][str_date]['day']['sunset']   = sunset_time.text

                        # Add night moonrise and moonset
                        moonrise_time = day_night.find('span', attrs={ "data-testid" : "MoonriseTime" })
                        moonset_time  = day_night.find('span', attrs={ "data-testid" : "MoonsetTime" })
                        moonphase     = day_night.find('span', attrs={ "data-testid" : "moonPhase" })
                        
                        if moonrise_time != None:
                            data['location']['forecasts']['dates'][str_date]['night']['moonrise']  = moonrise_time.text
                        if moonset_time != None:
                            data['location']['forecasts']['dates'][str_date]['night']['moonset']   = moonset_time.text
                        if moonphase != None:
                            data['location']['forecasts']['dates'][str_date]['night']['moonphase'] = moonphase. text



    

    json_data = json.dumps(data)
    return json_data

      
if __name__ == "__main__":
    main()

    
