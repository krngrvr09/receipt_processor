#!/bin/bash

docker build -t receipt_processor .
docker run -p 127.0.0.1:8080:8000 receipt_processor
