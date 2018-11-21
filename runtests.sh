#! /bin/bash

# each command can cause test failure
set -e

COVERAGE_THRESHOLD=90

export TERM=xterm
TERM=${TERM:-xterm}

# set up terminal colors
NORMAL=$(tput sgr0)
RED=$(tput bold && tput setaf 1)
GREEN=$(tput bold && tput setaf 2)
YELLOW=$(tput bold && tput setaf 3)


threshold=0.6

export MAJORITY_THRESHOLD=$threshold
export DATA_DIR=.

PYTHONPATH=$(pwd)/src
export PYTHONPATH

printf "%sCreate Virtualenv for Python deps ..." "${NORMAL}"

function prepare_venv() {
    VIRTUALENV=$(which virtualenv)
    if [ $? -eq 1 ]
    then
        # python34 which is in CentOS does not have virtualenv binary
        VIRTUALENV=$(which virtualenv-3)
    fi

    ${VIRTUALENV} -p python3 venv && source venv/bin/activate && python3 "$(which pip3)" install -r requirements.txt\
     && "$(which pip3)" install git+https://github.com/fabric8-analytics/fabric8-analytics-auth.git@fff8f49
    
    if [ $? -ne 0 ]
    then
        printf "%sPython virtual environment can't be initialized%s" "${RED}" "${NORMAL}"
        exit 1
    fi
    printf "%sPython virtual environment initialized%s\n" "${YELLOW}" "${NORMAL}"
}

[ "$NOVENV" == "1" ] || prepare_venv || exit 1

export DISABLE_AUTHENTICATION=1

# the module src/config.py must exists because it is included from stack_license and license_analysis.py as well.
cp src/config.py.template src/config.py

echo "*****************************************"
echo "*** Cyclomatic complexity measurement ***"
echo "*****************************************"
radon cc -s -a -i venv .

echo "*****************************************"
echo "*** Maintainability Index measurement ***"
echo "*****************************************"
radon mi -s -i venv .

echo "*****************************************"
echo "*** Unit tests ***"
echo "*****************************************"
cd tests || exit
mkdir testdir1
mkdir testdir4
PYTHONDONTWRITEBYTECODE=1 python3 "$(which pytest)" --cov=../src/ --cov-report term-missing --cov-fail-under=$COVERAGE_THRESHOLD -vv .

cp -r ../.git ./
codecov --token=3a540a46-f7e9-4050-b36a-97f81b948bcb
printf "%stests passed%s\n\n" "${GREEN}" "${NORMAL}"
