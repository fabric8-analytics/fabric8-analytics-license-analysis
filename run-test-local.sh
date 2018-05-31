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

export PYTHONPATH=`pwd`/src

function prepare_venv() {
	virtualenv -p python3 venv && source venv/bin/activate && python3 `which pip3` install -r requirements.txt
}

[ "$NOVENV" == "1" ] || prepare_venv || exit 1

export DISABLE_AUTHENTICATION=1

# the module src/config.py must exists because it is included from stack_license and license_analysis.py as well.
cp src/config.py.template src/config.py
cd tests
mkdir testdir1
mkdir testdir4
PYTHONDONTWRITEBYTECODE=1 python3 `which pytest` --cov=../src/ --cov-report term-missing -vv -s .
rm -rf testdir1
rm -rf testdir4
