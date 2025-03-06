#!/bin/bash

docker build -t adclab/keydb:v0.4.1 -t adclab/keydb:latest .
docker push adclab/keydb:v0.4.1
docker push adclab/keydb:latest