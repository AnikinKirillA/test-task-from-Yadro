#!/bin/bash
set -e
echo "Building images..."
docker compose build
echo "Build complete."
