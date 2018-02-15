#!/bin/bash

set -ex

. cico_setup.sh

build_image
./runtests.sh
push_image
