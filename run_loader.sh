#!/bin/bash

# Change to the scripts directory
cd pipeline/load

# Set title
echo -en "\033]0;Loader\007"

# Run the Python script
python3 mongoload.py

# Keep virtualenv activated after running
# Uncomment the next line if needed
# source venv/Scripts/deactivate
