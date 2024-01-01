#!/bin/bash

# Change to the scraper directory
cd pipeline/scraper

# Set title
echo -en "\033]0;Scraper\007"

# Prompt user for URL input
read -p "Enter URL to scrape: " URL

# Run script with user input URL
python3 live.py --url "$URL"
