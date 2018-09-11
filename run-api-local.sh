#!/bin/bash

PYTHONPATH=$(pwd)/src/
export PYTHONPATH

function prepare_venv() {
    virtualenv -p python3 venv && source venv/bin/activate && python3 "$(which pip3)" install -r requirements.txt && python3 "$(which pip3)" install git+https://github.com/fabric8-analytics/fabric8-analytics-auth.git
}

[ "$NOVENV" == "1" ] || prepare_venv || exit 1

# Usage info
# Ref. Link http://mywiki.wooledge.org/BashFAQ/035
show_help() {
cat << EOF
Usage: ${0##*/} [-h] [-t MAJORITY_THRESHOLD] [-p SERVER_PORT]...
Bring up the API on you local system.

    -h display this help and exit
    -t MAJORITY_THRESHOLD Set the outlier threshold value
    -p SERVICE_PORT The port where the license service runs.
EOF
}

#Set default values
threshold=0.6
port=6006

while getopts ht:p: opt; do
# t and p are optional arguments, but require a value when present in the command line.
  case $opt in
    h)
      show_help
      exit 0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    t) threshold=$OPTARG
      ;;
    p) port=$OPTARG
      ;;
  esac
done

export MAJORITY_THRESHOLD=$threshold
export SERVICE_PORT=$port
export DATA_DIR=tests
PYTHONPATH=$(pwd)/src
export PYTHONPATH
cp src/config.py.template src/config.py
gunicorn -b 0.0.0.0:"$SERVICE_PORT" rest_api:app
