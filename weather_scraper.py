#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import re
import json
from datetime import datetime
import argparse



def main():
    
    # define argparse
    parser = argparse.ArgumentParser(description="Scraps weather.com for weather data.")
    parser.add_argument("url", type=valid_url,
                        help="URL needs to be from weather.com\nTo change language/ units/ location just set them at the weather.com page and copy the URL (make sure it is the 'Hourly' site not 'Today')")
    parser.add_argument("-m", "--max", type=valid_max, default=48, help="specify how many hours should be scraped.") 
    args = parser.parse_args()
    
    # if url and max are valid
    if args.url and args.max:
       
        # Run scraper with the url and print to stout
        json = scrap_it(args.url, args.max)
        print(json)



# Check if max is a signed int
def valid_max(value):
    try:
        max = int(value)
        if max < 1: 
            raise argparse.ArgumentTypeError(f"'{value}' is not greater 0")
        return max
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not an int")



# check if url is valid via regex
def valid_url(value):
    if not re.search('^https://weather.com/\S+/weather/hourbyhour/l/\S+$', value):
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid url")
    return value



# Gets weather.com URL and returns a json object containing the weather data.
def scrap_it(url, max=48):
    
    # Setting up scraper
    page = BeautifulSoup(requests.get(url).text, 'lxml')

    # Getting the location
    location = page.find('span', class_ = 'LocationPageTitle--PresentationName--1QYny').text.strip().split(', ')

    # Init the dict
    data = {}
    data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['url'] = url
    data['location'] = {}
    data['location']['city'] = location[0]
    
    # if location has only city and country eg.: Vienna
    if len(location) == 2:
        data['location']['state'] = location[0]
    else:
        data['location']['state'] = location[1]
    data['location']['country'] = location[len(location)-1]
    data['dates'] = {}

    # Get the data section of the page
    hourly = page.find('div', class_ = 'HourlyForecast--DisclosureList--3CdxR')
    
    # Iterate over the next 48h (is the maximum)
    for index in range(0, max):
        
        # Check if its a new day
        ugly_date = hourly.find( 'h2', id = re.compile('currentDateId' + str(index) + '$') )
        if ugly_date != None:
            
            # Format the date and add it to dict
            str_date = str(ugly_date.text) + ' ' + str(datetime.now().year)
            date = str( datetime.strptime(str_date, '%A, %d %B %Y').strftime("%Y-%m-%d") )
            data['dates'][date] = {}
        
        # Check if its a new weather section
        weather = hourly.find( id = re.compile('detailIndex' + str(index) + '$') )
        if weather != None:
            
            # Get the time for this weather section
            time = weather.find( class_ = 'Disclosure--Summary--UuybP DaypartDetails--Summary--3IBUr Disclosure--hideBorderOnSummaryOpen--ZdSDc' )\
                .div.div.h3.text    
            
            # Add the time to the dict
            data['dates'][date][time] = {} 
            data['dates'][date][time]['weather'] = {} 
            
            # Iterate over weather stats
            for li in weather.find( class_ = 'DaypartDetails--Content--hJ52O DaypartDetails--contentGrid--1SWty')\
                .find( class_ = '' ).ul:
                
                # Get label (replace Feels Like with Temperature)
                label = li.div.find_all('span')[0].text
                if label == "Feels Like": label = "Temperature"
                
                # Get the value
                value = li.div.find_all('span')[1].text

                # Add the stats to the dict
                data['dates'][date][time]['weather'][label] = value 

    # Make it json
    json_data = json.dumps(data)
    return json_data

      
if __name__ == "__main__":
    main()

    
