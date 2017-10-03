## Hardware preparations

This has been tested on a Raspberry Pi 1 Model B using latest Raspbian as of time of writing.

- The door lock is opened by raising a single GPIO pin
- Pins are numbered using the [wiringPi scheme][1]

## Installing

    # apt install wiringpi
    # curl -sSfo /usr/bin/open-door https://raw.githubusercontent.com/hackeriet/door/master/open-door

## Usage

Configurable environment variables and their defaults:

  - `GPIO_PIN_DOOR=0` GPIO pin to trigger lock
  - `STAY_UNLOCKED_SEC=2` How long should the pin be kept high

Open the door

```
$ GPIO_PIN_DOOR=0 STAY_UNLOCKED_SEC=2 open-door
```

## References

- [wiringPi wiring scheme][1]
- [The `gpio` utility][2]
- [Bash exit traps][3]

[1]: https://pinout.xyz/pinout/wiringpi
[2]: https://projects.drogon.net/raspberry-pi/wiringpi/the-gpio-utility/
[3]: http://redsymbol.net/articles/bash-exit-traps/
