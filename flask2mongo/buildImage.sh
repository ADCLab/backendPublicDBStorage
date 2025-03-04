#!/bin/bash

docker build -t adclab/flask2mongo:v0.4.0 .
docker push adclab/flask2mongo:v0.4.0
