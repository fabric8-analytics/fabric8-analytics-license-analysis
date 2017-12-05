#!/bin/bash

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
export PYTHONPATH=`pwd`/src
cp src/config.py.template src/config.py
gunicorn -b 0.0.0.0:$SERVICE_PORT rest_api:app