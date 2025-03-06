#!/bin/sh

# Set default values if environment variables are not provided
WORKERS=${NUM_WORKERS:-1}  # Default: 1 workers
IP_ADDRESS=${IP_ADDRESS:-0.0.0.0}  # Default: Bind to all interfaces
PORT=${PORT:-5000}  # Default: Port 5000

# Start Gunicorn with environment-configured settings
gunicorn -w "$WORKERS" -k gthread -b "$IP_ADDRESS:$PORT" flask2mongo:app