#!/bin/bash
daemon=doord.py
project_root="$(realpath $(dirname $(realpath $0))/..)"
echo "Running $daemon with mock card reads"

set -a
AUTHORIZED_CARDS_URL="file://localhost$project_root/test/test-cards.json"
OPEN_DOOR_SCRIPT="$project_root/test/open-door-mock"
READER_DAEMON="$project_root/test/nfcreader-mock"
$project_root/$daemon
