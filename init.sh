#!/bin/bash

gnome-terminal --tab --title="Loader" --command="bash -c 'bash run_loader.sh; exec bash'" &
gnome-terminal --tab --title="Process" --command="bash -c 'bash run_process.sh; exec bash'" &
gnome-terminal --tab --title="Scraper" --command="bash -c 'bash run_scraper.sh; exec bash'" &
gnome-terminal --tab --title="Server" --command="bash -c 'bash run_server.sh; exec bash'" &
gnome-terminal --tab --title="Client" --command="bash -c 'bash run_client.sh; exec bash'" &
