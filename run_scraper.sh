#!/bin/bash

# Activate the virtualenv
source venv/Scripts/activate

# Change to the scraper directory
cd pipeline/scraper

# Set title
echo -en "\033]0;Scraper\007"

# Uncomment and replace the next two lines with your URLs if needed
# python live.py --url https://www.youtube.com/watch?v=TPcmrPrygDc
# python live.py --url https://www.youtube.com/watch?v=YZ0QUd-URt4

# Prompt user for URL input
read -p "Enter URL to scrape: " URL

# Run script with user input URL
python3 live.py --url "$URL"
