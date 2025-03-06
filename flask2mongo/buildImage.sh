#!/bin/bash

docker build -t adclab/flask2mongo:v0.4.3 -t adclab/flask2mongo:latest .
docker push adclab/flask2mongo:v0.4.3
docker push adclab/flask2mongo:latest