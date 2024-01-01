#!/bin/bash

# Change to the process directory
cd pipeline/process

# Set title
echo -en "\033]0;Process\007"

# Run the Python script
python3 analysis.py
