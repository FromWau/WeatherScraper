#!/bin/sh

info_to_icon() {    
    case $1 in
        'Sunny')
            echo '☀ ';;
        'Night Clear')
            echo ' ';;
        'Mostly Sunny')
            echo ' ';;
        'Partly Cloudy')
            echo ' ';;
        'Partly Cloudy Night')
            echo ' ';;
        'Mostly Cloudy')
            echo ' ';;
        'Mostly Cloudy Night')
            echo ' ';;
        'Cloudy')
            echo ' ';;
        'Scattered Showers')
            echo ' ';;
        'Rain')
            echo ' ';;
        *)
            echo "$1";;
        esac
}

json=$(python weather_scraper.py 38d35340a098212bc3ae7aa6ff89ce95a7eed769997999f8ad0804d2f3ccd560)
weather=$(echo "$json" | jq '.location.forecasts' | jq '.[0].weather')


# forecast 1
tmp1=$(echo "$weather" | jq -r '.[0].temperature')
typ1=$(echo "$weather" | jq -r '.[0].info')
tmp1_num=$(echo "$tmp1" | tr -d '°')
icon1=$(info_to_icon "$typ1")

# forecast 2
tmp2=$(echo "$weather" | jq -r '.[1].temperature')
typ2=$(echo "$weather" | jq -r '.[1].info')
tmp2_num=$(echo "$tmp2" | tr -d '°')
icon2=$(info_to_icon "$typ2")

# Set the arrow for the corresponding diff temps
if [ "$tmp1_num" -lt "$tmp2_num" ]; 
then
    tmp_diff='↗ '
elif [ "$tmp1_num" -eq "$tmp2_num" ];
then
    tmp_diff='→ '
else
    tmp_diff='↘ '
file
fi

echo "$icon1 $tmp1 $tmp_diff $icon2 $tmp2"
