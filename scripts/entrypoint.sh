#!/usr/bin/env bash

#make necessary changes in config.py
gunicorn --pythonpath /src/ -b 0.0.0.0:$SERVICE_PORT rest_api:app



