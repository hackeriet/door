# door

GPIO door lock control

- Tested on a Raspberry Pi 1 Model B using Raspbian 9.1
- The door lock is triggered by raising a single GPIO pin
- Pins are numbered using the [wiringPi scheme][1]

## Installing

> **IMPORTANT:** This has only been tested on a Raspberry Pi 3 Model B running Raspbian GNU/Linux 9

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

Connect with SSH from the local network and use the password stored from hackerpass `infrastructure/entry@humladoor-new.haus.hackeriet.no`.

```
$ ssh entry@10.10.3.15 open-door
```

Using a static IP as there seems to be some problems with hostname resolution at the moment. The hostname of this system will eventually change anyway.

### Web interface

> **NOTE** Up to date information about this functionality can be found in https://github.com/hackeriet/door-remote

https://door-remote.hackeriet.no

## References

- [wiringPi wiring scheme][1]
- [The `gpio` utility][2]
- [Bash exit traps][3]

[1]: https://pinout.xyz/pinout/wiringpi
[2]: https://projects.drogon.net/raspberry-pi/wiringpi/the-gpio-utility/
[3]: http://redsymbol.net/articles/bash-exit-traps/
