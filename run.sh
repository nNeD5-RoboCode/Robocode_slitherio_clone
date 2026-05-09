#!/usr/bin/env bash


set -o errexit
set -o pipefail
set -o nounset

# debuging
set -o xtrace




python main.py &
python main.py &
python main.py &

wait
