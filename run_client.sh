#!/bin/bash

echo -en "\033]0;WebApp\007"  # Set terminal title to "WebApp"
cd client/frontend/chat-tracker
npm run dev
