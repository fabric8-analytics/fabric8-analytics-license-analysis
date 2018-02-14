#!/bin/bash

set -ex

. cico_setup.sh

prep() {
    yum -y update
    yum -y install epel-release
    yum -y install python34 python34-virtualenv which
}

prep
build_image
./runtests.sh
push_image
