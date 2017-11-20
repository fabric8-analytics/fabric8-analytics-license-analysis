#! /bin/bash


# Usage info
# Ref. Link http://mywiki.wooledge.org/BashFAQ/035
show_help() {
cat << EOF
Usage: ${0##*/} [-h] [-t MAJORITY_THRESHOLD]
Run the unit test in your local environment.

    -h display this help and exit
    -t MAJORITY_THRESHOLD Set the outlier threshold value
EOF
}

#Set default values
threshold=0.6

while getopts ht: opt; do
# t is an optional argument, but requires a value when present in the command line.

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
  esac
done

export MAJORITY_THRESHOLD=$threshold
export DATA_DIR=.
cd tests
pytest . -v