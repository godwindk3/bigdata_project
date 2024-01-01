#!/bin/bash

# Change to the backend directory
cd client/backend

# Set title
echo -en "\033]0;BackendServer\007"

# Run the Python script
python3 app.py
