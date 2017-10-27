#!/bin/bash
daemon=doord.py
project_root="$(realpath $(dirname $(realpath $0))/..)"
echo "Running $daemon with mock card reads"
TESTING=true $project_root/$daemon
