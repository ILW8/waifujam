#!/usr/bin/env bash

docker build --tag "waifujam" .
docker stop gunicorn || true
docker run --name gunicorn -p 80:80 -d --rm "waifujam" gunicorn main:app --workers 6 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80
