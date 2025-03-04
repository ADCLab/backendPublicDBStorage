#!/bin/bash

docker build -t adclab/keydb:v0.3.0 .
docker push adclab/keydb:v0.3.0
