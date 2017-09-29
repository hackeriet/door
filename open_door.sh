#!/bin/bash
set -eux

# Pins are numbered after the wiringPi scheme (https://pinout.xyz/pinout/wiringpi)
GPIO_PIN_DOOR=${GPIO_PIN_DOOR:-0}
STAY_UNLOCKED_SEC=${STAY_UNLOCKED_SEC:-2}

STATE_UNLOCKED=1
STATE_LOCKED=0

# This function will always be invoked on script exit
function cleanup {
  # Lock the door
  gpio write 0 $STATE_LOCKED
  echo "Door locked"
}
trap cleanup EXIT

# Unlock the door
gpio mode $GPIO_PIN_DOOR out
gpio write $GPIO_PIN_DOOR $STATE_UNLOCKED
echo "Door unlocked"
sleep $STAY_UNLOCKED_SEC
