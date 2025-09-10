#!/bin/bash
set -e
echo "Starting services..."
sudo docker compose run --rm agent pytest -v
echo "Target and agent started."
