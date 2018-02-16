#! /bin/bash


threshold=0.6

export MAJORITY_THRESHOLD=$threshold
export DATA_DIR=.

export PYTHONPATH=`pwd`/src

function prepare_venv() {
    VIRTUALENV=`which virtualenv`
    if [ $? -eq 1 ]; then
        # python34 which is in CentOS does not have virtualenv binary
        VIRTUALENV=`which virtualenv-3`
    fi

    ${VIRTUALENV} -p python3 venv && source venv/bin/activate && python3 `which pip3` install pytest pytest-cov
}

[ "$NOVENV" == "1" ] || prepare_venv || exit 1

# the module src/config.py must exists because it is included from stack_license and license_analysis.py as well.
cp src/config.py.template src/config.py
cd tests
PYTHONDONTWRITEBYTECODE=1 python3 `which pytest` --cov=../src/ --cov-report term-missing -vv .
