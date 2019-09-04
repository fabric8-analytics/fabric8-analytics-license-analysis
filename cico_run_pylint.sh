#!/bin/bash

set -ex

prep() {
    yum -y update
    yum -y install epel-release
    yum -y install python36 python36-virtualenv which
}

# this script is copied by CI, we don't need it
rm -f env-toolkit

prep
./qa/detect-common-errors.sh
./qa/detect-dead-code.sh
./qa/run-linter.sh
