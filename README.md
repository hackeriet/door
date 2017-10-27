# door

GPIO door lock control

- Tested on a Pi Zero W running Raspbian GNU/Linux 9
- The door lock is triggered by raising a single GPIO pin
- Pins are numbered using the [wiringPi scheme][1]
- The cardreader is assumed connected with `i2c` on interface #1 (the lowest i2c pin numbers)

## Wiring

Schematics of the circuit can be found in [/schematics](/schematics) which have been
created with [`gschem`][gschem].


## Installation

    # apt install wiringpi libnfc5 libnfc-bin libnfc-dev libnfc-examples i2c-tools build-essential

### Enable i2c interface

    # echo 'dtparam=i2c_arm=on' >> /boot/config.txt

### Verify that the i2c device is found

    # i2cdetect -y 1

A device address should be shown.

### Configure libnfc

    # echo 'device.connstring = "pn532_i2c:/dev/i2c-1"' > /etc/nfc/libnfc.conf

### Verify device is found by libnfc

    $ nfc-scan-device 
    nfc-scan-device uses libnfc 1.7.1
    1 NFC device(s) found:
    - pn532_i2c:/dev/i2c-1:
        pn532_i2c:/dev/i2c-1

### Install systemd service file

    # cp doord.service /etc/systemd/system

Change the password in environment variable set in the service file before starting service.

    # systemctl daemon-reload && systemctl enable doord.service && systemctl start doord.service

## Usage

Configurable environment variables and their defaults:

  - `GPIO_PIN_DOOR=0` GPIO pin to trigger door lock
  - `STAY_UNLOCKED_SEC=2` How long should the pin be kept high

Trigger the door lock

```
$ GPIO_PIN_DOOR=0 STAY_UNLOCKED_SEC=2 open-door
```

## Trigger lock over network

### SSH

Connect with SSH from the local network and use the password stored from hackerpass `infrastructure/hackeriet-door-trigger`.
The shell of the `entry` user is the `open-door` script. Connect with caution.

```
$ ssh entry@10.10.3.15
```

### Web interface

> **NOTE** Up to date information about this functionality can be found in https://github.com/hackeriet/door-remote

https://door-remote.hackeriet.no

## Debugging and Troubleshooting

### Verify daemon is running as it should

    # journalctl -u doord.service -f

## References

- [wiringPi wiring scheme][1]
- [The `gpio` utility][2]
- [Bash exit traps][3]
- [Power a 5V relay from GPIO pins](https://raspberrypi.stackexchange.com/questions/27928/power-a-5v-relay-from-gpio-pins#28201)
- [Logging in Systemd](https://www.loggly.com/blog/logging-in-new-style-daemons-with-systemd/)

[1]: https://pinout.xyz/pinout/wiringpi
[2]: https://projects.drogon.net/raspberry-pi/wiringpi/the-gpio-utility/
[3]: http://redsymbol.net/articles/bash-exit-traps/
[gschem]: https://wiki.archlinux.org/index.php/GEDA
